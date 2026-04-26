import { useState } from "react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import ParametricScene from "./components/ParametricScene"

export default function App() {
  const [globalScale,    setGlobalScale]    = useState(1)
  const [animate,        setAnimate]        = useState(false)
  const [showBoxes,      setShowBoxes]      = useState(true)
  const [showSpheres,    setShowSpheres]    = useState(true)
  const [showCylinders,  setShowCylinders]  = useState(true)

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#111", position: "relative" }}>

      <div style={{
        position: "absolute", top: 16, left: 16, zIndex: 10,
        background: "rgba(0,0,0,0.75)", color: "#fff",
        padding: "16px", borderRadius: "8px", minWidth: "200px",
        fontFamily: "monospace", fontSize: "13px"
      }}>
        <div style={{ marginBottom: 12, fontWeight: "bold", color: "#aef" }}>
          Escena Paramétrica
        </div>

        <label>Escala global: {globalScale.toFixed(2)}</label>
        <input type="range" min="0.1" max="3" step="0.05"
          value={globalScale}
          onChange={e => setGlobalScale(Number(e.target.value))}
          style={{ width: "100%", marginBottom: 10 }}
        />

        <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <input type="checkbox" checked={animate}
            onChange={e => setAnimate(e.target.checked)} />
          Animar rotación
        </label>

        <div style={{ marginTop: 8, color: "#aaa", marginBottom: 4 }}>Filtros</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <input type="checkbox" checked={showBoxes}
            onChange={e => setShowBoxes(e.target.checked)} />
          Cubos
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <input type="checkbox" checked={showSpheres}
            onChange={e => setShowSpheres(e.target.checked)} />
          Esferas
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input type="checkbox" checked={showCylinders}
            onChange={e => setShowCylinders(e.target.checked)} />
          Cilindros
        </label>
      </div>

      <Canvas camera={{ position: [8, 6, 12], fov: 50 }}>
        <ParametricScene
          globalScale={globalScale}
          animate={animate}
          showBoxes={showBoxes}
          showSpheres={showSpheres}
          showCylinders={showCylinders}
        />
        <OrbitControls />
      </Canvas>
    </div>
  )
}