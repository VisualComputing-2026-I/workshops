# Implementación de Z-Buffer y Depth Testing

## Nombre del estudiante

<!-- TODO: Completar -->

## Fecha de entrega

<!-- TODO: Completar -->

---

## Descripción breve

Este taller implementa el algoritmo de Z-buffer (depth buffer) desde cero para comprender su funcionamiento dentro del pipeline de renderizado 3D. Se compara el renderizado con y sin Z-buffer, se visualiza el depth buffer, se analizan problemas de precisión y se simula Z-fighting. Se desarrolla en tres entornos: Python (implementación desde cero), Three.js y Unity (configuración y análisis).

---

## Implementaciones

### Python

Notebook que implementa el Z-buffer desde cero usando NumPy y Matplotlib. Incluye: proyección perspectiva 3D→2D, rasterización de triángulos con coordenadas baricéntricas, renderizado con Painter's Algorithm (sin Z-buffer) y con Z-buffer, visualización del depth buffer como imagen en escala de grises, comparación lado a lado de ambos métodos, experimentación con ratios near/far y simulación de Z-fighting con triángulos casi coplanares que se cruzan.

### Three.js / React Three Fiber

<!-- TODO: Completar implementación Three.js -->

### Unity

<!-- TODO: Completar implementación Unity -->

---

## Resultados visuales

### Python - Implementación

