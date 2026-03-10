import { useRef, useEffect } from "react"
import * as THREE from "three"
import { VertexNormalsHelper } from "three/examples/jsm/helpers/VertexNormalsHelper"

import vertexShader from "../shaders/normalVertex.glsl"
import fragmentShader from "../shaders/normalFragment.glsl"

export default function ProceduralMesh(){

  const meshRef = useRef()

  useEffect(()=>{

    const geometry = meshRef.current.geometry

    const pos = geometry.attributes.position

    // deformación procedural
    for(let i=0;i<pos.count;i++){

      const x = pos.getX(i)
      const y = pos.getY(i)

      const z = Math.sin(x*2)*Math.cos(y*2)*0.2

      pos.setZ(i,z)

    }

    pos.needsUpdate = true

    // recalcular normales smooth
    geometry.computeVertexNormals()

    // visualizar normales
    const helper = new VertexNormalsHelper(meshRef.current,0.15,0xff0000)
    meshRef.current.add(helper)

  },[])

  return(
    <mesh ref={meshRef}>
      <planeGeometry args={[2,2,20,20]}/>
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
      />
    </mesh>
  )
}