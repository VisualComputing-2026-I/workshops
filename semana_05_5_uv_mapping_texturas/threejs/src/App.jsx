import { useMemo, useState, useEffect } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls, Grid, Environment } from "@react-three/drei";
import { MeshStandardMaterial, TextureLoader, RepeatWrapping, MirroredRepeatWrapping, SRGBColorSpace, CanvasTexture } from "three";
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";

const PRESETS = {
  Default:    { repeatX: 1,   repeatY: 1,   offsetX: 0,    offsetY: 0,    rotation: 0 },
  Tiled:      { repeatX: 3,   repeatY: 3,   offsetX: 0,    offsetY: 0,    rotation: 0 },
  Offset:     { repeatX: 1,   repeatY: 1,   offsetX: 0.25, offsetY: 0.25, rotation: 0 },
  Rotated:    { repeatX: 1,   repeatY: 1,   offsetX: 0,    offsetY: 0,    rotation: 0.5 },
  Stretched:  { repeatX: 0.5, repeatY: 2,   offsetX: 0,    offsetY: 0,    rotation: 0 },
};

function makeCheckerTexture(size = 512, tiles = 8) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");
  const cell = size / tiles;
  for (let row = 0; row < tiles; row++) {
    for (let col = 0; col < tiles; col++) {
      ctx.fillStyle = (row + col) % 2 === 0 ? "#ffffff" : "#ff0080";
      ctx.fillRect(col * cell, row * cell, cell, cell);
    }
  }
  const tex = new CanvasTexture(canvas);
  tex.colorSpace = SRGBColorSpace;
  return tex;
}

function SpotModel({ useChecker, uvParams}) {
  const obj            = useLoader(OBJLoader, "/models/spot/spot.obj");
  const rawTexture     = useLoader(TextureLoader, "/models/spot/spot_texture.png");
  const checkerTexture = useMemo(() => makeCheckerTexture(), []);

  const texture = useChecker ? checkerTexture : rawTexture;
  const effectiveRepeatX = useChecker ? uvParams.repeatX : 1;
  const effectiveRepeatY = useChecker ? uvParams.repeatY : 1;
 
  texture.repeat.set(effectiveRepeatX, effectiveRepeatY);
  texture.offset.set(uvParams.offsetX, uvParams.offsetY);
  texture.rotation  = uvParams.rotation * Math.PI;
  texture.needsUpdate = true;

  useEffect(() => {
    obj.traverse((node) => {
      if (node.isMesh) {
        node.material = new MeshStandardMaterial({ map: texture });
      }
    });
  }, [obj, texture]);

  return <primitive object={obj} scale={2} position={[0, 0, 0]} />;
}

function Controls({ params, onChange, useChecker, onCheckerToggle, activePreset, onPreset }) {
  const slider = (label, key, min, max, step) => (
    <div style={styles.row}>
      <span style={styles.label}>{label}</span>
      <input
        type="range" min={min} max={max} step={step}
        value={params[key]}
        onChange={(e) => onChange(key, parseFloat(e.target.value))}
        style={styles.slider}
      />
      <span style={styles.val}>{params[key].toFixed(2)}</span>
    </div>
  );

  return (
    <div style={styles.panel}>
      <p style={styles.section}>Texturas</p>
      <div style={styles.row}>
        <button
          onClick={onCheckerToggle}
          style={{ ...styles.btn, ...(useChecker ? styles.btnActive : {}) }}
        >
          {useChecker ? "UV Checker" : "Spot original"}
        </button>
      </div>

      <p style={styles.section}>Presets UV</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {Object.keys(PRESETS).map((p) => (
          <button
            key={p}
            onClick={() => onPreset(p)}
            style={{ ...styles.btn, ...(activePreset === p ? styles.btnActive : {}), fontSize: 10 }}
          >
            {p}
          </button>
        ))}
      </div>

      <p style={styles.section}>UV Transformar</p>
      {slider("Repeat X",   "repeatX",   0.1, 5, 0.1)}
      {slider("Repeat Y",   "repeatY",   0.1, 5, 0.1)}
      {slider("Offset X",   "offsetX",   0,   1, 0.01)}
      {slider("Offset Y",   "offsetY",   0,   1, 0.01)}
      {slider("Rotation",   "rotation",  0,   2, 0.01)}
    </div>
  );
}

