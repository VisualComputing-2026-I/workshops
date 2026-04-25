# Taller Local Voice Recognition Commands

## Nombre de los estudiantes
- Juan Esteban Santacruz Corredor
- Nicolas Quezada Mora
- Cristian Steven Motta Ojeda
- Sebastian Andrade Cedano
- Esteban Barrera Sanabria
- Jerónimo Bermúdez Hernández

## Fecha de entrega

`2026-04-24`

---

## Descripción breve

Este taller implementa un flujo local (offline) de reconocimiento de voz en Python y lo conecta a un visualizador en Processing en tiempo real mediante OSC. El sistema reconoce comandos hablados en español, los transforma en acciones visuales (color, forma, animación, velocidad y reinicio) y actualiza la escena remota de forma inmediata.

El proyecto se centró en mantener baja latencia, mejorar la robustez ante ruido de voz y usar una interacción push-to-talk simple para controlar la salida visual con instrucciones cortas.

---

## Implementaciones

### Python

- Reconocimiento de voz offline con `pocketsphinx` usando gramática cerrada de comandos en español.
- Bucle push-to-talk con captura de micrófono por `sounddevice`.
- Normalización de texto (eliminación de acentos y limpieza de tokens) y matching difuso para tolerar pequeñas variaciones.
- Parseo de comandos a mensajes OSC:
  - `/color`
  - `/shape`
  - `/anim`
  - `/spin`
  - `/speed`
  - `/reset`
- Envío OSC a `127.0.0.1:12000`.

### Processing

- Receptor OSC con `oscP5`.
- Respuesta visual en tiempo real a comandos entrantes (forma, color, estado de animación, estado de giro, velocidad y reset).
- HUD con estado actual y última frase reconocida.
- Ventana redimensionable para facilitar pruebas y demostración.

---

## Resultados visuales

### Python - Implementación

![Python voice control loop](./media/python_1.gif)

Python ejecutándose en modo push-to-talk, capturando audio local y enviando comandos parseados por OSC.

### Processing - Implementación

![Processing OSC visualizer](./media/processing_1.gif)

Visualizador en Processing reaccionando en tiempo real a los comandos de voz enviados desde Python.

---

## Código relevante

### Python — parseo de comandos

```python
def parse_commands(text: str) -> List[ParsedCommand]:
    words = canonical_tokens(text)
    commands: List[ParsedCommand] = []
    canonical_action_tokens = {"start", "stop", "spin", "faster", "slower", "reset", "exit"}
    actions = [ACTION_ALIASES[word] if word in ACTION_ALIASES else word for word in words if word in ACTION_ALIASES or word in canonical_action_tokens]

    for word in words:
        if word in COLOR_ALIASES:
            commands.append(ParsedCommand("/color", COLOR_ALIASES[word]))
            break

    for word in words:
        if word in SHAPE_ALIASES:
            commands.append(ParsedCommand("/shape", SHAPE_ALIASES[word]))
            break
```

### Processing — manejo de eventos OSC

```java
void oscEvent(OscMessage message) {
  String address = message.addrPattern();
  String value = normalize(extractArg(message));

  if (address.equals("/color")) {
    applyColor(value);
    return;
  }

  if (address.equals("/shape")) {
    applyShape(value);
    return;
  }
}
```

### Archivos principales

- Reconocedor y emisor OSC en Python: [python/voice_to_osc.py](python/voice_to_osc.py)
- Dependencias de Python: [python/requirements.txt](python/requirements.txt)
- Receptor visual en Processing: [processing/processing.pde](processing/processing.pde)

---

## Prompts utilizados

1. "Build an offline Spanish voice command recognizer in Python using PocketSphinx and send actions over OSC."
2. "Improve recognition stability with constrained grammar and robust token normalization."
3. "Create a Processing OSC visualizer that reacts to color, shape, animation, and speed commands."
4. "Reduce terminal output to clean, essential logs while keeping useful feedback."

---

## Aprendizajes y dificultades

### Aprendizajes

- Cómo una gramática cerrada mejora notablemente la confiabilidad del reconocimiento en conjuntos pequeños de comandos.
- Cómo mapear frases habladas a mensajes de control deterministas para sistemas visuales.
- Cómo OSC permite desacoplar la lógica de reconocimiento (Python) de la lógica de render (Processing).
- Cómo decisiones pequeñas de UX (push-to-talk, feedback breve, ventana redimensionable) mejoran la calidad de la demo.

### Dificultades

- La calidad de reconocimiento offline cae cuando el modelo de lenguaje no está alineado con el idioma objetivo.
- Mantener precisión de comandos sin perder tolerancia frente a ruido y variaciones de pronunciación.
- Balancear una consola limpia con suficiente información útil para depurar en vivo.

---

## Contribuciones grupales (si aplica)

| Integrante | Rol |
|---|---|
| Juan Esteban Santacruz Corredor | Diseño del flujo de interacción y definición del vocabulario de comandos |
| Nicolas Quezada Mora | Implementación del pipeline de voz en Python y ajustes de reconocimiento |
| Cristian Steven Motta Ojeda | Integración OSC entre reconocimiento y visualización |
| Sebastian Andrade Cedano | Implementación visual en Processing y comportamiento de animaciones |
| Esteban Barrera Sanabria | Pruebas funcionales, validación de comandos y control de calidad de la demo |
| Jerónimo Bermúdez Hernández | Documentación técnica, curaduría de evidencias y edición final del README |

---

## Estructura del proyecto

```
semana_07_10_reconocimiento_voz_local/
├── media/                           # Evidencias (gifs, imagenes, videos)
│   ├── processing_1.gif
│   └── python_1.gif
├── processing/
│   └── processing.pde               # Receptor visual OSC (ventana redimensionable)
├── python/
│   ├── requirements.txt             # Dependencias de Python
│   └── voice_to_osc.py              # Reconocimiento local + emisor OSC
├── semana_07_10_reconocimiento_voz_local.md
└── README.md                        # Este documento
```

---

## Referencias

- PocketSphinx: https://pypi.org/project/pocketsphinx/
- Python OSC: https://pypi.org/project/python-osc/
- SoundDevice: https://python-sounddevice.readthedocs.io/
- Processing: https://processing.org/
- oscP5 para Processing: https://sojamo.de/libraries/oscP5/
