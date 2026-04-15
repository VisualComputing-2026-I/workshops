import { Canvas } from "@react-three/fiber";
import Model from "./Model";
import { useState } from "react";
import { OrbitControls } from '@react-three/drei'

export default function App() {
  const [anim, setAnim] = useState("Armature|mixamo.com|Layer0");

  return (
    <>
      <div style={{ position: "absolute", top: 20, left: 20 }}>
        <button onClick={() => setAnim('Armature|mixamo.com|Layer0')}>
          Play
        </button>

      </div>

      <Canvas camera={{ position: [0, 1, 3] }}>
        <ambientLight intensity={3} />
        <directionalLight position={[2, 2, 2]} intensity={2} />
        <OrbitControls></OrbitControls>
        <Model anim={anim} />
      </Canvas>
    </>
  );
}
