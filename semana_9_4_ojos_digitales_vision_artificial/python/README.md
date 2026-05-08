# Procesamiento de imagenes con OpenCV

Implementacion local en Python para cargar una imagen a color, convertirla a escala de grises, aplicar filtros convolucionales simples y comparar detectores de bordes.

## Requisitos

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Uso rapido

Ejecuta el programa principal:

```powershell
python image_filters_edges.py
```

El programa abre un menu en consola desde donde puedes elegir:

- Comparacion visual de filtros y bordes.
- Sliders interactivos con una imagen.
- Webcam en tiempo real con sliders.
- Imagen demo generada por el programa o imagen propia desde una ruta.
- Visualizacion con Matplotlib o ventanas de OpenCV.

## Uso opcional con argumentos

Los argumentos siguen disponibles si quieres ejecutar una opcion directamente.

Ejecutar con una imagen propia:

```powershell
python image_filters_edges.py --image ruta\a\imagen.jpg
```

Mostrar resultados con ventanas de OpenCV en vez de Matplotlib:

```powershell
python image_filters_edges.py --image ruta\a\imagen.jpg --display cv2
```

## Sliders interactivos

Permite cambiar en vivo el tipo de filtro y el tamano del kernel.

Desde el menu principal:

```powershell
python image_filters_edges.py
```

Luego selecciona `2. Sliders interactivos con una imagen`.

O directamente con argumentos:

```powershell
python image_filters_edges.py --image ruta\a\imagen.jpg --interactive
```

Controles:

- `Filtro`: 0 gris, 1 blur, 2 sharpening, 3 Sobel, 4 Laplaciano.
- `Kernel`: tamano impar usado por blur, Sobel y Laplaciano.
- Teclas `q` o `Esc`: cerrar.

## Webcam opcional

Procesa frames en tiempo real desde la webcam:

Desde el menu principal:

```powershell
python image_filters_edges.py
```

Luego selecciona `3. Webcam en tiempo real con sliders`.

O directamente con argumentos:

```powershell
python image_filters_edges.py --webcam
```

Tambien acepta indice de camara:

```powershell
python image_filters_edges.py --webcam --camera-index 1
```

## Que implementa

- Carga de imagen a color.
- Conversion a escala de grises.
- Filtro blur convolucional con kernel promedio.
- Filtro sharpening convolucional.
- Deteccion de bordes con Sobel X y Sobel Y.
- Deteccion de bordes con Laplaciano.
- Comparacion visual entre metodos.
- Visualizacion con `matplotlib.pyplot.imshow()` o `cv2.imshow()`.
- Sliders con `cv2.createTrackbar`.
- Procesamiento opcional en tiempo real con webcam.
