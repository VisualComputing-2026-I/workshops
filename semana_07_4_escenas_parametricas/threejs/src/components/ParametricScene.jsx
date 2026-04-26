import { useRef } from "react"
import { useFrame } from "@react-three/fiber"
import { sceneData } from "../data/sceneData"

function ParametricObject({ data, globalScale, animate }) {
  const ref = useRef()

  useFrame((_, delta) => {
    if (animate && ref.current) {
      ref.current.rotation.y += delta * 0.5
    }
  })

  const s = data.scale * globalScale
  const rot = (data.rotation * Math.PI) / 180

  return (
    <mesh ref={ref} position={data.position} rotation={[0, rot, 0]} scale={[s, s, s]}>
      {data.type === "box"      && <boxGeometry args={[1, 1, 1]} />}
      {data.type === "sphere"   && <sphereGeometry args={[0.5, 32, 32]} />}
      {data.type === "cylinder" && <cylinderGeometry args={[0.4, 0.4, 1, 32]} />}
      <meshStandardMaterial color={data.color} />
    </mesh>
  )
}

export default function ParametricScene({ globalScale, animate, showBoxes, showSpheres, showCylinders }) {
  const filtered = sceneData.filter(obj => {
    if (obj.type === "box"      && !showBoxes)     return false
    if (obj.type === "sphere"   && !showSpheres)   return false
    if (obj.type === "cylinder" && !showCylinders) return false
    return true
  })

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      {filtered.map(obj => (
        <ParametricObject
          key={obj.id}
          data={obj}
          globalScale={globalScale}
          animate={animate}
        />
      ))}
      <gridHelper args={[20, 20, "#444", "#222"]} />
    </>
  )
}