export default function UVMappingTaller() {
  const [uvParams, setUvParams]     = useState(PRESETS.Default);
  const [wrapMode, setWrapMode]     = useState("Repeat");
  const [useChecker, setUseChecker] = useState(false);
  const [activePreset, setPreset]   = useState("Default");

  const handleChange = (key, value) => {
    setUvParams((p) => ({ ...p, [key]: value }));
    setPreset(null);
  };

  const handlePreset = (name) => {
    setUvParams(PRESETS[name]);
    setPreset(name);
  };

  return (
    <div style={styles.root}>
      <Controls
        params={uvParams}
        onChange={handleChange}
        wrapMode={wrapMode}
        onWrapChange={setWrapMode}
        useChecker={useChecker}
        onCheckerToggle={() => setUseChecker((v) => !v)}
        activePreset={activePreset}
        onPreset={handlePreset}
      />

      <div style={styles.canvas}>
        <div style={styles.badge}>UV Mapping</div>
        <Canvas camera={{ position: [0, 2, 5], fov: 50 }} shadows>
          <ambientLight intensity={0.6} />
          <directionalLight position={[5, 8, 5]} intensity={1.2} castShadow />
          <SpotModel
            useChecker={useChecker}
            uvParams={uvParams}
            wrapMode={wrapMode}
          />
          <Grid
            position={[0, -1, 0]}
            args={[10, 10]}
            cellColor="#444"
            sectionColor="#666"
            fadeDistance={12}
          />
          <Environment preset="city" />
          <OrbitControls makeDefault />
        </Canvas>
      </div>
    </div>
  );
}

const styles = {
  root: {
    display: "flex",
    width: "100vw",
    height: "100vh",
    background: "#0e0e0e",
    fontFamily: "'JetBrains Mono', monospace",
    color: "#e0e0e0",
    overflow: "hidden",
  },
  panel: {
    width: 240,
    flexShrink: 0,
    background: "#161616",
    borderRight: "1px solid #2a2a2a",
    padding: "20px 16px",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  canvas: {
    flex: 1,
    position: "relative",
  },
  badge: {
    position: "absolute",
    top: 14,
    left: 14,
    zIndex: 10,
    fontSize: 11,
    letterSpacing: "0.08em",
    color: "#888",
    textTransform: "uppercase",
  },
  section: {
    fontSize: 9,
    letterSpacing: "0.12em",
    color: "#555",
    textTransform: "uppercase",
    margin: "12px 0 4px",
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    margin: "3px 0",
  },
  label: {
    fontSize: 10,
    width: 66,
    flexShrink: 0,
    color: "#aaa",
  },
  slider: {
    flex: 1,
    accentColor: "#6ee7b7",
    cursor: "pointer",
  },
  val: {
    fontSize: 10,
    width: 34,
    textAlign: "right",
    color: "#6ee7b7",
    fontFamily: "monospace",
  },
  btn: {
  padding: "5px 10px",
  fontSize: 11,
  background: "#222",
  color: "#aaa",
  borderWidth: "1px",
  borderStyle: "solid",
  borderColor: "#333",
  borderRadius: 4,
  cursor: "pointer",
  transition: "all 0.15s",
  },
  btnActive: {
    background: "#1a3a2a",
    color: "#6ee7b7",
    borderColor: "#6ee7b7",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 10,
    marginTop: 4,
  },
  td: {
    padding: "2px 4px",
    color: "#666",
    borderBottom: "1px solid #1f1f1f",
  },
};
