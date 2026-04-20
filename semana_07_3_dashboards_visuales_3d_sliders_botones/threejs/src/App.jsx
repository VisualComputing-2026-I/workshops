import { useCallback, useState } from 'react'
import SceneViewer from './components/SceneViewer'
import Controls from './components/Controls'
import './App.css'

const defaultSettings = {
  objectType: 'box',
  objectScale: 1.5,
  objectColor: '#4a9eff',
  autoRotate: false,
  materialMode: 'standard',
  wireframe: false,
  lightIntensity: 1.15,
  lightColor: '#ffffff',
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
