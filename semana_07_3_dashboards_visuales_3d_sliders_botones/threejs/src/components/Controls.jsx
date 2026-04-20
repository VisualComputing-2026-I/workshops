import './Controls.css'

export default function Controls({ settings, onChange }) {
  const handleNumber = (key) => (event) => {
    onChange(key, Number(event.target.value))
  }

  const handleToggle = (key) => (event) => {
    onChange(key, event.target.checked)
  }

  const handleColor = (key) => (event) => {
    onChange(key, event.target.value)
  }

  const cycleMaterial = () => {
    const modes = ['standard', 'toon', 'normal']
    const currentIndex = modes.indexOf(settings.materialMode)
    const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % modes.length
    onChange('materialMode', modes[nextIndex])
  }

  const setObjectType = (type) => {
    onChange('objectType', type)
  }

  return (
    <div className="controls-container">
      <div className="controls-panel">
        <div className="controls-header">
          <div>
            <p className="eyebrow">Three.js Dashboard Workshop</p>
            <h2>Scene Controls</h2>
            <p className="lede">Control a 3D scene in real time with sliders and buttons. Adjust scale, color, material style, and lighting while orbiting around the model.</p>
          </div>
        </div>

        <div className="control-section">
          <h3>Object</h3>
          <div className="button-group">
            <button
              className={settings.objectType === 'box' ? 'ghost-button is-active' : 'ghost-button'}
              onClick={() => setObjectType('box')}
              type="button"
            >
              Box
            </button>
            <button
              className={settings.objectType === 'sphere' ? 'ghost-button is-active' : 'ghost-button'}
              onClick={() => setObjectType('sphere')}
              type="button"
            >
              Sphere
            </button>
            <button
              className={settings.objectType === 'torus' ? 'ghost-button is-active' : 'ghost-button'}
              onClick={() => setObjectType('torus')}
              type="button"
            >
              Torus
            </button>
          </div>
          <div className="field-row">
            <label>Scale</label>
            <input type="range" min="0.5" max="3.5" step="0.05" value={settings.objectScale} onChange={handleNumber('objectScale')} />
            <span className="value-pill">{settings.objectScale.toFixed(2)}</span>
          </div>
          <div className="field-row">
            <label>Color</label>
            <input type="color" value={settings.objectColor} onChange={handleColor('objectColor')} />
          </div>
        </div>

        <div className="control-section">
          <h3>Animation and Material</h3>
          <div className="field-row">
            <label>Auto rotate</label>
            <input type="checkbox" checked={settings.autoRotate} onChange={handleToggle('autoRotate')} />
          </div>
          <div className="button-row">
            <button className="primary-button" onClick={cycleMaterial} type="button">
              Switch Material
            </button>
            <span className="value-pill text">{settings.materialMode}</span>
          </div>
          <div className="field-row">
            <label>Wireframe</label>
            <input type="checkbox" checked={settings.wireframe} onChange={handleToggle('wireframe')} />
          </div>
        </div>

        <div className="control-section">
          <h3>Light (Bonus)</h3>
          <div className="field-row">
            <label>Intensity</label>
            <input type="range" min="0.1" max="2.5" step="0.05" value={settings.lightIntensity} onChange={handleNumber('lightIntensity')} />
            <span className="value-pill">{settings.lightIntensity.toFixed(2)}</span>
          </div>
          <div className="field-row">
            <label>Color</label>
            <input type="color" value={settings.lightColor} onChange={handleColor('lightColor')} />
          </div>
        </div>
      </div>
    </div>
  )
}
