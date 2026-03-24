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

  return (
    <div className="controls-container">
      <div className="controls-panel">
        <div className="controls-header">
          <div>
            <p className="eyebrow">Three.js — Custom Shaders</p>
            <h2>Shaders</h2>
            <p className="lede">Explore how a custom shader blends a vertical gradient, an animation driven by <code>uTime</code>, and a Fresnel rim. Toggle wireframe or toon shading to see light quantization.</p>
          </div>
        </div>

        <div className="control-section">
          <h3>Colors and Gradient</h3>
          <div className="field-row">
            <label>Bottom color</label>
            <input type="color" value={settings.bottomColor} onChange={handleColor('bottomColor')} />
          </div>
          <div className="field-row">
            <label>Top color</label>
            <input type="color" value={settings.topColor} onChange={handleColor('topColor')} />
          </div>
          <div className="field-row">
            <label>Gradient height</label>
            <input type="range" min="1" max="6" step="0.1" value={settings.gradientHeight} onChange={handleNumber('gradientHeight')} />
            <span className="value-pill">{settings.gradientHeight.toFixed(1)}</span>
          </div>
        </div>

        <div className="control-section">
          <h3>Animation</h3>
          <div className="field-row">
            <label>Speed</label>
            <input type="range" min="0" max="4" step="0.05" value={settings.animationSpeed} onChange={handleNumber('animationSpeed')} />
            <span className="value-pill">{settings.animationSpeed.toFixed(2)}x</span>
          </div>
          <div className="field-row">
            <label>Wave frequency</label>
            <input type="range" min="0" max="6" step="0.1" value={settings.waveFrequency} onChange={handleNumber('waveFrequency')} />
            <span className="value-pill">{settings.waveFrequency.toFixed(1)}</span>
          </div>
          <div className="field-row">
            <label>Wave amplitude</label>
            <input type="range" min="0" max="0.8" step="0.01" value={settings.waveAmplitude} onChange={handleNumber('waveAmplitude')} />
            <span className="value-pill">{settings.waveAmplitude.toFixed(2)}</span>
          </div>
        </div>

        <div className="control-section">
          <h3>Stylized shading</h3>
          <div className="field-row">
            <label>Toon shading</label>
            <input type="checkbox" checked={settings.useToon} onChange={handleToggle('useToon')} />
          </div>
          <div className="field-row">
            <label>Toon steps</label>
            <input type="range" min="2" max="8" step="1" value={settings.toonSteps} onChange={handleNumber('toonSteps')} disabled={!settings.useToon} />
            <span className="value-pill">{settings.toonSteps}</span>
          </div>
          <div className="field-row">
            <label>Wireframe</label>
            <input type="checkbox" checked={settings.wireframe} onChange={handleToggle('wireframe')} />
          </div>
          <div className="field-row">
            <label>Fresnel</label>
            <input type="range" min="0" max="1" step="0.05" value={settings.fresnelStrength} onChange={handleNumber('fresnelStrength')} />
            <span className="value-pill">{settings.fresnelStrength.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
