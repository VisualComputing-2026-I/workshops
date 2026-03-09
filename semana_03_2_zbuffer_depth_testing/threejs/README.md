# Taller Z-Buffer & Depth Testing — Three.js

## Descripción

Implementación interactiva en **Three.js** (vanilla ES modules, sin bundler) que permite explorar en tiempo real el funcionamiento del **Z-buffer** y el **depth testing** en el pipeline de renderizado 3D.

La aplicación corre directamente en el navegador cargando Three.js desde CDN mediante un **import map**.

---

## Estructura del proyecto

```
threejs/
├── index.html              # Punto de entrada
├── css/
│   └── styles.css          # Estilos de UI y overlay
├── js/
│   ├── main.js             # Orquestador: renderer, cámara, loop, split-screen
│   ├── scene-objects.js    # Objetos 3D, luces y planos de Z-fighting
│   ├── shaders.js          # Shaders GLSL de visualización de profundidad
│   └── gui-controls.js    # Panel lil-gui con todos los controles
└── README.md
```

---

## Cómo ejecutar

El proyecto usa ES modules (`type="module"`), por lo que necesita un servidor HTTP local.

### Opción 1 — VS Code Live Server

1. Instalar la extensión **Live Server**.
2. Clic derecho sobre `index.html` → **Open with Live Server**.

### Opción 2 — Python

```bash
cd threejs
python -m http.server 8080
```

Luego abrir `http://localhost:8080`.

---

## Funcionalidades implementadas

### 1. Escena con objetos a diferentes profundidades

Cubo, esfera, cono y torus colocados en posiciones superpuestas para que el depth buffer determine la oclusión.

### 2. Activar / desactivar Depth Test

Con el control **"Depth Test"** se puede comparar visualmente:
- **ON**: oclusiones correctas basadas en el Z-buffer.
- **OFF**: los objetos se pintan por order de draw call, generando artefactos (painter's algorithm).

### 3. Comparación lado a lado (split-screen)

El control **"Comparar (split)"** divide la pantalla en dos mitades usando scissor test:
- **Izquierda**: renderizado SIN depth test.
- **Derecha**: renderizado CON depth test.

### 4. Visualización del Depth Buffer

Dos modos de shader intercambiables:

| Modo | Shader | Descripción |
|------|--------|-------------|
| **Depth** | `gl_FragColor = vec4(vec3(gl_FragCoord.z), 1.0)` | Profundidad nativa no-lineal del GPU |
| **Depth Lineal** | Linearización con uniforms `uNear` / `uFar` | Distribución uniforme de profundidad |

### 5. Ajuste de Near / Far planes

Sliders para modificar `camera.near` y `camera.far` en tiempo real y observar:
- Pérdida de precisión con rangos muy amplios.
- Mayor resolución al acercar el near plane.
- Efecto sobre la distribución no-lineal del depth buffer.

### 6. Z-Fighting: demostración y solución

Dos planos casi coplanares (separación de 0.001 unidades) que producen **Z-fighting** visible. El control **"Resolver (offset)"** aplica:
- `material.polygonOffset = true`
- `polygonOffsetFactor = -1` / `polygonOffsetUnits = -1`
- Separación mínima adicional.

---

## Código relevante

### Shader de profundidad no-lineal

```glsl
// Fragment shader
void main() {
  gl_FragColor = vec4(vec3(gl_FragCoord.z), 1.0);
}
```

### Shader de profundidad linealizada

```glsl
uniform float uNear;
uniform float uFar;
varying float vViewZ;
void main() {
  float linearDepth = (vViewZ - uNear) / (uFar - uNear);
  linearDepth = clamp(linearDepth, 0.0, 1.0);
  gl_FragColor = vec4(vec3(linearDepth), 1.0);
}
```

### Toggle de depth test

```js
function setDepthTest(enabled) {
  scene.traverse((obj) => {
    if (!obj.isMesh) return;
    obj.material.depthTest  = enabled;
    obj.material.depthWrite = enabled;
    obj.material.needsUpdate = true;
  });
}
```

### Solución de Z-fighting

```js
material.polygonOffset       = true;
material.polygonOffsetFactor = -1;
material.polygonOffsetUnits  = -1;
```

---

## Evidencias visuales sugeridas

| # | Captura | Descripción |
|---|---------|-------------|
| 1 | `depth_test_off.png` | Artefactos de oclusión con depth test desactivado |
| 2 | `depth_test_on.png` | Oclusión correcta con depth test activado |
| 3 | `depth_visualization.png` | Escena renderizada con shader de profundidad |
| 4 | `depth_linear_vs_nonlinear.png` | Comparación visual depth lineal vs no-lineal |
| 5 | `split_comparison.png` | Vista split-screen sin/con depth test |
| 6 | `zfighting_active.png` | Z-fighting visible entre planos coplanares |
| 7 | `zfighting_solved.png` | Z-fighting resuelto con polygonOffset |
| 8 | `near_far_precision.png` | Efecto de near/far extremos en precisión |

> Guardar las capturas en `../media/` y referenciarlas en el README principal del taller.

---

## Prompts utilizados

Se utilizó IA generativa (GitHub Copilot) para:
- Estructura inicial del proyecto Three.js con import maps.
- Shaders GLSL de visualización de profundidad.
- Lógica de comparación split-screen con scissor test.
- Panel de controles lil-gui.

---

## Aprendizajes y dificultades

- El depth buffer de WebGL almacena profundidad de forma **no-lineal** (más precisión cerca del near plane), lo que explica el Z-fighting en objetos lejanos.
- `polygonOffset` es la solución estándar de GPU para Z-fighting sin modificar geometría.
- La comparación split-screen con scissor test permite ver claramente la diferencia entre renderizado con y sin depth testing.
- Ajustar `near` demasiado bajo (e.g., 0.001) desperdicia bits de precisión del depth buffer en el rango cercano.
