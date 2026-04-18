# Visión por Computadora con MediaPipe Hands

## Nombre del estudiante

- Esteban Barrera
- Nicolas Quezada Mora
- Cristian Motta
- Esteban Santacruz
- Jeronimo Bermudez
- Sebastian Andrade

## Fecha de entrega

2026-04-11

---

## Descripción breve

En este taller se implementó un sistema de visión por computadora en Python que permite interactuar con la pantalla en tiempo real mediante gestos de manos, sin ningún hardware adicional. La captura de video se realiza a través de una webcam, y la detección de manos se delega a MediaPipe Hands, una biblioteca de Google que entrega 21 puntos de referencia (landmarks) por mano con coordenadas normalizadas en cada frame.

A partir de esos landmarks se calculan dos métricas principales: el número de dedos extendidos y la distancia euclidiana entre la punta del pulgar y la del índice. Con base en esas métricas, la aplicación organiza tres escenas intercambiables que responden de forma diferente a los gestos detectados.

---

## Implementación en Python

### Estructura general

El script está organizado en funciones independientes por responsabilidad. El flujo principal consiste en capturar un frame de la cámara con OpenCV, convertirlo a RGB y pasarlo al detector de MediaPipe, obtener los landmarks, calcular las métricas y despachar el frame a la escena activa según el estado global de la aplicación.

El estado se centraliza en un diccionario que almacena la escena activa, la posición del objeto, el canvas de pintura y un contador de frames para el cooldown entre cambios de escena. Esto evita variables globales dispersas y facilita el razonamiento sobre el ciclo de vida de la aplicación.

### Detección de manos

MediaPipe entrega los landmarks como coordenadas normalizadas entre 0 y 1 respecto al tamaño del frame. Para contar dedos extendidos se compara la coordenada Y de la punta de cada dedo (landmarks 8, 12, 16, 20) contra la de su articulación PIP (6, 10, 14, 18): si la punta está más arriba en pantalla (Y menor), el dedo está extendido. El pulgar es el caso especial, ya que se extiende lateralmente y su detección depende de la coordenada X y de si es la mano izquierda o derecha.

### Escena 1 — Métricas y fondo reactivo

La primera escena es la más informativa: muestra en tiempo real el número de dedos extendidos, la distancia entre pulgar e índice, y la lateralidad de la mano. El fondo cambia de color en función del número de dedos, usando `addWeighted` de OpenCV para fusionar un overlay de color sólido con el frame de cámara, lo que produce una transición visual inmediata sin perder la imagen del usuario.

![escena_1](./media/escena_1.gif)

### Escena 2 — Pintura con el dedo índice

La segunda escena mantiene un canvas paralelo al frame de cámara, inicializado como una matriz de ceros (negro puro). Cuando el usuario extiende solo el dedo índice, se pinta un círculo en la posición de ese landmark. El canvas se fusiona con el frame usando una máscara binaria: los píxeles donde el canvas tiene contenido reemplazan directamente al frame. Un puño cerrado reinicia el canvas a cero, borrando todo lo dibujado.

![escena_2](./media/escena_2.gif)

### Escena 3 — Objeto móvil controlado por la mano

En la tercera escena aparece un objeto geométrico que sigue la posición de la muñeca del usuario. Su posición no se actualiza de forma abrupta sino mediante interpolación lineal (lerp) entre la posición anterior y la nueva, con un factor de 0.2, lo que produce un movimiento suave y con inercia. El radio del objeto varía proporcionalmente a la distancia entre pulgar e índice, y su forma cambia entre círculo y rectángulo según el número de dedos extendidos.

![escena_3](./media/escena_3.gif)

### Navegación entre escenas

El gesto de palma abierta (cinco dedos extendidos) activa el cambio de escena, ciclando entre las tres disponibles. Para evitar cambios involuntarios por frames consecutivos con la palma abierta, se implementó un cooldown basado en el número de frame: el cambio solo se permite si han transcurrido al menos 40 frames desde el último.

---

## Código relevante

### Conteo de dedos extendidos

