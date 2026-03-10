import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import ProceduralMesh from "./components/ProceduralMesh"

export default function App() {
  return (
    <Canvas style={{ width: "100%", height: "100%" }} camera={{ position: [2,2,2] }}>
      <ambientLight />
      <ProceduralMesh />
      <OrbitControls />
    </Canvas>
  )
}