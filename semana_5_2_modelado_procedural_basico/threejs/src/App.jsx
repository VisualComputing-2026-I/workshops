import { useEffect, useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, OrbitControls, Sky, Stars } from '@react-three/drei';
import * as THREE from 'three';

function RepeatedGrid() {
  const groupRef = useRef(null);
  const size = 7;
  const spacing = 1.75;

  const items = useMemo(() => {
    return Array.from({ length: size * size }, (_, index) => {
      const xIndex = index % size;
      const zIndex = Math.floor(index / size);
      const x = (xIndex - (size - 1) / 2) * spacing;
      const z = (zIndex - (size - 1) / 2) * spacing;
      const distance = Math.hypot(x, z);
      return {
        id: `${xIndex}-${zIndex}`,
        type: (xIndex + zIndex) % 2 === 0 ? 'box' : 'sphere',
        position: [x, 0.5 + Math.sin(distance * 0.55) * 0.25, z],
        color: new THREE.Color().setHSL(0.55 + distance * 0.015, 0.6, 0.5).getStyle(),
      };
    });
  }, []);

  useFrame((state) => {
    if (!groupRef.current) {
      return;
    }

    const time = state.clock.getElapsedTime();
    groupRef.current.rotation.y = time * 0.12;

    groupRef.current.children.forEach((child, index) => {
      child.position.y =
        items[index].position[1] +
        Math.sin(time * 1.8 + child.position.x * 0.5 + child.position.z * 0.5) * 0.35;
      child.rotation.x = time * 0.35;
      child.rotation.z = time * 0.18;
    });
  });

  return (
    <group ref={groupRef} position={[-10, 0, -2]}>
      {items.map((item) => (
        <mesh key={item.id} position={item.position} castShadow receiveShadow>
          {item.type === 'box' ? <boxGeometry args={[0.9, 0.9, 0.9]} /> : <sphereGeometry args={[0.52, 28, 28]} />}
          <meshStandardMaterial color={item.color} roughness={0.25} metalness={0.08} />
        </mesh>
      ))}
    </group>
  );
}

function SpiralStructures() {
  const groupRef = useRef(null);

  const points = useMemo(() => {
    return Array.from({ length: 44 }, (_, index) => {
      const angle = index * 0.48;
      const radius = 0.35 + index * 0.18;
      const y = index * 0.12;
      return {
        id: index,
        position: [Math.cos(angle) * radius, y, Math.sin(angle) * radius],
        scale: 0.22 + index * 0.015,
        hue: 0.04 + index * 0.012,
      };
    });
  }, []);

  useFrame((state) => {
    if (!groupRef.current) {
      return;
    }

    const time = state.clock.getElapsedTime();
    groupRef.current.rotation.y = -time * 0.24;

    groupRef.current.children.forEach((child, index) => {
      const pulse = 1 + Math.sin(time * 2.1 + index * 0.35) * 0.18;
      child.scale.setScalar(pulse);
      child.position.y = points[index].position[1] + Math.sin(time + index * 0.25) * 0.18;
    });
  });

  return (
    <group ref={groupRef} position={[0, 0.25, -1]}>
      {points.map((point) => (
        <mesh key={point.id} position={point.position} castShadow>
          <sphereGeometry args={[point.scale, 24, 24]} />
          <meshStandardMaterial
            color={new THREE.Color().setHSL(point.hue, 0.75, 0.58)}
            emissive={new THREE.Color().setHSL(point.hue, 0.5, 0.16)}
            roughness={0.35}
          />
        </mesh>
      ))}
    </group>
  );
}

function AnimatedSurface() {
  const meshRef = useRef(null);
  const basePositionsRef = useRef(null);

  useEffect(() => {
    if (!meshRef.current) {
      return;
    }

    const positions = meshRef.current.geometry.attributes.position.array;
    basePositionsRef.current = positions.slice();
  }, []);

  useFrame((state) => {
    if (!meshRef.current || !basePositionsRef.current) {
      return;
    }

    const geometry = meshRef.current.geometry;
    const positions = geometry.attributes.position.array;
    const basePositions = basePositionsRef.current;
    const time = state.clock.getElapsedTime();

    for (let index = 0; index < positions.length; index += 3) {
      const x = basePositions[index];
      const y = basePositions[index + 1];
      positions[index + 2] =
        Math.sin(x * 1.25 + time * 1.8) * 0.45 +
        Math.cos(y * 1.8 - time * 1.35) * 0.2 +
        Math.sin((x + y) * 0.9 + time * 0.85) * 0.15;
    }

    geometry.attributes.position.needsUpdate = true;
    geometry.computeVertexNormals();
    meshRef.current.rotation.z = Math.sin(time * 0.35) * 0.08;
  });

  return (
    <mesh ref={meshRef} position={[10, 1.25, 0]} rotation={[-Math.PI / 2.2, 0, 0]} receiveShadow castShadow>
      <planeGeometry args={[8, 8, 72, 72]} />
      <meshStandardMaterial color="#4fd1c5" wireframe={false} metalness={0.1} roughness={0.25} side={THREE.DoubleSide} />
    </mesh>
  );
}

