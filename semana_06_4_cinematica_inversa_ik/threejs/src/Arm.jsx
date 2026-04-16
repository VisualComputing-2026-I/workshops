import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const POSES = {
  rest: [0, 0, 0, 0],
  reach: [0.2, 0.25, 0.2, 0.1],
  curl: [0.9, -0.6, 0.45, -0.25],
};

export default function Arm({
  target,
  mode,
  pose,
  onStats,
  segmentCount = 4,
  segmentLength = 0.9,
  basePosition = [0, 0.5, 0],
}) {
  const rootRef = useRef();
  const endRef = useRef();
  const jointRefs = useMemo(
    () => Array.from({ length: segmentCount }, () => ({ current: null })),
    [segmentCount],
  );
  const currentAngles = useRef(new Array(segmentCount).fill(0));
  const colors = useMemo(
    () =>
      Array.from({ length: segmentCount }, (_, index) =>
        new THREE.Color().setHSL(0.58 - index * 0.07, 0.7, 0.55),
      ),
    [segmentCount],
  );

  const temp = useMemo(
    () => ({
      jointPos: new THREE.Vector3(),
      endPos: new THREE.Vector3(),
      toEnd: new THREE.Vector3(),
      toTarget: new THREE.Vector3(),
      axis: new THREE.Vector3(),
      targetVec: new THREE.Vector3(),
      jointQuat: new THREE.Quaternion(),
      invQuat: new THREE.Quaternion(),
      axisLocal: new THREE.Vector3(),
    }),
    [],
  );

  const iterations = 10;
  const maxStep = 0.35;

  useFrame((_, delta) => {
    if (!rootRef.current || !endRef.current) return;

    const {
      jointPos,
      endPos,
      toEnd,
      toTarget,
      axis,
      targetVec,
      jointQuat,
      invQuat,
      axisLocal,
    } = temp;

    targetVec.set(target[0], target[1], target[2]);

    if (mode === "ik") {
      for (let iter = 0; iter < iterations; iter += 1) {
        for (let i = segmentCount - 1; i >= 0; i -= 1) {
          const joint = jointRefs[i].current;
          if (!joint) continue;

          joint.getWorldPosition(jointPos);
          endRef.current.getWorldPosition(endPos);

          toEnd.copy(endPos).sub(jointPos);
          toTarget.copy(targetVec).sub(jointPos);

          if (toEnd.lengthSq() < 1e-8 || toTarget.lengthSq() < 1e-8) {
            continue;
          }

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
    } else {
      const poseAngles = POSES[pose] || POSES.rest;
      for (let i = 0; i < segmentCount; i += 1) {
        const joint = jointRefs[i].current;
        if (!joint) continue;

        const next = THREE.MathUtils.damp(
          currentAngles.current[i],
          poseAngles[i] ?? 0,
          6,
          delta,
        );
        currentAngles.current[i] = next;
        joint.rotation.set(0, next, 0);
      }
      rootRef.current.updateWorldMatrix(true, true);
    }

    endRef.current.getWorldPosition(endPos);
    const distance = endPos.distanceTo(targetVec);
    onStats?.(distance, iterations);
  });

  const Segment = ({ index }) => {
    const isLast = index === segmentCount - 1;
    return (
      <group ref={(node) => (jointRefs[index].current = node)}>
        <mesh position={[segmentLength * 0.5, 0, 0]}>
          <boxGeometry args={[segmentLength, 0.22, 0.22]} />
          <meshStandardMaterial color={colors[index]} />
        </mesh>
        {!isLast && (
          <group position={[segmentLength, 0, 0]}>
            <Segment index={index + 1} />
          </group>
        )}
        {isLast && <object3D ref={endRef} position={[segmentLength, 0, 0]} />}
      </group>
    );
  };

  return (
    <group ref={rootRef} position={basePosition}>
      <Segment index={0} />
    </group>
  );
}
