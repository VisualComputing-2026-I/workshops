# Proyecto Python - Matching, Homografia y Panorama

Este proyecto implementa el taller de coincidencia de caracteristicas con OpenCV y NumPy.

## Instalacion

```bash
pip install -r requirements.txt
```

## Uso

Agrega tus imagenes manualmente y ejecuta:

```bash
python main.py --match-a data/matching_1.jpg --match-b data/matching_2.jpg --object-template data/template.jpg --object-scene data/scene.jpg --panorama-dir data/panorama --output-dir outputs
```

El script acepta SIFT por defecto. Tambien puedes usar ORB:

```bash
python main.py --detector orb --match-a data/matching_1.jpg --match-b data/matching_2.jpg --output-dir outputs_orb
```

## Que genera

- Comparacion de matches con BFMatcher y FLANN.
- Visualizacion de matches e inliers.
- Calculo de homografia con RANSAC.
- Deteccion del objeto con bounding box.
- Panorama con `warpPerspective` y blending suave.
- Archivo `metrics.json` con tiempos, cantidad de matches e inliers.

Los resultados se guardan en la carpeta indicada con `--output-dir`.
