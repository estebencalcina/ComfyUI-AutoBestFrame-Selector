# MiniMax Pika Flex — AUTO BEST FRAME + CACHÉS SEPARADOS

**Repositorio para GitHub (ya propuesto):** `ComfyUI-AutoBestFrame-Selector`. No se ha publicado.

## Reparación específica

- Nodo 317 = `RefModV2FaceCache`: foto inicial, archivo `output/refmod_cache_v2/ultima_foto_rostro.png`.
- Nodo 349 = `RefModV2BodyCache`: Character Sheet, archivo `output/refmod_cache_v2/ultima_foto_cuerpo.png`.
- Cada uno tiene su propio BOOLEAN TRUE/FALSE; NO son el mismo archivo.
- La selección automática del mejor fotograma (nodo 314) se conserva.
- Se mantienen todas las demás conexiones del JSON original.

## Instalación

1. Si ya instalaste `ComfyUI-AutoBestFrame-Selector`, **NO reinstales otro nodo**: solo carga el JSON corregido.
2. Asegura que esté instalado el nodo que compartiste `ComfyUI-RefMod-Persistent-Cache-V2`, que registra **ambas** clases `RefModV2FaceCache` y `RefModV2BodyCache`.
3. Abre `PIKA_FLEX_AVATAR_AUTO_BEST_FRAME_CACHE_SEPARADO.json`.
4. Para generar: ambos FALSE. Para reutilizar solo foto inicial: foto TRUE, hoja FALSE. Para reutilizar la hoja directamente en el video: hoja TRUE.

**Atención:** los PNG antiguos guardados erróneamente bajo `ultima_foto_cuerpo.png` pueden contener la foto inicial o la hoja de personaje según cuál se ejecutó al final. Antes de usar TRUE por primera vez, haz una ejecución con FALSE en ambos para crear cada archivo correctamente. Si `ultima_foto_rostro.png` no existe aún, hay que generar una vez con FALSE.

Comprobaciones hechas: JSON válido, tipos de nodos corregidos, enlaces conservados, Python del selector compilado. No probado en ComfyUI real.
