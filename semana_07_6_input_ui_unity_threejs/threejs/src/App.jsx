import { Canvas } from '@react-three/fiber'
import { Suspense, useState } from 'react'
import Scene from './Scene'
import './App.css'

export default function App() {
  return (
    <div className="app-container">
      <Canvas
        camera={{ position: [0, 2, 5], fov: 75 }}
        style={{ width: '100%', height: '100%' }}
      >
        <color attach="background" args={['#1a1a2e']} />
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
    </div>
  )
}
