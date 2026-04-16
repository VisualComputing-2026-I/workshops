# Taller Cinematica Inversa Ik

## Nombre del estudiante
- Juan Esteban Santacruz Corredor
- Nicolas Quezada Mora
- Cristian Steven Motta Ojeda
- Sebastian Andrade Cedano
- Esteban Barrera Sanabria
- Jeronimo Bermudez Hernandez

## Fecha de entrega

`15 de abril de 2026`

---

## Descripcion breve

El objetivo de este taller fue implementar cinematica inversa para un brazo articulado y comparar su comportamiento en distintos entornos. Se desarrollo una escena en React Three Fiber con un objetivo arrastrable, un solver CCD por frame, una linea de referencia y un modo alternativo de cinematica directa con poses predefinidas.

---

## Implementaciones

### Three.js / React Three Fiber

- Cadena jerarquica de eslabones con `boxGeometry`.
- Objetivo arrastrable con el mouse sobre un plano de trabajo.
- Solver CCD en cada `useFrame` para alinear la punta con el objetivo.
- Linea de referencia desde la base al objetivo.
- Modo IK / FK con poses predefinidas y alternancia automatica.
- HUD con distancia restante e iteraciones por frame.

### Unity

- Escena de cinematica inversa con brazo segmentado y objetivo interactivo.
- Ajuste del brazo para alcanzar el objetivo y visualizacion del resultado.

---

## Resultados visuales

### Three.js - Implementacion

![Three.js IK vista general](./media/threejs.gif)

Vista general del brazo alcanzando el objetivo con CCD.

![Three.js IK detalle](./media/threejs.gif)

Detalle del seguimiento del objetivo con la cadena de eslabones.

### Unity - Implementacion

![Unity IK vista general](./media/unity.gif)

Vista general de la escena en Unity.

![Unity IK detalle](./media/unity.gif)

Detalle del brazo alcanzando el objetivo en Unity.

---

## Codigo relevante

### Solver CCD (fragmento)

```javascript
for (let iter = 0; iter < iterations; iter += 1) {
  for (let i = segmentCount - 1; i >= 0; i -= 1) {
    const joint = jointRefs[i].current;
    if (!joint) continue;

    joint.getWorldPosition(jointPos);
    endRef.current.getWorldPosition(endPos);

    toEnd.copy(endPos).sub(jointPos);
    toTarget.copy(targetVec).sub(jointPos);

    if (toEnd.lengthSq() < 1e-8 || toTarget.lengthSq() < 1e-8) continue;

    toEnd.normalize();
    toTarget.normalize();
    axis.crossVectors(toEnd, toTarget);
    if (axis.lengthSq() < 1e-10) continue;

    axis.normalize();
    const angle = Math.acos(
      THREE.MathUtils.clamp(toEnd.dot(toTarget), -1, 1),
    );
    const step = Math.min(angle, maxStep);

    joint.getWorldQuaternion(jointQuat);
    invQuat.copy(jointQuat).invert();
    axisLocal.copy(axis).applyQuaternion(invQuat);
    joint.rotateOnAxis(axisLocal, step);
    joint.updateWorldMatrix(true, true);
  }
}
```

### Enlaces al codigo

- Solver y jerarquia de eslabones: [threejs/src/Arm.jsx](./threejs/src/Arm.jsx)
- Objetivo arrastrable: [threejs/src/Target.jsx](./threejs/src/Target.jsx)
- Escena y UI: [threejs/src/App.jsx](./threejs/src/App.jsx)

---

## Prompts utilizados

- No se utilizaron prompts de IA generativa.

---

## Aprendizajes y dificultades

### Aprendizajes

- La tecnica CCD converge de forma estable con iteraciones cortas por frame.
- La jerarquia de `group` simplifica la propagacion de rotaciones en un brazo.
- Separar IK y FK facilita comparar estrategias de control en tiempo real.

### Dificultades

- Evitar oscilaciones cuando el objetivo esta fuera del alcance total.
- Balancear el numero de iteraciones para mantener rendimiento.
- Mantener la interaccion de camara sin interferir con el drag del objetivo.
