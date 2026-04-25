import { Canvas } from "@react-three/fiber";
import { useState } from "react";
import { Link } from "react-router-dom";

function Cubo({ onClick, position }) {
  return (
    <mesh position={position} onClick={onClick}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}

export default function Juego() {
  const [score, setScore] = useState(0);
  const [position, setPosition] = useState([0, 0, 0]);

  const moverCubo = () => {
    // nueva posición aleatoria
    const nuevaPos = [
      (Math.random() - 0.5) * 5,
      (Math.random() - 0.5) * 5,
      (Math.random() - 0.5) * 5,
    ];

    setPosition(nuevaPos);
    setScore(score + 1);
  };

  return (
    <div style={{ height: "100vh" }}>
      <Link to="/">Volver</Link>

      <h1>Haz click en el cubo!</h1>
      
      <div style={{ fontSize: "20px" }}>
            Score: {score}
      </div>

      <Canvas>
        <ambientLight />
        <pointLight position={[10, 10, 10]} />

        <Cubo onClick={moverCubo} position={position} />

      </Canvas>
    </div>
  );
}