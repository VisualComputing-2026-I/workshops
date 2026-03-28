# Three.js con React Three Fiber

Ejemplo básico replicable para el taller. La escena incluye:

- Geometrías básicas con `boxGeometry` y `sphereGeometry`
- Estructuras repetitivas creadas al mapear arreglos
- Deformación procedural de una malla editando `bufferGeometry.attributes.position.array`
- Animación con `useFrame()`
- Árbol fractal construido de forma recursiva

## Ejecutar

```bash
npm install
npm run dev
```

## Dependencias principales

- `react`
- `three`
- `@react-three/fiber`
- `@react-three/drei`

## Estructura

- `src/App.jsx`: escena y componentes principales
- `src/styles.css`: estilos de la interfaz superpuesta
