import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Leva, useControls } from 'leva'

function App() {
  const controls = useControls('Luces', {
    ambientIntensity: {
      value: 0.35,
      min: 0,
      max: 2,
      step: 0.05,
      label: 'Ambient intensity',
    },
    pointIntensity: {
      value: 80,
      min: 0,
      max: 180,
      step: 1,
      label: 'Point intensity',
    },
    pointColor: {
      value: '#ff9f68',
      label: 'Point color',
    },
    pointX: {
      value: 3.5,
      min: -8,
      max: 8,
      step: 0.1,
      label: 'Point X',
    },
    pointY: {
      value: 5.5,
      min: 0,
      max: 10,
      step: 0.1,
      label: 'Point Y',
    },
    pointZ: {
      value: 2.5,
      min: -8,
      max: 8,
      step: 0.1,
      label: 'Point Z',
    },
    directionalIntensity: {
      value: 2.2,
      min: 0,
      max: 6,
      step: 0.1,
      label: 'Directional intensity',
    },
    directionalColor: {
      value: '#d9ecff',
      label: 'Directional color',
    },
    directionalX: {
      value: -4.5,
      min: -10,
      max: 10,
      step: 0.1,
      label: 'Directional X',
    },
    directionalY: {
      value: 6,
      min: 0,
      max: 12,
      step: 0.1,
      label: 'Directional Y',
    },
    directionalZ: {
      value: 3.5,
      min: -10,
      max: 10,
      step: 0.1,
      label: 'Directional Z',
    },
  })

  const scene = useControls('Escena', {
    motionSpeed: {
      value: 1,
      min: 0,
      max: 3,
      step: 0.05,
      label: 'Motion speed',
    },
    orbitAutoRotate: {
      value: false,
      label: 'Auto rotate camera',
    },
  })

  return (
    <div className="app-shell">
      <Leva collapsed={false} oneLineLabels />
      <div className="hud">
        <p className="eyebrow">Computacion Visual</p>
        <h1>Luces, sombras y materiales fisicos</h1>
        <p>
          La escena combina <code>ambientLight</code>, <code>pointLight</code> y{' '}
          <code>directionalLight</code>. Los objetos se animan para mostrar como
          cambian las sombras y los reflejos en tiempo real.
        </p>
      </div>

      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [8, 6, 10], fov: 45 }}
      >
        <color attach="background" args={['#09111f']} />
        <fog attach="fog" args={['#09111f', 12, 28]} />

        <Scene controls={controls} scene={scene} />
      </Canvas>
    </div>
  )
}

function Scene({ controls, scene }) {
  return (
    <>
      <ambientLight intensity={controls.ambientIntensity} />

      <pointLight
        castShadow
        color={controls.pointColor}
        intensity={controls.pointIntensity}
        position={[controls.pointX, controls.pointY, controls.pointZ]}
        shadow-bias={-0.0005}
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />

      <directionalLight
        castShadow
        color={controls.directionalColor}
        intensity={controls.directionalIntensity}
        position={[
          controls.directionalX,
          controls.directionalY,
          controls.directionalZ,
        ]}
        shadow-bias={-0.00015}
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={30}
        shadow-camera-left={-10}
        shadow-camera-right={10}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}
      />

      <Ground />
      <AnimatedObjects motionSpeed={scene.motionSpeed} />

      <mesh position={[controls.pointX, controls.pointY, controls.pointZ]}>
        <sphereGeometry args={[0.18, 24, 24]} />
        <meshBasicMaterial color={controls.pointColor} />
      </mesh>

      <OrbitControls
        autoRotate={scene.orbitAutoRotate}
        autoRotateSpeed={1.5}
        enableDamping
      />
    </>
  )
}

function Ground() {
  return (
    <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.75, 0]}>
      <planeGeometry args={[30, 30]} />
      <meshStandardMaterial color="#111827" roughness={0.92} metalness={0.08} />
    </mesh>
  )
}

function AnimatedObjects({ motionSpeed }) {
  const sphereRef = useRef(null)
  const boxRef = useRef(null)
  const knotRef = useRef(null)
  const cylinderRef = useRef(null)

  useFrame((state, delta) => {
    const elapsed = state.clock.getElapsedTime() * motionSpeed

    if (sphereRef.current) {
      sphereRef.current.position.x = Math.sin(elapsed) * 2.4
      sphereRef.current.position.y = 0.95 + Math.abs(Math.cos(elapsed * 1.2)) * 1.2
      sphereRef.current.position.z = Math.cos(elapsed * 0.7) * 1.3
      sphereRef.current.rotation.y += delta * 0.8
    }

    if (boxRef.current) {
      boxRef.current.rotation.x += delta * 0.45 * motionSpeed
      boxRef.current.rotation.y += delta * 0.7 * motionSpeed
      boxRef.current.position.z = -2.2 + Math.sin(elapsed * 0.8) * 0.9
    }

    if (knotRef.current) {
      knotRef.current.rotation.x += delta * 0.35 * motionSpeed
      knotRef.current.rotation.y -= delta * 0.6 * motionSpeed
      knotRef.current.position.x = 2.7 + Math.cos(elapsed * 0.9) * 0.55
      knotRef.current.position.y = 1.15 + Math.sin(elapsed * 1.4) * 0.35
    }

    if (cylinderRef.current) {
      cylinderRef.current.rotation.y -= delta * 0.55 * motionSpeed
      cylinderRef.current.position.x = -3 + Math.cos(elapsed * 0.6) * 0.75
      cylinderRef.current.position.y = 0.6 + Math.abs(Math.sin(elapsed * 1.1)) * 0.5
    }
  })

  return (
    <>
      <mesh ref={sphereRef} castShadow position={[0, 1.2, 0]}>
        <sphereGeometry args={[0.85, 48, 48]} />
        <meshStandardMaterial color="#4fd1c5" roughness={0.25} metalness={0.35} />
      </mesh>

      <mesh ref={boxRef} castShadow position={[-2.4, 0.4, -2.2]}>
        <boxGeometry args={[1.35, 1.35, 1.35]} />
        <meshStandardMaterial color="#f97316" roughness={0.45} metalness={0.6} />
      </mesh>

      <mesh ref={knotRef} castShadow position={[2.7, 1.2, 1.4]}>
        <torusKnotGeometry args={[0.75, 0.24, 180, 24]} />
        <meshPhysicalMaterial
          color="#c4b5fd"
          roughness={0.18}
          metalness={0.55}
          clearcoat={1}
          clearcoatRoughness={0.12}
          reflectivity={1}
        />
      </mesh>

      <mesh ref={cylinderRef} castShadow position={[-3, 0.8, 2.3]}>
        <cylinderGeometry args={[0.65, 0.95, 1.8, 32]} />
        <meshPhysicalMaterial
          color="#fde68a"
          roughness={0.38}
          metalness={0.15}
          clearcoat={0.7}
          clearcoatRoughness={0.2}
        />
      </mesh>
    </>
  )
}

export default App
