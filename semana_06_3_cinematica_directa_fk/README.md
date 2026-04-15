# Forward Kinematics: Brazo Mecánico con Articulaciones Encadenadas

## Nombre del estudiante

<!-- TODO: Completar -->

## Fecha de entrega

'2026-04-11'

---

## Descripción breve

En este taller se implementó un sistema de cinemática directa (forward kinematics) en Unity, el cual consiste en una cadena de articulaciones donde cada segmento propaga su transformación a los siguientes. Se construyó un brazo mecánico compuesto por tres segmentos cilíndricos conectados jerárquicamente (`Base → Brazo1 → Brazo2 → Pinza`), con dos modos de operación: animación automática mediante funciones sinusoidales y control manual a través de sliders en la UI.

---

## Implementación en Unity

### Jerarquía de objetos

La base del sistema es la jerarquía de GameObjects en Unity. Cada articulación es un `GameObject` vacío que actúa como pivot de rotación, y cada segmento visual es un cilindro hijo de dicho pivot. Esto permite que al rotar una articulación, todos los segmentos descendientes se muevan en consecuencia, lo cual es el principio fundamental de la cinemática directa.

La jerarquía final quedó de la siguiente forma:

```
Base (GO vacío, pivot en y=0)
└── CilindroBase (visual)
    Brazo1 (GO vacío, pivot en y=1.0)
    └── CilindroB1 (visual)
        Brazo2 (GO vacío, pivot en y=1.25)
        └── CilindroB2 (visual)
            Pinza (GO vacío, pivot en y=1.2)
            └── CilindroP (visual)
                Extremo (GO vacío, punto de seguimiento)
```

Un aspecto clave fue posicionar cada cilindro con un desplazamiento local en Y igual a la mitad de su altura, de forma que su base coincida con el pivot de la articulación y la rotación se vea correctamente anclada.

### Script de cinemática

El script `ForwardKinematics.cs` centraliza toda la lógica del sistema. Expone referencias a cada articulación y a los controles de UI, y en cada frame decide qué modo ejecutar según el estado de un `Toggle`.

#### Modo animación

Cuando el toggle está activo, cada articulación recibe un ángulo calculado a partir de `Mathf.Sin(Time.time)` escalado por una amplitud y una velocidad configurables desde el Inspector. El desfase de fase entre articulaciones (`Mathf.PI / 3f`) genera un movimiento más orgánico y menos mecánico.

![animacion](./media/animacion.gif)

#### Modo manual con sliders

Cuando el toggle está inactivo, cada articulación toma su ángulo directamente del valor del slider correspondiente. Los sliders se deshabilitan automáticamente al activar la animación y se vuelven a habilitar al apagarla, usando `onValueChanged` para escuchar el cambio del toggle sin necesidad de chequearlo en cada frame.

![sliders](./media/sliders.gif)

#### Visualización de trayectoria

Se implementó un buffer circular de posiciones del `Extremo` del brazo, el cual se dibuja frame a frame con `Debug.DrawLine()`. Las líneas más antiguas se dibujan con menor opacidad mediante un fade basado en el índice, lo que permite visualizar la trayectoria reciente del extremo en la Scene view con Gizmos activados.

---

## Código Relevante

Script principal de forward kinematics:

```csharp
using UnityEngine;
using UnityEngine.UI;

public class ForwardKinematics : MonoBehaviour
{
    public Transform brazo1;
    public Transform brazo2;
    public Transform pinza;
    public Transform extremo;

    public Slider sliderB1;
    public Slider sliderB2;
    public Slider sliderPinza;
    public Toggle toggleAnimacion;

    public float amplitudB1    = 60f;
    public float amplitudB2    = 40f;
    public float amplitudPinza = 20f;

    public float velocidadB1    = 0.8f;
    public float velocidadB2    = 1.2f;
    public float velocidadPinza = 1.5f;

    public bool mostrarTrayectoria = true;
    public int  maxPuntos          = 300;
    public Color colorLinea        = Color.cyan;

    private Vector3[] _puntos;
    private int       _indice = 0;
    private bool      _lleno  = false;

    void Start()
    {
        _puntos = new Vector3[maxPuntos];
        ActualizarUI(toggleAnimacion.isOn);
        toggleAnimacion.onValueChanged.AddListener(ActualizarUI);
    }

    void ActualizarUI(bool animando)
    {
        sliderB1.interactable    = !animando;
        sliderB2.interactable    = !animando;
        sliderPinza.interactable = !animando;
    }

    void Update()
    {
        if (toggleAnimacion.isOn)
            AnimarArticulaciones();
        else
            MoverArticulaciones();

        RegistrarTrayectoria();

        if (mostrarTrayectoria)
            DibujarTrayectoria();
    }
}
```

---

## Aprendizajes y dificultades

### Aprendizajes

Se pudo comprender cómo funciona la propagación de transformaciones en una jerarquía de Unity, y cómo este comportamiento por defecto del motor es suficiente para implementar forward kinematics sin ninguna matemática matricial explícita. También se entendió la diferencia entre `localEulerAngles`, `localRotation` y `Transform.Rotate()`, siendo este último acumulativo y los dos primeros absolutos, lo cual es determinante al controlar ángulos desde sliders. Adicionalmente se practicó el uso de listeners de UI como `onValueChanged` para mantener la lógica desacoplada del `Update`.

### Dificultades

La mayor dificultad fue la configuración correcta de los pivots de cada articulación. El modo de visualización de gizmos en Unity muestra por defecto el centro geométrico del grupo (`Center`) en lugar de la posición real del transform (`Pivot`), lo que generaba confusión al intentar verificar si la rotación ocurría desde el punto correcto. Una vez cambiado ese ajuste en el editor, el comportamiento fue el esperado.

### Mejoras futuras

Podría extenderse el sistema para incluir cinemática inversa (IK), donde dado un punto destino en el espacio, el sistema calcule automáticamente los ángulos necesarios en cada articulación para alcanzarlo.

---

## Estructura del proyecto

```
forward_kinematics/
├── unity/                     # Proyecto en Unity
├── media/                     # GIFs de resultados
│   ├── animacion.gif
│   └── sliders.gif
└── README.md                  # Este archivo
```
