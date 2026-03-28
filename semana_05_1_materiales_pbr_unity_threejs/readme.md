# Taller Materiales PBR Unity Threejs

## Nombre de los estudiantes
- Juan Esteban Santacruz Corredor
- Nicolas Quezada Mora
- Cristian Stiven Motta
- Cristian Steven Motta Ojeda
- Sebastian Andrade Cedano
- Esteban Barrera Sanabria
- Jerónimo Bermúdez Hernández

## Fecha de entrega

2026-03-27

---

## Descripcion breve

En este taller se desarrollaron dos implementaciones para explorar el uso de materiales PBR (Physically Based Rendering) en entornos 3D en tiempo real: Unity y React Three Fiber (Three.js). El objetivo principal fue comprender cómo funcionan los mapas PBR (albedo, roughness, metalness y normal), cómo afectan la iluminación y cómo pueden modificarse dinámicamente mediante interfaces de usuario.

En Unity se construyó una escena con objetos básicos, iluminación direccional y materiales configurados con el shader Standard/Lit. Se implementó una interfaz de sliders para modificar propiedades físicas como smoothness y metallic en tiempo real y observar su impacto visual.

En React Three Fiber se replicó una escena equivalente utilizando Three.js, cargando texturas PBR desde archivos externos y aplicándolas a una geometría con MeshStandardMaterial. Se añadió un panel de control interactivo para modificar roughness y metalness dinámicamente, permitiendo comparar resultados entre materiales físicos y materiales básicos.

---

## Implementaciones

### Unity

Se creó una escena 3D básica con:

- un plano como piso,
- un cubo y una esfera como objetos principales,
- una luz direccional y una luz ambiental.

Se importó un conjunto de texturas PBR (albedo, roughness, metalness y normal) y se configuró un material utilizando el shader Standard/Lit. Este material fue aplicado a la esfera, mientras que el cubo utilizó un material simple para comparación visual.

Se desarrolló un script en C# que conecta sliders de la interfaz de usuario con propiedades del material, permitiendo modificar smoothness y metallic en tiempo real durante la ejecución de la escena.

El proyecto en Unity demuestra:
- uso correcto de mapas PBR,
- diferencias visuales entre materiales físicos y no físicos,
- y control interactivo de parámetros de shading.

### React Three Fiber / Three.js

Se implementó una escena equivalente en React utilizando React Three Fiber y Three.js. La escena contiene:

- un plano como piso,
- una esfera con material PBR,
- un cubo con MeshBasicMaterial para comparación,
- iluminación ambiental y direccional,
- controles de cámara con OrbitControls.

Las texturas PBR fueron cargadas mediante TextureLoader y aplicadas a un MeshStandardMaterial utilizando las propiedades:

- map
- roughnessMap
- metalnessMap
- normalMap

Se integró la librería Leva para crear un panel de control que permite modificar roughness y metalness en tiempo real, replicando la funcionalidad de los sliders implementados en Unity.

Esta implementación permitió observar las diferencias entre el pipeline de materiales de Unity y el de Three.js, así como las convenciones distintas para smoothness y roughness.

---

## Resultados visuales


### Unity - Implementacion

![Resultado Unity](./media/Unity.gif)

Comparacion entre objeto con material PBR y objeto con material plano. Ademas de la Interfaz de usuario con sliders modificando propiedades de metallic y smoothness en tiempo real.

### React Three Fiber - Implementacion


![Resultado Threejs](./media/Threejs.gif)

Escena 3D con materiales PBR y panel interactivo Leva modificando parametros fisicos. Ademas de la Comparacion visual entre MeshStandardMaterial y MeshBasicMaterial bajo la misma iluminacion.

---

## Codigo relevante

### Script de control de materiales en Unity

```csharp
using UnityEngine;
using UnityEngine.UI;

public class MaterialUIController : MonoBehaviour
{
    public Material sphereMaterial;
    public Material cubeMaterial;

    public Slider sphereSmoothness;
    public Slider cubeMetallic;
    public Slider cubeSmoothness;

    void Start()
    {
        sphereSmoothness.onValueChanged.AddListener(SetSphereSmoothness);
        cubeMetallic.onValueChanged.AddListener(SetCubeMetallic);
        cubeSmoothness.onValueChanged.AddListener(SetCubeSmoothness);
    }

    void SetSphereSmoothness(float value)
    {
        sphereMaterial.SetFloat("_Smoothness", value);
    }

    void SetCubeMetallic(float value)
    {
        cubeMaterial.SetFloat("_Metallic", value);
    }

    void SetCubeSmoothness(float value)
    {
        cubeMaterial.SetFloat("_Smoothness", value);
    }
}
```

### Escena en React Three Fiber

```javascript
import * as THREE from "three"
import { useLoader } from "@react-three/fiber"
import { TextureLoader } from "three"
import { useControls } from "leva"

export default function Scene() {
  const [color, roughness, metalness, normal] = useLoader(TextureLoader, [
    "/textures/color.png",
    "/textures/roughness.png",
    "/textures/metalness.png",
    "/textures/normal.png",
  ])

  const { rough, metal } = useControls({
    rough: { value: 0.5, min: 0, max: 1 },
    metal: { value: 0.5, min: 0, max: 1 },
  })

  return (
    <>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#777" />
      </mesh>

      <mesh position={[-1.5, 0, 0]}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial
          map={color}
          roughnessMap={roughness}
          metalnessMap={metalness}
          normalMap={normal}
          roughness={rough}
          metalness={metal}
        />
      </mesh>

      <mesh position={[1.5, 0, 0]}>
        <boxGeometry />
        <meshBasicMaterial color="orange" />
      </mesh>
    </>
  )
}
```

## Escena en React Three Fiber

- "Cómo cargar texturas PBR en React Three Fiber y aplicarlas a MeshStandardMaterial."

- "Cómo estructurar un proyecto para cargar texturas correctamente en Vite usando la carpeta public."


## Aprendizajes y dificultades

### Aprendizajes

Se comprendió en profundidad el flujo de trabajo de materiales PBR y cómo distintos motores gráficos implementan el mismo modelo físico con convenciones diferentes. En particular, se aprendió que Unity utiliza smoothness mientras que Three.js utiliza roughness directamente, lo cual requiere conversiones o ajustes al compartir texturas entre motores.

También se reforzó el uso de interfaces interactivas para modificar parámetros de shading en tiempo real, lo cual es una herramienta útil para depuración visual y aprendizaje de iluminación.

### Mejoras futuras

Como mejora futura, se podría extender el taller utilizando MeshPhysicalMaterial para simular materiales más complejos como vidrio o superficies con clear coat, así como implementar entornos HDRI para obtener iluminación basada en imágenes y reflejos más realistas.

## Mejoras futuras

- Documentacion oficial de Unity sobre materiales Standard: https://docs.unity3d.com/Manual/shader-StandardShader.html
- Documentacion de React Three Fiber: https://docs.pmnd.rs/react-three-fiber
- Documentacion de Three.js MeshStandardMaterial: https://threejs.org/docs/#api/en/materials/MeshStandardMaterial
- Libreria de texturas PBR: https://ambientcg.com/