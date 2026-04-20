import { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

function ObjectMesh({ settings }) {
  const meshRef = useRef()

  const geometry = useMemo(() => {
    if (settings.objectType === 'sphere') {
      return <sphereGeometry args={[1.1, 48, 48]} />
    }

    if (settings.objectType === 'torus') {
      return <torusGeometry args={[0.95, 0.32, 48, 128]} />
    }

    return <boxGeometry args={[1.8, 1.8, 1.8]} />
  }, [settings.objectType])

  const material = useMemo(() => {
    const commonProps = {
      color: settings.objectColor,
      wireframe: settings.wireframe,
    }

    if (settings.materialMode === 'toon') {
      return <meshToonMaterial {...commonProps} />
    }

    if (settings.materialMode === 'normal') {
      return <meshNormalMaterial wireframe={settings.wireframe} />
    }

    return <meshStandardMaterial {...commonProps} metalness={0.25} roughness={0.35} />
  }, [settings.materialMode, settings.objectColor, settings.wireframe])

  useFrame((_, delta) => {
    if (!meshRef.current || !settings.autoRotate) {
      return
    }

    meshRef.current.rotation.y += delta * 0.9
    meshRef.current.rotation.x += delta * 0.35
  })

  return (
    <mesh ref={meshRef} castShadow receiveShadow scale={settings.objectScale}>
      {geometry}
      {material}
    </mesh>
  )
}

function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.35, 0]} receiveShadow>
      <circleGeometry args={[10, 80]} />
      <meshStandardMaterial color="#141414" roughness={0.9} metalness={0.1} />
    </mesh>
  )
}

export default function SceneViewer({ settings }) {
  return (
    <Canvas camera={{ position: [5.5, 4, 5.5], fov: 48 }} shadows style={{ background: '#101010' }}>
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[5, 7, 4]}
        intensity={settings.lightIntensity}
        color={new THREE.Color(settings.lightColor)}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <pointLight position={[-5, 1, -4]} intensity={0.2} color={new THREE.Color(settings.lightColor)} />

      <ObjectMesh settings={settings} />
      <Ground />

      <gridHelper args={[20, 20, '#2d2d2d', '#1d1d1d']} />
      <axesHelper args={[3]} />
      <OrbitControls enableDamping dampingFactor={0.08} rotateSpeed={0.7} zoomSpeed={0.85} />
    </Canvas>
  )
}
