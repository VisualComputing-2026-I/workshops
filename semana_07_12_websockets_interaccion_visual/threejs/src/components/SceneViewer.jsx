import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { useRef } from 'react'
import * as THREE from 'three'

function Agent({ data }) {
  const meshRef = useRef()
  const targetPosition = useRef(new THREE.Vector3(0, 1, 0))

  useFrame((state) => {
    if (!meshRef.current) {
      return
    }

    targetPosition.current.set(data.x, data.y, data.z)
    meshRef.current.position.lerp(targetPosition.current, 0.18)

    meshRef.current.rotation.y += state.clock.getDelta() * data.pulse * 0.45
  })

  return (
    <mesh ref={meshRef} castShadow>
      <sphereGeometry args={[0.6, 48, 48]} />
      <meshStandardMaterial color={data.color} emissive={data.color} emissiveIntensity={0.22} roughness={0.35} metalness={0.3} />
    </mesh>
  )
}

function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]} receiveShadow>
      <circleGeometry args={[8, 64]} />
      <meshStandardMaterial color="#101b33" roughness={0.9} metalness={0.05} />
    </mesh>
  )
}

export default function SceneViewer({ data }) {
  return (
    <Canvas shadows camera={{ position: [5, 4, 5], fov: 50 }}>
      <ambientLight intensity={0.4} />
      <directionalLight position={[4, 6, 3]} intensity={1.1} color="#ffffff" castShadow />
      <pointLight position={[-3, 2, -3]} intensity={0.5} color={data.color} />

      <Agent data={data} />
      <Ground />

      <gridHelper args={[12, 12, '#2a3f6d', '#1b2f56']} position={[0, 0.001, 0]} />
      <axesHelper args={[2]} />
      <OrbitControls enableDamping dampingFactor={0.08} rotateSpeed={0.65} zoomSpeed={0.8} />
    </Canvas>
  )
}
