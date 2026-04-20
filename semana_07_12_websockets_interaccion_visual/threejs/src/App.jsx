import { useEffect, useMemo, useState } from 'react'
import SceneViewer from './components/SceneViewer'
import './App.css'

const defaultData = {
  x: 0,
  y: 1,
  z: 0,
  color: '#40a9ff',
  pulse: 1,
  timestamp: 'waiting...'
}

export default function App() {
  const [data, setData] = useState(defaultData)
  const [status, setStatus] = useState('Connecting...')

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765')

    socket.onopen = () => {
      setStatus('Connected')
    }

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data)
        setData((previous) => ({ ...previous, ...parsed }))
      } catch {
        setStatus('Invalid JSON received')
      }
    }

    socket.onerror = () => {
      setStatus('Connection error')
    }

    socket.onclose = () => {
      setStatus('Disconnected')
    }

    return () => {
      socket.close()
    }
  }, [])

  const statusColor = useMemo(() => {
    if (status === 'Connected') {
      return '#73d13d'
    }

    if (status === 'Connecting...') {
      return '#ffd666'
    }

    return '#ff7875'
  }, [status])

  return (
    <main className="layout">
      <section className="panel">
        <p className="eyebrow">Workshop 58</p>
        <h1>WebSockets Visual Interaction</h1>
        <p className="description">
          Real-time data from a Python WebSocket server updates the position and color of a 3D object.
        </p>

        <div className="status-row">
          <span className="status-dot" style={{ background: statusColor }} />
          <span>{status}</span>
        </div>

        <div className="metrics">
          <div className="metric-item"><span>X</span><strong>{data.x.toFixed(3)}</strong></div>
          <div className="metric-item"><span>Y</span><strong>{data.y.toFixed(3)}</strong></div>
          <div className="metric-item"><span>Z</span><strong>{data.z.toFixed(3)}</strong></div>
          <div className="metric-item"><span>Pulse</span><strong>{data.pulse.toFixed(3)}</strong></div>
          <div className="metric-item"><span>Color</span><strong>{data.color}</strong></div>
        </div>

        <p className="timestamp">Last message: {data.timestamp}</p>
      </section>

      <section className="viewer">
        <SceneViewer data={data} />
      </section>
    </main>
  )
}
