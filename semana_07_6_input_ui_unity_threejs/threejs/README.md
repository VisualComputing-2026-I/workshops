# Taller 6.1: Input & UI - Three.js + React Three Fiber

## Descripción
Este taller demuestra cómo capturar entrada del usuario (mouse, teclado) e implementar interfaces visuales (UI) usando **Three.js** con **React Three Fiber**, incluyendo:

- **Movimiento 3D:** WASD / Flechas para mover el jugador
- **Controles de Cámara:** OrbitControls para orbitar alrededor del jugador
- **Click Detection:** Interacción con objetos 3D (cubo rojo)
- **UI HTML Overlay:** Paneles informativos y botones
- **Sliders Dinámicos:** Ajustar velocidad de movimiento y rotación

## Tecnologías

- **React 18** - Framework de interfaz
- **Three.js** - Renderizado 3D
- **@react-three/fiber** - Renderer de Three.js para React
- **@react-three/drei** - Utilidades (OrbitControls, Html)
- **Leva** - Panel de controles interactivos
- **Vite** - Build tool

## Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Build para producción
npm run build
```

## Controles

| Tecla/Input | Acción |
|-------------|--------|
| **W / ↑** | Avanzar |
| **A / ←** | Izquierda |
| **S / ↓** | Retroceder |
| **D / →** | Derecha |
| **Mouse Drag** | Orbitar cámara |
| **Rueda Mouse** | Zoom in/out |
| **Click Izquierdo** | Clickear objeto rojo (cambiar color) |
| **R** | Resetear posición del jugador |

## Estructura de Archivos

```
src/
├── main.jsx          # Punto de entrada React
├── App.jsx           # Componente raíz con Canvas
├── Scene.jsx         # Lógica de escena 3D y input
├── Landscape.jsx     # Geometrías 3D (piso, cubo, etc)
├── ControlsUI.jsx    # Paneles de UI (Html + Leva)
└── ControlsUI.css    # Estilos de UI
```

## Características Principales

### 1. Input del Teclado (WASD)
```javascript
useEffect(() => {
  const handleKeyDown = (e) => {
    keysPressed.current[e.key.toLowerCase()] = true
  }
  window.addEventListener('keydown', handleKeyDown)
  // ...
})
```

### 2. Movimiento con useFrame
```javascript
useFrame((state) => {
  // Evaluar keysPressed.current y mover jugador
  if (keysPressed.current['w']) moveZ -= 1
})
```

### 3. Click Detection en Objetos 3D
```javascript
<mesh onClick={onCubeClick}>
  <boxGeometry args={[1, 1, 1]} />
</mesh>
```

### 4. UI HTML Overlay con @react-three/drei
```javascript
<Html fullScreen>
  <div className="ui-container">
    {/* UI aquí */}
  </div>
</Html>
```

### 5. OrbitControls para Cámara
```javascript
<OrbitControls 
  target={[playerPos[0], 1, playerPos[2]]}
  autoRotate={false}
/>
```

## Comparación con el Taller Unity

| Aspecto | Unity | Three.js + React |
|--------|-------|------------------|
| Input | `Input.GetKey()` | `window.addEventListener('keydown')` |
| Física | Physics engine | Manual con estado |
| Cámara | Manual rotation | `OrbitControls` |
| UI | Canvas/UI System | HTML DOM + React |
| Estado | MonoBehaviour | React hooks (useState) |

## Notas

- El proyecto usa `useFrame` del hook de @react-three/fiber para actualizar lógica cada frame
- El estado del jugador se maneja con React hooks, no con variables globales
- La UI es completamente reactiva y se actualiza con cambios en el estado
- Los controles de Leva permiten ajustar parámetros en tiempo real sin recompilar

## Autor
Computación Visual - Semana 7, Taller 6
