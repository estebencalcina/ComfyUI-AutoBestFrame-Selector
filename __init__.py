"""Automatic frame selection for an IMAGE batch in ComfyUI.

Uses deterministic no-training-reference quality measurements, with optional OpenCV
Haar face detection. No model downloads and no changes to installed nodes.
"""
import math
import torch
import torch.nn.functional as F


def _metrics(x, face_detection, face_weight):
    """x is CPU RGB tensor [H,W,3], float 0..1; compute quality score."""
    # Fast, bounded resolution makes metrics comparable across frames.
    y = x.permute(2, 0, 1).unsqueeze(0).float()
    y = F.interpolate(y, size=(384, 384), mode='bilinear', align_corners=False)[0]
    g = (0.2126 * y[0] + 0.7152 * y[1] + 0.0722 * y[2]).clamp(0, 1)
    selected = g
    face_found = False
    face_fraction = 0.0
    if face_detection:
        try:
            import cv2
            import numpy as np
            detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if not detector.empty():
                gray = (g.numpy() * 255).astype('uint8')
                faces = detector.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=4, minSize=(34,34))
                if len(faces) > 0:
                    # Favor the largest detected face.
                    xx, yy, ww, hh = sorted(faces, key=lambda z: z[2]*z[3], reverse=True)[0]
                    m = int(0.12 * max(ww, hh))
                    x0=max(0,xx-m);x1=min(384,xx+ww+m)
                    y0=max(0,yy-m);y1=min(384,yy+hh+m)
                    selected = g[y0:y1, x0:x1]
                    face_found = True
                    face_fraction = (ww * hh)/(384 * 384)
        except (ImportError, RuntimeError, AttributeError):
            pass
    if not face_found:
        # Middle of image tends to carry subject for studio full-body shots;
        # small enough to avoid a detailed background dominating the score.
        selected = g[64:320, 64:320]
    # Laplacian variance indicates high frequency, not necessarily *true* detail.
    local = selected.unsqueeze(0).unsqueeze(0)
    lap_kernel = torch.tensor([[0.,1.,0.],[1.,-4.,1.],[0.,1.,0.]],dtype=torch.float32).view(1,1,3,3)
    lap = F.conv2d(local,lap_kernel,padding=1)[0,0]
    lapvar = float(lap.var(unbiased=False))
    dx = selected[:,1:]-selected[:,:-1]
    dy = selected[1:,:]-selected[:-1,:]
    grad = 0.5 * float(dx.abs().mean() + dy.abs().mean())
    contrast = float(selected.std(unbiased=False))
    lum = float(g.mean())
    clipped = float(((g < 0.025) | (g > 0.975)).float().mean())
    # Log-saturated sharpness and gradient, moderate contrast, exposure.
    sharp = min(1.0, math.log1p(lapvar*2500)/math.log1p(10))
    texture = min(1.0, math.log1p(grad*100)/math.log1p(6))
    detail = 0.70*sharp+0.30*texture
    contrast_q = min(1.0,contrast/0.22)
    exposure_q = max(0.0, 1.0-abs(lum-0.50)/0.50)
    clip_q = max(0.0, 1.0-min(1.0,clipped/0.35))
    score = 100*(0.60*detail+0.16*contrast_q+0.13*exposure_q+0.11*clip_q)
    if face_detection and face_found:
        score += float(face_weight)*min(1.0,face_fraction/0.025)
    # In no-face-detected cases, no penalty: side views are allowed.
    return score,face_found,detail,contrast_q,exposure_q,clip_q


class AutoBestFrameSelector:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'images': ('IMAGE',),
            'face_detection': ('BOOLEAN', {'default': True}),
            'face_bonus': ('FLOAT', {'default': 12.0, 'min': 0.0, 'max': 40.0, 'step': 1.0}),
            'skip_first_frames': ('INT', {'default': 0, 'min': 0, 'max': 100, 'step': 1}),
            'skip_last_frames': ('INT', {'default': 0, 'min': 0, 'max': 100, 'step': 1}),
            'sample_every': ('INT', {'default': 1, 'min': 1, 'max': 20, 'step': 1}),
        }}
    RETURN_TYPES = ('IMAGE', 'INT', 'STRING')
    RETURN_NAMES = ('best_frame', 'frame_index_0_based', 'quality_report')
    FUNCTION = 'select'
    CATEGORY = 'Image/Quality'
    DESCRIPTION = 'Scores all eligible frames by sharpness, contrast and exposure; optionally prefers a clearly detected face. Returns one frame.'

    def select(self,images,face_detection=True,face_bonus=12.0,skip_first_frames=0,skip_last_frames=0,sample_every=1):
        if images.ndim != 4 or images.shape[-1] < 3:
            raise ValueError('AutoBestFrame: se espera IMAGE [N,H,W,C]')
        n=int(images.shape[0]);start=min(max(0,int(skip_first_frames)),n-1)
        stop=max(start+1,n-max(0,int(skip_last_frames)))
        indices=list(range(start,stop,max(1,int(sample_every))))
        if not indices: indices=[min(start,n-1)]
        results=[]
        with torch.no_grad():
            for i in indices:
                rgb=images[i,...,:3].detach().cpu().clamp(0,1)
                score,face,detail,contrast,exposure,clipping=_metrics(rgb,face_detection,face_bonus)
                results.append((score,i,face,detail,contrast,exposure,clipping))
        results.sort(key=lambda a:(-a[0],a[1]))
        best=results[0]
        report=(f'Fotograma seleccionado: {best[1]} (indice desde 0; fotograma humano {best[1]+1}) | '
                f'Puntuacion {best[0]:.2f}/~112. Evaluados {len(indices)} de {n}.\n'
                + '\n'.join(f'{i:03d}: score={s:.2f} rostro={"si" if face else "no"} '
                            f'nitidez={d:.2f} contraste={c:.2f} exposicion={e:.2f} recorte={cl:.2f}'
                            for s,i,face,d,c,e,cl in results[:12]))
        print('[AutoBestFrame] '+report.replace('\n',' | '))
        return (images[best[1]:best[1]+1], best[1], report)

NODE_CLASS_MAPPINGS = {'AutoBestFrameSelector': AutoBestFrameSelector}
NODE_DISPLAY_NAME_MAPPINGS = {'AutoBestFrameSelector': 'AUTO BEST FRAME | Nitidez + Rostro'}
