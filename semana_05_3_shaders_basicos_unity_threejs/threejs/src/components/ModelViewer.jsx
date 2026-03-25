import { useEffect, useState, useMemo } from 'react'
import { Canvas, useLoader } from '@react-three/fiber'
import { OrbitControls, useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader'

// Component to render the 3D model with different visualization modes
function Model({ url, format, viewMode, onModelLoad }) {
  // Load model based on format
  let scene = null
  
  if (format === 'gltf') {
    const gltf = useGLTF(url)
    scene = gltf.scene
  } else if (format === 'obj') {
    const obj = useLoader(OBJLoader, url)
    scene = obj
  } else if (format === 'stl') {
    const geometry = useLoader(STLLoader, url)
    // STL loader returns geometry, so we need to create a mesh
    const material = new THREE.MeshStandardMaterial({ color: '#808080', metalness: 0.5, roughness: 0.5 })
    const mesh = new THREE.Mesh(geometry, material)
    scene = new THREE.Group()
    scene.add(mesh)
  }
  const [scaleValue, setScaleValue] = useState(1)

  // Calculate scale only once when scene loads
  useEffect(() => {
    if (scene) {
      // Calculate bounding box from original scene
      const box = new THREE.Box3().setFromObject(scene)
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      
      // Scale model to fit approximately 8 units
      const targetSize = 8
      const calculatedScale = maxDim > 0 ? targetSize / maxDim : 1
      setScaleValue(calculatedScale)
      
      // Calculate statistics
      let totalVertices = 0
      let totalFaces = 0

      scene.traverse((child) => {
        if (child.isMesh && child.geometry) {
          const geometry = child.geometry
          if (geometry.attributes.position) {
            totalVertices += geometry.attributes.position.count
          }
          
          if (geometry.index) {
            totalFaces += geometry.index.count / 3
          } else {
            totalFaces += geometry.attributes.position.count / 3
          }
        }
      })

      const totalEdges = totalFaces * 3 / 2
      onModelLoad({
        vertices: totalVertices,
        faces: Math.floor(totalFaces),
        edges: Math.floor(totalEdges)
      })
    }
  }, [scene, onModelLoad])

  // Create a new scene clone with appropriate materials and transformations for current viewMode
  const processedScene = useMemo(() => {
    if (!scene) return null
    
    const sceneClone = scene.clone(true)
    
    // First apply scale
    sceneClone.scale.set(scaleValue, scaleValue, scaleValue)
    
    // Then calculate bounding box AFTER scaling to get correct position
    sceneClone.updateMatrixWorld(true)
    const scaledBox = new THREE.Box3().setFromObject(sceneClone)
    const scaledCenter = scaledBox.getCenter(new THREE.Vector3())
    const scaledMinY = scaledBox.min.y
    
    // Now position it: bottom at Y=0, centered on X and Z
    sceneClone.position.set(
      -scaledCenter.x,
      -scaledMinY,
      -scaledCenter.z
    )
    
    sceneClone.traverse((child) => {
      if (child.isMesh) {
        // Store original material if not already stored
        if (!child.userData.originalMaterial) {
          child.userData.originalMaterial = child.material.clone()
        }
        
        if (viewMode === 'faces') {
          // Use original material
          child.material = child.userData.originalMaterial.clone()
          child.visible = true
        } else if (viewMode === 'wireframe') {
          // Wireframe material
          child.material = new THREE.MeshBasicMaterial({
            color: '#00ff00',
            wireframe: true
          })
          child.visible = true
        } else if (viewMode === 'vertices') {
          // Hide meshes in vertices mode
          child.visible = false
        }
      }
    })
    
    return sceneClone
  }, [scene, viewMode, scaleValue])

  // Create points for vertices mode, preserving hierarchy
  const verticesScene = useMemo(() => {
    if (!scene || viewMode !== 'vertices') return null
    
    const sceneClone = scene.clone(true)
    
    // First apply scale
    sceneClone.scale.set(scaleValue, scaleValue, scaleValue)
    
    // Then calculate bounding box AFTER scaling to get correct position
    sceneClone.updateMatrixWorld(true)
    const scaledBox = new THREE.Box3().setFromObject(sceneClone)
    const scaledCenter = scaledBox.getCenter(new THREE.Vector3())
    const scaledMinY = scaledBox.min.y
    
    // Now position it: bottom at Y=0, centered on X and Z
    sceneClone.position.set(
      -scaledCenter.x,
      -scaledMinY,
      -scaledCenter.z
    )
    
    sceneClone.traverse((child) => {
      if (child.isMesh && child.geometry) {
        // Hide the mesh
        child.visible = false
        
        // Create points object in the same position
        const points = new THREE.Points(
          child.geometry,
          new THREE.PointsMaterial({
            color: '#ff0000',
            size: 0.1,
            sizeAttenuation: true
          })
        )
        
        // Add points as sibling to mesh (within same parent)
        if (child.parent) {
          child.parent.add(points)
        }
      }
    })
    
    return sceneClone
  }, [scene, viewMode, scaleValue])

  if (!processedScene) return null

  return (
    <>
      {/* Render the scene with faces or wireframe */}
      {viewMode !== 'vertices' && <primitive object={processedScene} />}
      
      {/* Render vertices mode scene */}
      {viewMode === 'vertices' && verticesScene && <primitive object={verticesScene} />}
    </>
  )
}

// Main ModelViewer component
export default function ModelViewer({ modelPath, format, viewMode, onModelLoad }) {
  if (!modelPath) {
    return (
      <Canvas
        camera={{ position: [5, 5, 5], fov: 50 }}
        style={{ background: '#1a1a1a' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          rotateSpeed={0.5}
          zoomSpeed={0.8}
        />
        
        <gridHelper args={[20, 20]} />
        <axesHelper args={[10]} />
      </Canvas>
    )
  }

  return (
    <Canvas
      camera={{ position: [5, 5, 5], fov: 50 }}
      style={{ background: '#1a1a1a' }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -5]} intensity={0.5} />
      
      <Model url={modelPath} format={format} viewMode={viewMode} onModelLoad={onModelLoad} />
      
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        rotateSpeed={0.5}
        zoomSpeed={0.8}
      />
      
      <gridHelper args={[20, 20]} />
      <axesHelper args={[10]} />
    </Canvas>
  )
}
