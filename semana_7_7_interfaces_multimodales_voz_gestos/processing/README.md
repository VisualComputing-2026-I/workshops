# Visualizador OSC en Processing

Proyecto base para la tarea: una escena visual en Processing que recibe comandos desde Python via OSC y los vincula a cambios visuales.

## Incluye

- `processing.pde`: sketch principal en Processing.
- `python_sender.py`: emisor OSC de ejemplo en Python.

## Requisitos

### Processing

1. Abrir esta carpeta en Processing.
2. Instalar la libreria `oscP5` desde `Sketch > Import Library... > Add Library...`.
3. Ejecutar el sketch.

### Python

Instalar `python-osc`:

```bash
pip install python-osc
```

## Puerto OSC

El sketch escucha en `127.0.0.1:12000`.

## Protocolo simple usado

- `/color <nombre>`
- `/shape <nombre>`
- `/anim <accion>`
- `/text <mensaje>`

## Valores soportados

### Color

`rojo`, `verde`, `azul`, `amarillo`, `naranja`, `morado`, `rosa`, `cian`, `blanco`, `negro`

### Forma

`circulo`, `cuadrado`, `triangulo`, `estrella`

### Animacion

`start`, `stop`, `toggle`

## Ejecucion

1. Ejecutar `processing.pde` en Processing.
2. En otra terminal, ejecutar:

```bash
python python_sender.py
```

3. Probar comandos como:

```text
color rojo
shape estrella
anim stop
text ultimo comando recibido desde python
anim start
```

## Resultado esperado

- Cambia el color del objeto principal.
- Cambia la forma del objeto.
- Inicia o detiene la animacion.
- Muestra en pantalla el ultimo comando recibido.
