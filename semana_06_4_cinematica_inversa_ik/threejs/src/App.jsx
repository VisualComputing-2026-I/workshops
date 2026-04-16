import { useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Line, OrbitControls } from "@react-three/drei";
import Arm from "./Arm.jsx";
import Target from "./Target.jsx";

const BASE_POSITION = [0, 0.5, 0];
const POSES = ["rest", "reach", "curl"];

export default function App() {
  const [target, setTarget] = useState([2.2, BASE_POSITION[1], 0]);
  const [mode, setMode] = useState("ik");
  const [pose, setPose] = useState(POSES[0]);
  const [autoPose, setAutoPose] = useState(false);
  const [stats, setStats] = useState({ distance: 0, iterations: 0 });
  const controlsRef = useRef();

  useEffect(() => {
    if (!autoPose) return;

    let index = POSES.indexOf(pose);
    const timer = setInterval(() => {
      index = (index + 1) % POSES.length;
      setPose(POSES[index]);
    }, 1400);

    return () => clearInterval(timer);
  }, [autoPose, pose]);

  return (
    <>
      <div className="hud">
        <div className="row">
          <button
            type="button"
            onClick={() => setMode(mode === "ik" ? "fk" : "ik")}
          >
            Modo: {mode.toUpperCase()}
          </button>
          <button type="button" onClick={() => setAutoPose(!autoPose)}>
            Auto pose: {autoPose ? "ON" : "OFF"}
          </button>
        </div>
        <div className="row">
          <label htmlFor="pose">Pose</label>
          <select
            id="pose"
            value={pose}
            onChange={(event) => setPose(event.target.value)}
            disabled={mode === "ik"}
          >
            {POSES.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <div className="row">Distancia restante: {stats.distance.toFixed(3)}</div>
        <div className="row">Iteraciones por frame: {stats.iterations}</div>
      </div>

      <Canvas camera={{ position: [4, 2.5, 4], fov: 50 }}>
        <color attach="background" args={["#070b10"]} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[3, 3, 2]} intensity={1.6} />
        <OrbitControls ref={controlsRef} enableDamping />

        <mesh position={[0, 2, -6]}>
          <planeGeometry args={[18, 10]} />
          <meshStandardMaterial color="#16202a" />
        </mesh>

        <Line points={[BASE_POSITION, target]} color="#f6c453" lineWidth={2} />

        <Arm
          target={target}
          mode={mode}
          pose={pose}
          basePosition={BASE_POSITION}
          onStats={(distance, iterations) =>
            setStats({ distance, iterations })
          }
        />

        <Target
          position={target}
          planeY={BASE_POSITION[1]}
          onChange={setTarget}
          onDragChange={(dragging) => {
            if (controlsRef.current) {
              controlsRef.current.enabled = !dragging;
            }
          }}
        />
      </Canvas>
    </>
  );
}
