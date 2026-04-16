import { useMemo, useState } from "react";
import * as THREE from "three";

export default function Target({ position, planeY, onChange, onDragChange }) {
  const [dragging, setDragging] = useState(false);
  const dragPlane = useMemo(
    () => new THREE.Plane(new THREE.Vector3(0, 1, 0), -planeY),
    [planeY],
  );
  const hitPoint = useMemo(() => new THREE.Vector3(), []);

  const updateFromRay = (ray) => {
    if (ray.intersectPlane(dragPlane, hitPoint)) {
      onChange([hitPoint.x, planeY, hitPoint.z]);
    }
  };

  return (
    <mesh
      position={position}
      onPointerDown={(event) => {
        event.stopPropagation();
        event.currentTarget.setPointerCapture(event.pointerId);
        setDragging(true);
        onDragChange?.(true);
        updateFromRay(event.ray);
      }}
      onPointerUp={(event) => {
        event.stopPropagation();
        event.currentTarget.releasePointerCapture(event.pointerId);
        setDragging(false);
        onDragChange?.(false);
      }}
      onPointerMove={(event) => {
        if (!dragging) return;
        event.stopPropagation();
        updateFromRay(event.ray);
      }}
      onPointerLeave={() => {
        if (!dragging) return;
        setDragging(false);
        onDragChange?.(false);
      }}
    >
      <sphereGeometry args={[0.15, 32, 32]} />
      <meshStandardMaterial
        color="#ff6b6b"
        emissive="#a22626"
        emissiveIntensity={0.5}
      />
    </mesh>
  );
}
