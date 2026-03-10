#  Rasterización desde Cero: Dibujando con Algoritmos Clásicos

## Nombre del estudiante

<!-- TODO: Completar -->

## Fecha de entrega

<!-- TODO: Completar -->

---

## Descripción breve

En este taller se implementan tecnicas básicas de rasterización como el algoritmo de Brasenham, el de punto medio y la rasterización por scanline, para de esta manera comprender como se pueden dibujar aproximaciones de objetos geometricos en una cuadricula de pixeles.

---

## Implementaciones

### Algoritmo de Brasenham

El primer algoritmo a implementar es el de Brasenham, el cual nos permite dibujar rectas con pixeles de forma aproximada, es un algoritmo que toma la desición de hacer un incremento (o decremento, dependiendo de la pendiente) en  `x` y también em `y`, basandose en minimizar una aproximación del error, y usando únicamente valores discretos.

```
def bresenham(x0, y0, x1, y1):
 dx = abs(x1 - x0)
 dy = abs(y1 - y0)
 sx = 1 if x0 < x1 else -1
 sy = 1 if y0 < y1 else -1
 err = dx - dy

 while True:
  pixels[x0, y0] = (255, 0, 0)
  if x0 == x1 and y0 == y1:
    break
  e2 = 2 * err
  if e2 > -dy:
    err -= dy
    x0 += sx
  if e2 < dx:
    err += dx
    y0 += sy
```

### Punto Medio

Este algoritmo permite dibujar un circulo de radio $r$ empezando desde el punto $(r,0)$, y incrementando $y$ en una unidad por cada iteración, y decidiendo si disminuir o no $x$ en base a si el punto anterior está o no dentro del circulo, esto lo hace debido al hecho de que $0=x^2 + y^3 - r^2$, entonces si el punto está dentro, entonces esto sería menor que 0, de lo contrario, mayor.

```
def midpoint_circle(x0, y0, radius):
    x = radius
    y = 0
    p = 1 - radius

    while x >= y:

        for dx, dy in [
            (x, y), (y, x),
            (-x, y), (-y, x),
            (-x, -y), (-y, -x),
            (x, -y), (y, -x)
        ]:
            if 0 <= x0 + dx < width and 0 <= y0 + dy < height:
                pixels[x0 + dx, y0 + dy] = (0, 0, 255)

        y += 1

        if p <= 0:
            p = p + 2*y + 1
        else:
            x -= 1
            p = p + 2*y - 2*x + 1
```

### Scanline simple

Esta implementacion consiste en rellenar cada linea horizontal del triángulo. Para esto recorremos su altura dessde el punto más alto en $y$ hasta el más bajo, pero es necesario calcular los límites izquierdo ($xl$) y derecho ($xr$), los cuales se calculan despejando la ecuación de la recta de $x$ en función de $y$.

```
def fill_triangle(p1, p2, p3):
    # ordenar por y
    pts = sorted([p1, p2, p3], key=lambda p: p[1])
    (x1, y1), (x2, y2), (x3, y3) = pts

    def interpolate(y0, y1, x0, x1):
        if y1 - y0 == 0:
            return []
        return [
            int(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            for y in range(y0, y1)
        ]

    x12 = interpolate(y1, y2, x1, x2)
    x23 = interpolate(y2, y3, x2, x3)
    x13 = interpolate(y1, y3, x1, x3)

    x_right = x12 + x23

    for y, xl, xr in zip(range(y1, y3), x13, x_right):
        for x in range(min(xl, xr), max(xl, xr)):
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = (0, 255, 0)


fill_triangle((30, 50), (100, 150), (160, 60))

plt.imshow(image)
plt.axis('off')
plt.show()
```

## Resultados visuales

### Algoritmo de Brasenham

![Painter's Algorithm](./media/line.png)

### Punto Medio

![Painter's Algorithm](./media/circle.png)

### Scaline simple

![Painter's Algorithm](./media/triangle.png)

<!-- TODO: Agregar resultados Unity -->

---

## Prompts utilizados

<!-- TODO: Completar implementación Three.js -->
---

## Aprendizajes y dificultades

<!-- TODO: Completar implementación Three.js -->

### Aprendizajes

A lo largo del trabajo fueron comprendidos los fundamentos de algoritmos clásicos de rasterización como Bresenham, el punto medio para circunferencias y el rellenado por scanline. Fue entendida la importancia de la función implícita del círculo y cómo una variable de decisión puede ser actualizada de forma incremental sin recalcular toda la ecuación. También fue aclarado el papel de la interpolación lineal para calcular intersecciones horizontales en el rellenado de triángulos

### Dificultades

Fueron presentadas confusiones en la derivación matemática del algoritmo del punto medio, especialmente en la simplificación de expresiones y en la obtención del valor inicial de la variable de decisión. Fue cuestionado el efecto de ciertas cancelaciones algebraicas y el impacto del signo en las comparaciones. Además, fueron detectados problemas prácticos como errores de identación, visualización en Colab y la inversión del eje vertical al interpretar la imagen como matriz.

### Mejoras futuras

Podría ser realizada una derivación más estructurada paso a paso antes de implementar el código, para evitar saltos algebraicos que generen dudas. Sería recomendable validar cada parte del algoritmo con ejemplos numéricos pequeños antes de generalizarlo. También podría ser mejorada la claridad del código mediante comentarios más precisos que expliquen la lógica matemática detrás de cada decisión incremental.

---

## Contribuciones grupales (si aplica)

<!-- TODO: Documentar contribuciones del equipo -->

---

## Estructura del proyecto

<!-- TODO: Completar -->

```
semana_03_2_zbuffer_depth_testing/
├── python/
│   └── notebook.ipynb         # Implementación de los tres algoritmos mencionados
├── media/                     # Imágenes y GIFs de resultados
└── README.md                  # Este archivo
```

---

---
