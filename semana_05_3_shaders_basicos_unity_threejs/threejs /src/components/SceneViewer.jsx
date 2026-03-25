import { useEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

const vertexShader = `
  uniform float uTime;
  uniform float uWaveFrequency;
  uniform float uWaveAmplitude;

  varying vec3 vPosition;
  varying vec3 vNormal;

  void main() {
    vec3 pos = position;
    float wave = sin(pos.x * uWaveFrequency + uTime) * uWaveAmplitude;
    wave += sin(pos.y * (uWaveFrequency * 0.7) + uTime * 1.2) * (uWaveAmplitude * 0.6);
    wave += sin(pos.z * (uWaveFrequency * 0.45) + uTime * 0.9) * (uWaveAmplitude * 0.4);

    pos += normal * wave;

    vPosition = pos;
    vNormal = normalize(normalMatrix * normal);

    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`

const fragmentShader = `
  precision highp float;

  uniform vec3 uTopColor;
  uniform vec3 uBottomColor;
  uniform float uGradientHeight;
  uniform float uTime;
  uniform float uUseToon;
  uniform float uToonSteps;
  uniform float uFresnelStrength;

  varying vec3 vPosition;
  varying vec3 vNormal;

  void main() {
    float gradient = clamp((vPosition.y + uGradientHeight * 0.5) / uGradientHeight, 0.0, 1.0);
    float pulse = 0.55 + 0.45 * sin(uTime * 1.3 + vPosition.y * 0.5);

    vec3 base = mix(uBottomColor, uTopColor, gradient);
    base = mix(base, base * 1.2, pulse);

    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(vec3(0.35, 0.8, 0.45));
    float diffuse = clamp(dot(normal, lightDir), 0.0, 1.0);

    if (uUseToon > 0.5) {
      float steps = max(uToonSteps, 1.0);
      diffuse = floor(diffuse * steps) / steps;
    }

    float rim = pow(1.0 - dot(normal, normalize(vec3(0.0, 0.0, 1.0))), 3.0);

    vec3 color = base * (0.35 + 0.75 * diffuse);
    color += rim * uFresnelStrength;

    gl_FragColor = vec4(color, 1.0);
  }
`

function ShaderBall({ settings }) {
  const materialRef = useRef()

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uTopColor: { value: new THREE.Color(settings.topColor) },
      uBottomColor: { value: new THREE.Color(settings.bottomColor) },
      uGradientHeight: { value: settings.gradientHeight },
      uWaveFrequency: { value: settings.waveFrequency },
      uWaveAmplitude: { value: settings.waveAmplitude },
      uUseToon: { value: settings.useToon ? 1 : 0 },
      uToonSteps: { value: settings.toonSteps },
      uFresnelStrength: { value: settings.fresnelStrength },
    }),
    []
  )

  useFrame((_, delta) => {
    uniforms.uTime.value += delta * settings.animationSpeed
  })

  useEffect(() => {
    uniforms.uTopColor.value.set(settings.topColor)
    uniforms.uBottomColor.value.set(settings.bottomColor)
    uniforms.uGradientHeight.value = settings.gradientHeight
    uniforms.uWaveFrequency.value = settings.waveFrequency
    uniforms.uWaveAmplitude.value = settings.waveAmplitude
    uniforms.uUseToon.value = settings.useToon ? 1 : 0
    uniforms.uToonSteps.value = settings.toonSteps
    uniforms.uFresnelStrength.value = settings.fresnelStrength

    if (materialRef.current) {
      materialRef.current.wireframe = settings.wireframe
      materialRef.current.needsUpdate = true
    }
  }, [settings, uniforms])

  return (
    <mesh castShadow receiveShadow>
      <icosahedronGeometry args={[2, 48]} />
      <shaderMaterial
        ref={materialRef}
        uniforms={uniforms}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        side={THREE.DoubleSide}
        wireframe={settings.wireframe}
      />
    </mesh>
  )
}

function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2.2, 0]} receiveShadow>
      <circleGeometry args={[14, 64]} />
      <meshStandardMaterial color="#101010" roughness={0.9} metalness={0.1} />
    </mesh>
  )
}

export default function SceneViewer({ settings }) {
  return (
    <Canvas camera={{ position: [6.5, 4.5, 6.5], fov: 50 }} shadows style={{ background: '#0f0f0f' }}>
      <ambientLight intensity={0.35} />
      <directionalLight
        position={[6, 8, 6]}
        intensity={1.1}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <pointLight position={[-8, -6, -4]} intensity={0.25} />

      <ShaderBall settings={settings} />
      <Ground />

      <OrbitControls enableDamping dampingFactor={0.08} rotateSpeed={0.6} zoomSpeed={0.8} />
      <gridHelper args={[24, 24, '#1f1f1f', '#1f1f1f']} />
      <axesHelper args={[4]} />
    </Canvas>
  )
}
