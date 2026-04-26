import { useRef, useState, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Html, OrbitControls } from '@react-three/drei'
import Landscape from './Landscape'
import ControlsUI from './ControlsUI'

export default function Scene() {
  const playerRef = useRef(null)
  const cameraControlsRef = useRef(null)
  const [playerPos, setPlayerPos] = useState([0, 1, 0])
  const [cubeColor, setCubeColor] = useState('red')
  const [actionState, setActionState] = useState('Esperando interacción...')
  const [moveSpeed, setMoveSpeed] = useState(5)
  const [lookSpeed, setLookSpeed] = useState(3)
  
  const keysPressed = useRef({})
  const { camera } = useThree()

  // Detector de Teclado (WASD)
  useEffect(() => {
    const handleKeyDown = (e) => {
      keysPressed.current[e.key.toLowerCase()] = true
    }
    const handleKeyUp = (e) => {
      keysPressed.current[e.key.toLowerCase()] = false
    }
    
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [])

  // Detector de Reset (Tecla R)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === 'r') {
        setPlayerPos([0, 1, 0])
        setActionState('Posición reseteada (R)')
        if (cameraControlsRef.current) {
          camera.position.set(0, 2, 5)
          camera.lookAt(0, 1, 0)
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [camera])

  // Movimiento del Jugador (WASD)
  useFrame((state) => {
    if (!playerRef.current) return

    let moveX = 0
    let moveZ = 0

    // Capturar WASD e Input.GetKey directo
    if (keysPressed.current['w'] || keysPressed.current['arrowup']) moveZ -= 1
    if (keysPressed.current['s'] || keysPressed.current['arrowdown']) moveZ += 1
    if (keysPressed.current['d'] || keysPressed.current['arrowright']) moveX += 1
    if (keysPressed.current['a'] || keysPressed.current['arrowleft']) moveX -= 1

    if (moveX !== 0 || moveZ !== 0) {
      const speed = moveSpeed * state.clock.getDelta()
      setPlayerPos((prev) => [
        prev[0] + moveX * speed,
        prev[1],
        prev[2] + moveZ * speed,
      ])
    }
  })

  const handleCubeClick = () => {
    setActionState('¡Cubo clickeado!')
    setCubeColor([Math.random(), Math.random(), Math.random()])
  }

  const handleReset = () => {
    setPlayerPos([0, 1, 0])
    setActionState('Jugador reseteado desde UI')
    if (cameraControlsRef.current) {
      camera.position.set(0, 2, 5)
      camera.lookAt(0, 1, 0)
    }
  }

  return (
    <>
      {/* Iluminación */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 10]} intensity={0.8} castShadow />
      
      {/* Elementos del Mundo (Piso, Cubo, Jugador) */}
      <Landscape 
        playerPos={playerPos} 
        cubeColor={cubeColor} 
        onCubeClick={handleCubeClick}
        ref={playerRef}
      />

      {/* UI: Controles y Panel de Información */}
      <ControlsUI 
        playerPos={playerPos}
        actionState={actionState}
        moveSpeed={moveSpeed}
        setMoveSpeed={setMoveSpeed}
        lookSpeed={lookSpeed}
        setLookSpeed={setLookSpeed}
        onReset={handleReset}
      />

      {/* Texto Información Flotante */}
      <Html position={[0, 3, 0]} center>
        <div style={{
          fontSize: '14px',
          color: 'white',
          background: 'rgba(0,0,0,0.7)',
          padding: '10px 15px',
          borderRadius: '8px',
          whiteSpace: 'nowrap',
          fontFamily: 'monospace'
        }}>
          Pos: [{playerPos[0].toFixed(1)}, {playerPos[1].toFixed(1)}, {playerPos[2].toFixed(1)}]
        </div>
      </Html>

      {/* Camera Orbit Controls */}
      <OrbitControls 
        ref={cameraControlsRef}
        target={[playerPos[0], 1, playerPos[2]]}
        autoRotate={false}
        enableZoom={true}
        enablePan={true}
      />
    </>
  )
}
