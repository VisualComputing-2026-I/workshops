import { useState } from 'react'
import { Html } from '@react-three/drei'
import { useControls } from 'leva'
import './ControlsUI.css'

export default function ControlsUI({ 
  playerPos, 
  actionState, 
  moveSpeed, 
  setMoveSpeed, 
  lookSpeed, 
  setLookSpeed,
  onReset 
}) {
  const [showHelp, setShowHelp] = useState(true)

  // Panel de Leva para Sliders y Botones
  const controls = useControls(() => ({
    'Velocidad Mover': {
      value: moveSpeed,
      min: 1,
      max: 20,
      step: 0.5,
      onChange: setMoveSpeed
    },
    'Velocidad Rotación': {
      value: lookSpeed,
      min: 0.5,
      max: 15,
      step: 0.5,
      onChange: setLookSpeed
    },
    'Reset Posición': false,
    'Mostrar Help': showHelp
  }))

  // Detectar cambios en los controles
  if (controls['Reset Posición']) {
    onReset()
    controls['Reset Posición'] = false
  }
  if (controls['Mostrar Help'] !== showHelp) {
    setShowHelp(controls['Mostrar Help'])
  }

  return (
    <>
      {/* Panel Informativo en HTML (Overlay) */}
      <Html fullScreen>
        <div className="ui-container">
          {showHelp && (
            <div className="help-panel">
              <h2>TALLER 6.1: Input & UI (Three.js + React)</h2>
              <div className="help-content">
                <div className="control-group">
                  <h3>Controles 3D:</h3>
                  <p>• <strong>WASD / Flechas:</strong> Mover Jugador</p>
                  <p>• <strong>Mouse (Rueda/Drag):</strong> Orbitar Cámara</p>
                  <p>• <strong>Click izquierdo:</strong> Interactuar con Cubo</p>
                  <p>• <strong>Tecla R:</strong> Resetear Posición</p>
                </div>
                
                <div className="status-info">
                  <p><strong>Posición:</strong> ({playerPos[0].toFixed(1)}, {playerPos[1].toFixed(1)}, {playerPos[2].toFixed(1)})</p>
                  <p><strong>Estado:</strong> {actionState}</p>
                </div>
              </div>
            </div>
          )}

          {/* Panel de Botones HTML */}
          <div className="button-panel">
            <button onClick={onReset} className="reset-btn">
              Resetear (R)
            </button>
            <button 
              onClick={() => setShowHelp(!showHelp)}
              className="help-btn"
            >
              {showHelp ? 'Ocultar' : 'Mostrar'} Help
            </button>
          </div>

          {/* Información de Sliders en Tiempo Real */}
          <div className="slider-display">
            <div>Mover Speed: {moveSpeed.toFixed(1)}</div>
            <div>Look Speed: {lookSpeed.toFixed(1)}</div>
          </div>
        </div>
      </Html>
    </>
  )
}
