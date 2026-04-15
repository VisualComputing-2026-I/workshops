import { useRef, useEffect } from "react";
import { useGLTF, useAnimations } from "@react-three/drei";

export default function Model({ anim }) {
  const group = useRef();

  const { scene, animations } = useGLTF("/defeated.glb");
  const { actions } = useAnimations(animations, group);

  const current = useRef(null);

  useEffect(() => {
    if (!actions) return;

    // STOP
    if (anim === null) {
      if (current.current) {
        current.current.fadeOut(0.2);
        current.current.stop();
        current.current = null;
      }
      return;
    }

    const next = actions[anim];
    next.reset().fadeIn(0.2).play();
    current.current = next;
  }, [anim, actions]);

  return (
    <group ref={group}>
      <primitive object={scene} scale={1.5} />
    </group>
  );
}