![Painter's Algorithm](./media/painters_algorithm.png)

Renderizado con Painter's Algorithm: los triángulos se pintan de atrás hacia adelante sin prueba de profundidad.

![Artefactos de intersección](./media/painters_artifacts_intersection.png)

Artefactos del Painter's Algorithm con triángulos intersectados donde no existe un orden válido de atrás hacia adelante.

![Z-buffer oclusión correcta](./media/zbuffer_correct_occlusion.png)

Renderizado con Z-buffer: la oclusión se resuelve correctamente a nivel de píxel, sin importar el orden de renderizado.

![Comparación con/sin Z-buffer](./media/comparison_with_without_zbuffer.png)

Comparación lado a lado: Painter's Algorithm vs Z-buffer, con mapa de diferencias que resalta los píxeles incorrectos.

![Depth buffer](./media/depth_buffer_basic_scene.png)

Visualización del depth buffer como imagen en escala de grises (oscuro = cerca, claro = lejos).

![Precisión near/far](./media/precision_near_far_planes.png)

Efecto del ratio near/far en la precisión del depth buffer: ratios extremos degradan la resolución de profundidad.

![Z-fighting](./media/zfighting_near_coplanar.png)

Simulación de Z-fighting con triángulos casi coplanares que se cruzan, variando el ángulo de inclinación.

### Three.js - Implementación

<!-- TODO: Agregar resultados Three.js -->

### Unity - Implementación

<!-- TODO: Agregar resultados Unity -->

---

## Código relevante

<!-- TODO: Completar implementación Three.js -->

### Ejemplo de código Python - Rasterización con Z-buffer:

```python
def rasterize_triangle(screen_coords, depths, color, color_buffer, z_buffer=None, use_zbuffer=True):
    h, w = color_buffer.shape[:2]
    v0, v1, v2 = screen_coords
    d0, d1, d2 = depths

    # Bounding box (clamped to image)
    min_x = max(0, int(np.floor(min(v0[0], v1[0], v2[0]))))
    max_x = min(w - 1, int(np.ceil(max(v0[0], v1[0], v2[0]))))
    min_y = max(0, int(np.floor(min(v0[1], v1[1], v2[1]))))
    max_y = min(h - 1, int(np.ceil(max(v0[1], v1[1], v2[1]))))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            u, v, w_bary = barycentric(x + 0.5, y + 0.5, v0, v1, v2)

            if u >= 0 and v >= 0 and w_bary >= 0:
                # Interpolate depth using barycentric coordinates
                z = u * d0 + v * d1 + w_bary * d2

                if use_zbuffer:
                    if z < z_buffer[y, x]:  # Closer to camera?
                        z_buffer[y, x] = z
                        color_buffer[y, x] = color
                else:
                    color_buffer[y, x] = color  # Simply overwrite
```

### Ejemplo de código Python - Proyección perspectiva:

```python
def project_vertices(vertices, width=512, height=512, fov=60.0, near=0.1, far=100.0):
    aspect = width / height
    fov_rad = np.radians(fov)
    f = 1.0 / np.tan(fov_rad / 2.0)

    for i, v in enumerate(vertices):
        x, y, z = v
        depth = -z  # Camera looks down -Z

        # Perspective divide
        xp = (f / aspect) * x / depth
        yp = f * y / depth

        # NDC [-1, 1] to screen [0, width/height]
        sx = (xp + 1.0) * 0.5 * width
        sy = (1.0 - yp) * 0.5 * height  # Flip Y for screen space
```

### Ejemplo de código Python - Simulación de Z-fighting:

```python
def create_zfighting_scene(base_depth, tilt):
    return [
        {   # Flat triangle at constant depth
            "vertices": np.array([
                [-1.5, -1.0, base_depth],
                [ 1.5, -1.0, base_depth],
                [ 0.0,  1.5, base_depth],
            ]),
            "color": np.array([1.0, 0.2, 0.2]),
        },
        {   # Tilted triangle: crosses through the first one
            "vertices": np.array([
                [-1.5, -1.0, base_depth + tilt],   # Behind
                [ 1.5, -1.0, base_depth - tilt],   # In front
                [ 0.0,  1.5, base_depth],           # Same depth at top
            ]),
            "color": np.array([0.2, 0.8, 0.2]),
        },
    ]
```

---

## Prompts utilizados

<!-- TODO: Completar implementación Three.js -->

Se utilizó GitHub Copilot para:
1. Estructurar el pipeline de renderizado (proyección, rasterización, Z-buffer)
2. Implementar las coordenadas baricéntricas para la interpolación de profundidad
3. Diseñar las visualizaciones comparativas y los experimentos de precisión

---

## Aprendizajes y dificultades

<!-- TODO: Completar implementación Three.js -->

### Aprendizajes

Se comprendió que el Z-buffer resuelve la oclusión a nivel de píxel, superando las limitaciones del Painter's Algorithm que falla con triángulos intersectados o solapamiento cíclico. La distribución no lineal de los valores de profundidad en NDC concentra la mayor precisión cerca del near plane, lo que explica por qué ratios near/far extremos causan problemas. El Z-fighting ocurre cuando la diferencia de profundidad entre dos superficies es menor que la resolución del depth buffer a esa distancia.

### Dificultades

La implementación de la rasterización por coordenadas baricéntricas requirió cuidado con los casos degenerados (triángulos con área cero). Visualizar correctamente el depth buffer necesitó manejar los valores infinitos del fondo y normalizar solo los píxeles válidos. La detección automática de Z-fighting fue desafiante porque con triángulos que se cruzan, ambos colores están presentes legítimamente.

### Mejoras futuras

Optimizar la rasterización usando vectorización con NumPy en lugar de bucles píxel por píxel. Implementar perspective-correct interpolation para la profundidad. Agregar soporte para mallas 3D completas (OBJ) en lugar de triángulos individuales.

---

## Contribuciones grupales (si aplica)

<!-- TODO: Documentar contribuciones del equipo -->

---

## Estructura del proyecto

<!-- TODO: Completar -->

```
semana_03_2_zbuffer_depth_testing/
├── python/
│   └── notebook.ipynb         # Implementación Z-buffer desde cero
├── threejs/                   # TODO: Implementación Three.js
├── unity/                     # TODO: Implementación Unity
├── media/                     # Imágenes y GIFs de resultados
└── README.md                  # Este archivo
```

---

## Referencias

<!-- TODO: Completar -->

- **NumPy**: https://numpy.org/ - Operaciones matriciales
- **Matplotlib**: https://matplotlib.org/ - Visualización y generación de frames
- **GeeksForGeeks**: https://www.geeksforgeeks.org/computer-graphics/z-buffer-depth-buffer-method/ - 
Z-Buffer or Depth-Buffer method


---