function Branch({ depth, length, radius, tilt = 0.4 }) {
  if (depth <= 0) {
    return (
      <mesh position={[0, length, 0]} castShadow>
        <sphereGeometry args={[radius * 1.8, 16, 16]} />
        <meshStandardMaterial color="#8dcf68" roughness={0.8} />
      </mesh>
    );
  }

  const childLength = length * 0.76;
  const childRadius = Math.max(radius * 0.72, 0.04);
  const branchOffsets = [
    { rotation: [0.55, 0, tilt], color: '#8a5a44' },
    { rotation: [0.42, (Math.PI * 2) / 3, -tilt], color: '#8f6045' },
    { rotation: [0.48, (Math.PI * 4) / 3, tilt * 0.7], color: '#7f513d' },
  ];

  return (
    <group>
      <mesh position={[0, length / 2, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[radius * 0.75, radius, length, 10]} />
        <meshStandardMaterial color="#6e4632" roughness={0.9} />
      </mesh>

      <group position={[0, length, 0]}>
        {branchOffsets.map((branch, index) => (
          <group key={`${depth}-${index}`} rotation={branch.rotation}>
            <Branch depth={depth - 1} length={childLength} radius={childRadius} tilt={tilt * 0.92} />
          </group>
        ))}
      </group>
    </group>
  );
}

function FractalTree() {
  const treeRef = useRef(null);

  useFrame((state) => {
    if (!treeRef.current) {
      return;
    }

    const time = state.clock.getElapsedTime();
    treeRef.current.rotation.z = Math.sin(time * 0.7) * 0.04;
  });

  return (
    <Float speed={1.3} rotationIntensity={0.14} floatIntensity={0.22}>
      <group ref={treeRef} position={[0, -1.2, 8]}>
        <Branch depth={4} length={2.3} radius={0.28} />
      </group>
    </Float>
  );
}

function Ground() {
  return (
    <mesh position={[0, -1.55, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[60, 60, 1, 1]} />
      <meshStandardMaterial color="#182026" roughness={1} />
    </mesh>
  );
}

function Scene() {
  return (
    <>
      <color attach="background" args={['#08131d']} />
      <fog attach="fog" args={['#08131d', 18, 42]} />
      <ambientLight intensity={0.75} />
      <directionalLight
        position={[8, 14, 8]}
        intensity={1.8}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <pointLight position={[-12, 8, -6]} intensity={40} color="#66e3ff" distance={30} />
      <pointLight position={[12, 6, 10]} intensity={30} color="#ff8f6b" distance={25} />
      <Sky distance={450000} sunPosition={[3, 1, 4]} inclination={0.55} azimuth={0.2} />
      <Stars radius={120} depth={50} count={3000} factor={4} saturation={0} fade speed={0.3} />
      <Ground />
      <RepeatedGrid />
      <SpiralStructures />
      <AnimatedSurface />
      <FractalTree />
      <OrbitControls enableDamping maxPolarAngle={Math.PI / 1.85} minDistance={9} maxDistance={28} />
    </>
  );
}

function Overlay() {
  return (
    <div className="overlay">
      <div className="panel">
        <p className="eyebrow">React Three Fiber</p>
        <h1>Modelado procedural básico</h1>
        <p>
          Escena demostrativa con estructuras repetitivas, modificación directa de vértices, animación con
          <code> useFrame()</code> y árbol fractal recursivo.
        </p>
      </div>
      <div className="panel panel--small">
        <p>
          <strong>Izquierda:</strong> cuadrícula generada con <code>Array.map()</code> usando cajas y esferas.
        </p>
        <p>
          <strong>Centro:</strong> espiral de esferas con escala y altura animadas.
        </p>
        <p>
          <strong>Derecha:</strong> superficie cuya malla se deforma modificando
          <code> geometry.attributes.position.array</code>.
        </p>
        <p>
          <strong>Fondo:</strong> árbol fractal construido recursivamente con cilindros y hojas.
        </p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <Overlay />
      <Canvas shadows camera={{ position: [0, 6, 18], fov: 46 }}>
        <Scene />
      </Canvas>
    </div>
  );
}
