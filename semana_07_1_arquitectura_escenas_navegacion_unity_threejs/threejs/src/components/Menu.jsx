import { Link } from "react-router-dom";
import { Canvas } from "@react-three/fiber";

export default function Menu() {
  return (
    <div>
      <h1>Menú</h1>

      <Link to="/juego">Ir al Juego</Link>
      <br />
      <Link to="/creditos">Créditos</Link>

      <Canvas>
        <mesh>
          <boxGeometry />
          <meshStandardMaterial color="orange" />
        </mesh>
        <ambientLight />
      </Canvas>
    </div>
  );
}