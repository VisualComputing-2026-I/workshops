import { forwardRef } from 'react'
import { Mesh } from 'three'

const Landscape = forwardRef(({ playerPos, cubeColor, onCubeClick }, ref) => {
  return (
    <>
      {/* Piso */}
      <mesh position={[0, 0, 0]} rotation={[0, 0, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#2a5a3a" />
      </mesh>

      {/* Cubo Interactivo (Rojo) */}
      <mesh 
        position={[0, 0.5, 3]} 
        onClick={onCubeClick}
        ref={ref}
      >
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial 
          color={typeof cubeColor === 'string' ? cubeColor : cubeColor}
          emissive={typeof cubeColor === 'string' ? '#000000' : '#111111'}
        />
      </mesh>

      {/* Jugador (Representación Visual - Pequeño Cubo Azul) */}
      <mesh position={[playerPos[0], playerPos[1], playerPos[2]]}>
        <boxGeometry args={[0.5, 1.8, 0.5]} />
        <meshStandardMaterial color="#0066ff" />
      </mesh>

      {/* Punto de Luz al Jugador */}
      <pointLight 
        position={[playerPos[0], playerPos[1] + 1, playerPos[2]]} 
        intensity={0.4} 
        distance={10}
        color="#00aaff"
      />

      {/* Cubo Referencia Lejano */}
      <mesh position={[5, 0.5, 5]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#ff6600" />
      </mesh>

      {/* Esfera Referencia */}
      <mesh position={[-5, 1, -5]}>
        <sphereGeometry args={[0.7, 32, 32]} />
        <meshStandardMaterial color="#ff00ff" />
      </mesh>
    </>
  )
})

Landscape.displayName = 'Landscape'

export default Landscape
