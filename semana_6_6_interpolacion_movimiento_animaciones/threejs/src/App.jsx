import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Grid, Line, OrbitControls } from '@react-three/drei'
import { Leva, useControls } from 'leva'
import * as THREE from 'three'

const START_POINT = new THREE.Vector3(-3, 0.5, -1.25)
const END_POINT = new THREE.Vector3(3, 1.8, 1.5)
const CONTROL_POINT = new THREE.Vector3(0, 3.8, -0.2)

const STRAIGHT_POINTS = [START_POINT.clone(), END_POINT.clone()]
const GUIDE_POINTS = [
  START_POINT.clone(),
  CONTROL_POINT.clone(),
  END_POINT.clone(),
]

const BEZIER_CURVE = new THREE.QuadraticBezierCurve3(
  START_POINT.clone(),
  CONTROL_POINT.clone(),
  END_POINT.clone(),
)
const CURVE_POINTS = BEZIER_CURVE.getPoints(60)

const START_QUATERNION = new THREE.Quaternion().setFromEuler(
  new THREE.Euler(0, 0, 0),
)
const END_QUATERNION = new THREE.Quaternion().setFromEuler(
  new THREE.Euler(Math.PI * 0.6, Math.PI * 1.15, Math.PI * 0.35),
)

function PointMarker({ position, color, scale = 1 }) {
  return (
    <mesh position={position} scale={scale} castShadow receiveShadow>
      <sphereGeometry args={[0.14, 32, 32]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.35} />
    </mesh>
  )
}

function LinearBox({ t }) {
  const meshRef = useRef(null)

  useFrame(() => {
    if (!meshRef.current) {
      return
    }

    meshRef.current.position.lerpVectors(START_POINT, END_POINT, t)
    meshRef.current.quaternion.copy(START_QUATERNION).slerp(END_QUATERNION, t)
  })

  return (
    <mesh ref={meshRef} castShadow receiveShadow>
      <boxGeometry args={[0.5, 0.5, 0.5]} />
      <meshStandardMaterial color="#ef4444" metalness={0.1} roughness={0.35} />
    </mesh>
  )
}

function CurvedBox({ t }) {
  const meshRef = useRef(null)
  const curvePoint = useRef(new THREE.Vector3())

  useFrame(() => {
    if (!meshRef.current) {
      return
    }

    BEZIER_CURVE.getPoint(t, curvePoint.current)
    meshRef.current.position.copy(curvePoint.current)
    meshRef.current.quaternion.copy(START_QUATERNION).slerp(END_QUATERNION, t)
  })

  return (
    <mesh ref={meshRef} castShadow receiveShadow>
      <boxGeometry args={[0.48, 0.48, 0.48]} />
      <meshStandardMaterial color="#0ea5e9" metalness={0.15} roughness={0.25} />
    </mesh>
  )
}

function Scene({ t }) {
  return (
    <>
      <color attach="background" args={['#f6efe6']} />
      <fog attach="fog" args={['#f6efe6', 9, 18]} />

      <ambientLight intensity={0.9} />
      <directionalLight
        castShadow
        intensity={2.4}
        position={[5, 8, 4]}
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />

      <Grid
        args={[18, 18]}
        cellColor="#c7b9a7"
        cellSize={0.7}
        fadeDistance={32}
        fadeStrength={1.2}
        infiniteGrid
        position={[0, -0.001, 0]}
        sectionColor="#7f6651"
        sectionSize={3.5}
      />

      <axesHelper args={[2.5]} />

      <Line color="#ef4444" lineWidth={3} points={STRAIGHT_POINTS} />
      <Line color="#0ea5e9" lineWidth={3} points={CURVE_POINTS} />
      <Line color="#94a3b8" dashed dashScale={1.4} gapSize={0.35} lineWidth={1.5} points={GUIDE_POINTS} />

      <PointMarker color="#15803d" position={START_POINT} scale={1.15} />
      <PointMarker color="#ca8a04" position={END_POINT} scale={1.15} />
      <PointMarker color="#64748b" position={CONTROL_POINT} scale={0.85} />

      <LinearBox t={t} />
      <CurvedBox t={t} />

      <mesh position={[0, -0.03, 0]} receiveShadow rotation-x={-Math.PI / 2}>
        <planeGeometry args={[28, 28]} />
        <shadowMaterial opacity={0.18} />
      </mesh>

      <OrbitControls enableDamping makeDefault />
    </>
  )
}

export default function App() {
  const { t } = useControls('Interpolacion', {
    t: {
      value: 0.35,
      min: 0,
      max: 1,
      step: 0.01,
    },
  })

  return (
    <div className="app-shell">
      <header className="panel">
        <p className="eyebrow">React Three Fiber + Three.js</p>
        <h1>Interpolacion lineal vs curva Bezier</h1>
        <p className="description">
          La caja roja recorre el trayecto lineal con <code>lerpVectors()</code>.
          La caja azul sigue la curva con <code>QuadraticBezierCurve3</code>.
          Ambas interpolan la rotacion con <code>Quaternion.slerp()</code> en cada frame.
        </p>
      </header>

      <main className="canvas-card">
        <Canvas camera={{ position: [6, 5, 7], fov: 45 }} shadows>
          <Scene t={t} />
        </Canvas>
      </main>

      <footer className="legend">
        <span><i className="swatch swatch-red" /> Lineal</span>
        <span><i className="swatch swatch-blue" /> Curva Bezier</span>
        <span><i className="swatch swatch-green" /> Inicio</span>
        <span><i className="swatch swatch-gold" /> Fin</span>
      </footer>

      <Leva collapsed={false} oneLineLabels />
    </div>
  )
}
