# Taller Z-Buffer & Depth Testing — Unity 6

## Versión del Editor

**Unity 6000.3.10f1** (Unity 6)

---

## Descripción

Proyecto Unity que permite explorar interactivamente el funcionamiento del **Z-buffer** y el **depth testing**:

- Escena con múltiples objetos superpuestos generados por código.
- Shader personalizado que visualiza el depth buffer en escala de grises.
- Toggle de depth testing ON/OFF para comparar oclusiones.
- Demostración y resolución de Z-fighting.
- Control dinámico de near/far clip planes.
- HUD con estado de todos los controles.

---

## Estructura

```
unity/Assets/
├── Scripts/
│   ├── SceneSetup.cs              # Genera la escena (objetos, luces, planos Z-fighting)
│   ├── CameraDepthController.cs   # Control de near/far y órbita de cámara
│   ├── DepthMaterialSwitcher.cs   # Alterna entre materiales normales y shader de profundidad
│   ├── DepthTestToggle.cs         # Activa/desactiva depth test en todos los materiales
│   ├── ZFightingController.cs     # Muestra/resuelve Z-fighting
│   └── HUDOverlay.cs              # HUD en pantalla con estado de controles
├── Shaders/
│   ├── DepthVisualization.shader      # Shader Built-in (CG)
│   └── DepthVisualizationURP.shader   # Shader URP (HLSL)
```

---

## Cómo usar

### 1. Abrir el proyecto

1. Abrir **Unity Hub**.
2. Click en **Add** → seleccionar la carpeta `unity/`.
3. Se abrirá con Unity 6000.3.10f1.

### 2. Configurar la escena

1. Crear una **escena vacía** (File → New Scene → Empty).
2. Crear un **GameObject vacío** (GameObject → Create Empty) y nombrarlo `SceneManager`.
3. Agregar los siguientes componentes al GameObject `SceneManager`:
   - `SceneSetup`
   - `DepthMaterialSwitcher`
   - `ZFightingController`
   - `DepthTestToggle`
   - `HUDOverlay`
4. Agregar `CameraDepthController` a la **Main Camera**.
5. Dar **Play**.

### 3. Controles en tiempo de ejecución

| Tecla | Acción |
|-------|--------|
| **Space** | Toggle depth test ON / OFF |
| **1** | Vista normal (materiales estándar) |
| **2** | Vista depth no-lineal (escala de grises) |
| **3** | Vista depth linealizado |
| **D** | Toggle rápido normal ↔ depth |
| **Q / E** | Disminuir / aumentar near plane |
| **Z / X** | Disminuir / aumentar far plane |
| **F** | Mostrar / ocultar planos Z-fighting |
| **G** | Resolver / provocar Z-fighting |
| **T** | Toggle auto-rotación |
| **R** | Reset near/far a valores por defecto |

---

## Shader de profundidad

El shader `DepthVisualization` tiene dos modos:

### No-lineal (nativo del GPU)

```hlsl
o.depth = o.pos.z / o.pos.w;
// ...
return fixed4(depth, depth, depth, 1.0);
```

### Linealizado

```hlsl
float linearDepth = (viewZ - _ProjectionParams.y) /
                    (_ProjectionParams.z - _ProjectionParams.y);
return fixed4(linearDepth, linearDepth, linearDepth, 1.0);
```

Se incluyen dos variantes:
- `DepthVisualization.shader` → para **Built-in Render Pipeline** (CG/CGPROGRAM)
- `DepthVisualizationURP.shader` → para **Universal Render Pipeline** (HLSL)

---

## Evidencias sugeridas

| # | Captura | Descripción |
|---|---------|-------------|
| 1 | `unity_depth_test_off.png` | Artefactos de oclusión con depth test desactivado |
| 2 | `unity_depth_test_on.png` | Oclusión correcta con depth test activado |
| 3 | `unity_depth_shader.png` | Escena con shader de profundidad no-lineal |
| 4 | `unity_depth_linear.png` | Escena con shader de profundidad linealizado |
| 5 | `unity_zfighting.png` | Z-fighting visible entre planos coplanares |
| 6 | `unity_zfighting_solved.png` | Z-fighting resuelto con separación |
| 7 | `unity_near_far.png` | Efecto de near/far extremos |

> Guardar en `../media/` y referenciar en el README principal del taller.

---

## Notas

- Si el proyecto usa **URP**, usar el shader `DepthVisualizationURP.shader`.
- Si usa **Built-in**, usar `DepthVisualization.shader`.
- El `DepthMaterialSwitcher` busca automáticamente el shader disponible.
- Los scripts generan la escena en `Awake()` / `Start()`, no se necesita configurar objetos manualmente.