La función compara la punta de cada dedo con su articulación media. El pulgar requiere lógica diferenciada por eje X según la lateralidad de la mano:

```python
def contar_dedos(landmarks, handedness: str) -> int:
    tips = [4, 8, 12, 16, 20]
    pip  = [3, 6, 10, 14, 18]
    dedos_abiertos = 0

    if handedness == "Right":
        if landmarks[tips[0]].x < landmarks[pip[0]].x:
            dedos_abiertos += 1
    else:
        if landmarks[tips[0]].x > landmarks[pip[0]].x:
            dedos_abiertos += 1

    for i in range(1, 5):
        if landmarks[tips[i]].y < landmarks[pip[i]].y:
            dedos_abiertos += 1

    return dedos_abiertos
```

### Distancia entre pulgar e índice

Calcula la distancia euclidiana en píxeles entre los landmarks 4 y 8, convirtiendo previamente las coordenadas normalizadas al espacio de imagen:

```python
def distancia_indice_pulgar(landmarks, w, h) -> float:
    x1 = int(landmarks[4].x * w); y1 = int(landmarks[4].y * h)
    x2 = int(landmarks[8].x * w); y2 = int(landmarks[8].y * h)
    return math.hypot(x2 - x1, y2 - y1)
```

### Escena de pintura — fusión de canvas con frame

El canvas persiste entre frames y se integra al video usando una máscara binaria, lo que permite superponer el dibujo sin ocultar al usuario:

```python
if n_dedos == 0:
    estado["canvas"] = np.zeros((h, w, 3), dtype=np.uint8)
elif n_dedos == 1:
    cv2.circle(canvas, p8, 10, color_pincel, -1)

mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
frame[mask > 0] = canvas[mask > 0]
```

### Objeto móvil con interpolación

La posición del objeto se actualiza frame a frame mediante lerp, con el tamaño determinado por la apertura de la mano:

```python
ox, oy = estado["objeto_pos"]
estado["objeto_pos"][0] = int(ox * 0.8 + cx * 0.2)
estado["objeto_pos"][1] = int(oy * 0.8 + cy * 0.2)

radio = int(np.clip(dist * 0.4, 20, 120))

if n_dedos <= 2:
    cv2.circle(frame, (ox, oy), radio, color_obj, -1)
else:
    cv2.rectangle(frame, (ox-radio, oy-radio), (ox+radio, oy+radio), color_obj, -1)
```

---

## Aprendizajes y dificultades

### Aprendizajes

Se pudo comprender cómo MediaPipe abstrae por completo la complejidad del modelo de detección: el desarrollador recibe directamente los 21 landmarks en coordenadas normalizadas y puede construir toda la lógica de gestos sobre esa interfaz sin necesidad de manejar redes neuronales ni preprocesamiento de imagen. También se entendió la diferencia entre operar sobre el frame directamente y mantener un canvas separado que se fusiona en cada iteración, lo cual es fundamental para efectos persistentes como el de la escena de pintura.

El uso de interpolación lineal para suavizar el movimiento del objeto fue otro aprendizaje concreto: sin el lerp, el objeto trepida con cada pequeña variación del landmark; con él, el movimiento se percibe natural e intencional.

### Dificultades

Una dificultad fue la detección del pulgar: al estar en modo espejo (el frame se voltea horizontalmente), la lateralidad reportada por MediaPipe es la contraria a la visual, lo cual afecta la comparación por eje X. El ajuste fue invertir la condición según el valor de `handedness`.

### Mejoras futuras

Podría extenderse el sistema para reconocer gestos compuestos, como el gesto de pinza sostenida durante un número de frames, en lugar de depender solo de conteos de dedos en un único frame. También sería interesante añadir soporte para dos manos simultáneas, lo que abriría interacciones más ricas como escalar un objeto usando ambas manos.

---

## Estructura del proyecto

```
semana_07_gestos_webcam_mediapipe/
├── python/
│   └── main.py                 # Script principal
├── media/                      # Capturas de cada escena
│   ├── escena_1.png
│   ├── escena_2.png
│   └── escena_3.png
└── README.md
```