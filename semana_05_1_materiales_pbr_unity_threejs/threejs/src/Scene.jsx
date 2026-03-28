import * as THREE from "three"
import { useLoader } from "@react-three/fiber"
import { TextureLoader } from "three"
import { useControls } from "leva"

export default function Scene() {
  const [color, roughness, metalness, normal] = useLoader(TextureLoader, [
    "/textures/color.png",
    "/textures/roughness.png",
    "/textures/metalness.png",
    " textures/normal.png",
  ])

  const { rough, metal } = useControls({
    rough: { value: 0.5, min: 0, max: 1 },
    metal: { value: 0.5, min: 0, max: 1 },
  })

  return (
    <>
      {/* Piso */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#777" />
      </mesh>

      {/* Objeto PBR */}
      <mesh position={[-1.5, 0, 0]}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial
          map={color}
          roughnessMap={roughness}
          metalnessMap={metalness}
          normalMap={normal}
          roughness={rough}
          metalness={metal}
        />
      </mesh>

      {/* Objeto comparación */}
      <mesh position={[1.5, 0, 0]}>
        <boxGeometry />
        <meshBasicMaterial color="orange" />
      </mesh>
    </>
  )
}