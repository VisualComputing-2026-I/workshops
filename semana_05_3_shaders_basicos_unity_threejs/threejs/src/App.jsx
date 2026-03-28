import { useCallback, useState } from 'react'
import SceneViewer from './components/SceneViewer'
import Controls from './components/Controls'
import './App.css'

const defaultSettings = {
  topColor: '#5fc4ff',
  bottomColor: '#ff7a8a',
  gradientHeight: 3.4,
  animationSpeed: 1.4,
  waveFrequency: 2.4,
  waveAmplitude: 0.25,
  useToon: true,
  toonSteps: 4,
  wireframe: false,
  fresnelStrength: 0.35,
}

function App() {
  const [settings, setSettings] = useState(defaultSettings)

  const handleChange = useCallback((key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }, [])

  return (
    <div className="app-container">
      <Controls settings={settings} onChange={handleChange} />
      <div className="viewer-container">
        <SceneViewer settings={settings} />
      </div>
    </div>
  )
}

export default App
