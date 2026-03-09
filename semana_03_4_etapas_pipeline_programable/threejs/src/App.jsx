import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import { useRef } from "react"
import * as THREE from "three"

function WavePlane(){

  const materialRef = useRef()

  const uniforms = {
    time: { value: 0 },
    resolution: { value: new THREE.Vector2(window.innerWidth,window.innerHeight) }
  }

  useFrame(({clock})=>{
    materialRef.current.uniforms.time.value = clock.getElapsedTime()
  })

  const vertexShader = `
  uniform float time;

  varying vec2 vUv;
  varying vec3 vNormal;

  void main(){

      vUv = uv;
      vNormal = normal;

      vec3 pos = position;

      pos.z += sin(pos.x * 5.0 + time) * 0.1;

      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos,1.0);
  }
  `

  const fragmentShader = `
  uniform float time;

  varying vec2 vUv;
  varying vec3 vNormal;

  void main(){

      vec3 normal = normalize(vNormal);

      vec3 color = vec3(vUv,0.5);

      float light = dot(normal,vec3(0.0,0.0,1.0))*0.5+0.5;

      float rim = 1.0 - max(dot(normal,vec3(0,0,1)),0.0);
      rim = pow(rim,2.0);

      float fresnel = pow(1.0 - dot(normal,vec3(0,0,1)),3.0);

      color *= light;
      color += rim * 0.3;
      color += fresnel * 0.2;

      gl_FragColor = vec4(color,1.0);
  }
  `

  return(
    <mesh>
      <planeGeometry args={[2,2,100,100]}/>
      <shaderMaterial
        ref={materialRef}
        uniforms={uniforms}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}

export default function App(){

  return(
    <Canvas style={{height:"100vh",width:"100vw"}} camera={{position:[0,0,2]}}>
      <ambientLight/>
      <WavePlane/>
      <OrbitControls/>
    </Canvas>
  )
}