# AUTO BEST FRAME — Seleccion de fotograma MiniMax H3 (ComfyUI)

**Repositorio propuesto:** `ComfyUI-AutoBestFrame-Selector` (no publicado en GitHub).

## Que hace

Un nodo nuevo `AUTO BEST FRAME | Nitidez + Rostro` recibe un lote `IMAGE` de ComfyUI y elige un solo fotograma mediante una heuristica reproducible de nitidez, contraste, exposicion y porcentaje de pixeles quemados. Si `cv2` esta instalado, usa el detector frontal de Haar para orientar la seleccion hacia rostros grandes y visibles. No requiere pesos adicionales ni genera nuevas fotos.

## Como instalar

1. Extraer la carpeta `ComfyUI-AutoBestFrame-Selector` en `ComfyUI/custom_nodes/`.
2. Reiniciar ComfyUI.
3. Arrastrar el archivo `PIKA_FLEX_AVATAR_AUTO_BEST_FRAME.json` sobre el lienzo de ComfyUI.
4. Mantener los modelos y extensiones del workflow original.
5. Ejecutar el flujo normal. El mejor frame llegara al cache cuerpo, y de ahi al Character Sheet y al video.

## Conexion revisada (sin cambiar otra etapa)

VAEDecode (316) -> AUTO BEST FRAME (314) -> RefModV2BodyCache (317) -> H3CharacterSheetDesignerReferenceV13 (333).

## Controles

- face_detection: intenta detectar rostro con OpenCV si esta disponible.
- face_bonus: bonus por rostro frontal visible, predeterminado 12.
- skip_first_frames / skip_last_frames: omite transiciones borrosas de inicio y cierre.
- sample_every: 1 evalua todos, 2 cada segundo, etc.

## Limitaciones

La nitidez es una heuristica; un fotograma nitido puede tener errores anatómicos o identidad incorrecta. El detector Haar no detecta siempre perfiles o rostros pequenos. Se recomienda revisar la vista previa final y su identidad antes de utilizarla.

El flujo fue modificado y validado estructuralmente, pero NO se ha ejecutado en la GPU del usuario.
