import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import Scene from "./Scene"

export default function App() {
  return (
    <Canvas camera={{ position: [3, 2, 5] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={1} />

      <Scene />

      <OrbitControls />
    </Canvas>
  )
}