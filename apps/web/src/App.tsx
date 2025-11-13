import React, { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'

const token = import.meta.env.VITE_MAPBOX_TOKEN as string
mapboxgl.accessToken = token || ''
const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const mapContainer = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const [gps, setGps] = useState({ lat: 28.6139, lng: 77.2090 }) // Delhi
  const [apiToken, setApiToken] = useState<string>("")
  const [alerts, setAlerts] = useState<any[]>([])
  const [geojson, setGeojson] = useState<any>({ type: 'FeatureCollection', features: [] })
  const [inputLat, setInputLat] = useState<string>("28.6139")
  const [inputLng, setInputLng] = useState<string>("77.2090")
  const [email, setEmail] = useState<string>("")
  const [password, setPassword] = useState<string>("")
  const [filterStatus, setFilterStatus] = useState<string>("")
  const [filterRisk, setFilterRisk] = useState<string>("")
  const [offset, setOffset] = useState<number>(0)
  const [limit, setLimit] = useState<number>(20)
  const [autoAckDup, setAutoAckDup] = useState<boolean>(false)
  const [geofences, setGeofences] = useState<any[]>([])
  const [gfName, setGfName] = useState<string>("")
  const [gfRisk, setGfRisk] = useState<string>("low")
  const [gfCoords, setGfCoords] = useState<string>("[[77.2090,28.6139],[77.2190,28.6139],[77.2190,28.6239],[77.2090,28.6239],[77.2090,28.6139]]")

  useEffect(() => {
    // Load JWT from localStorage on first mount
    const saved = localStorage.getItem('jwt_token')
    if (saved) setApiToken(saved)
    if (!mapContainer.current || mapRef.current) return
    mapRef.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [gps.lng, gps.lat],
      zoom: 10
    })
    new mapboxgl.Marker().setLngLat([gps.lng, gps.lat]).addTo(mapRef.current)

    mapRef.current.on('load', () => {
      if (!mapRef.current) return
      // Add geofences source and layers
      mapRef.current.addSource('geofences', { type: 'geojson', data: geojson })
      mapRef.current.addLayer({
        id: 'geofences-fill',
        type: 'fill',
        source: 'geofences',
        paint: {
          'fill-color': [
            'match', ['get', 'risk_level'],
            'high', '#ff0000',
            'medium', '#ff8800',
            'low', '#00aa00',
            '#888888'
          ],
          'fill-opacity': 0.2
        }
      })
      mapRef.current.addLayer({
        id: 'geofences-line',
        type: 'line',
        source: 'geofences',
        paint: {
          'line-color': '#333',
          'line-width': 2
        }
      })
      // Initial fetches
      refreshGeofences()
      refreshAlerts()
    })
  }, [])

  // Persist JWT when it changes
  useEffect(() => {
    if (apiToken) localStorage.setItem('jwt_token', apiToken)
  }, [apiToken])

  const login = async () => {
    try {
      const body = new URLSearchParams()
      body.set('username', email)
      body.set('password', password)
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      })
      const json = await res.json()
      if (json && json.access_token) setApiToken(json.access_token)
    } catch (_) { /* ignore */ }
  }

  const listGeofences = async () => {
    try {
      const res = await fetch(`${API_URL}/geofences/`)
      const data = await res.json()
      setGeofences(data)
    } catch (_) { /* ignore */ }
  }

  const createGeofence = async () => {
    if (!apiToken) return
    try {
      const body = { name: gfName || 'New zone', risk_level: gfRisk, coordinates: [JSON.parse(gfCoords)] }
      const res = await fetch(`${API_URL}/geofences/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiToken}` },
        body: JSON.stringify(body)
      })
      await res.json()
      listGeofences()
      refreshGeofences()
    } catch (_) { /* ignore */ }
  }

  const deleteGeofence = async (id: number) => {
    if (!apiToken) return
    try {
      await fetch(`${API_URL}/geofences/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${apiToken}` }
      })
      listGeofences()
      refreshGeofences()
    } catch (_) { /* ignore */ }
  }

  const moveMock = (dx: number, dy: number) => {
    const next = { lat: gps.lat + dy, lng: gps.lng + dx }
    setGps(next)
    if (mapRef.current) {
      mapRef.current.setCenter([next.lng, next.lat])
      new mapboxgl.Marker().setLngLat([next.lng, next.lat]).addTo(mapRef.current)
    }
  }

  const setCenterFromInputs = () => {
    const lat = parseFloat(inputLat)
    const lng = parseFloat(inputLng)
    if (Number.isFinite(lat) && Number.isFinite(lng) && mapRef.current) {
      const next = { lat, lng }
      setGps(next)
      mapRef.current.setCenter([lng, lat])
      new mapboxgl.Marker().setLngLat([lng, lat]).addTo(mapRef.current)
    }
  }

  // Poll alerts and geofences periodically
  useEffect(() => {
    const t = setInterval(() => {
      refreshAlerts()
      refreshGeofences()
    }, 5000)
    return () => clearInterval(t)
  }, [])

  const refreshGeofences = async () => {
    try {
      const res = await fetch(`${API_URL}/geofences/geojson`)
      const data = await res.json()
      setGeojson(data)
      if (mapRef.current && mapRef.current.getSource('geofences')) {
        ;(mapRef.current.getSource('geofences') as mapboxgl.GeoJSONSource).setData(data)
      }
    } catch (_) { /* ignore */ }
  }

  const refreshAlerts = async () => {
    try {
      const qs = new URLSearchParams()
      if (filterStatus) qs.set('status', filterStatus)
      if (filterRisk) qs.set('risk', filterRisk)
      qs.set('offset', String(offset))
      qs.set('limit', String(limit))
      const res = await fetch(`${API_URL}/alerts/?${qs.toString()}`)
      const data = await res.json()
      setAlerts(data)
      // Auto-ack duplicates (same user+geofence, keep the newest only)
      if (autoAckDup && apiToken) {
        const seen = new Set<string>()
        for (const a of data) {
          if (a.status !== 'new') continue
          const key = `${a.user_id || 'u'}-${a.geofence_id || 'g'}`
          if (!seen.has(key)) { seen.add(key); continue }
          await fetch(`${API_URL}/alerts/${a.id}/acknowledge`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${apiToken}` }
          })
        }
      }
    } catch (_) { /* ignore */ }
  }

  const ingestHere = async () => {
    const body = {
      user_id: 1,
      lat: gps.lat,
      lng: gps.lng,
      speed: 0,
      source: 'web'
    }
    try {
      const res = await fetch(`${API_URL}/locations/ingest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiToken ? { 'Authorization': `Bearer ${apiToken}` } : {})
        },
        body: JSON.stringify(body)
      })
      await res.json()
      refreshAlerts()
    } catch (_) { /* ignore */ }
  }

  const ackAlert = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/alerts/${id}/acknowledge`, {
        method: 'POST',
        headers: {
          ...(apiToken ? { 'Authorization': `Bearer ${apiToken}` } : {})
        }
      })
      await res.json()
      refreshAlerts()
    } catch (_) { /* ignore */ }
  }

  const resolveAlert = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/alerts/${id}/resolve`, {
        method: 'POST',
        headers: {
          ...(apiToken ? { 'Authorization': `Bearer ${apiToken}` } : {})
        }
      })
      await res.json()
      refreshAlerts()
    } catch (_) { /* ignore */ }
  }

  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <div style={{ position: 'absolute', zIndex: 10, padding: 12, display: 'flex', gap: 12 }}>
        <div>
          <div style={{ marginBottom: 8 }}>
            <button onClick={() => moveMock(0.01, 0)} style={{ marginRight: 8 }}>→</button>
            <button onClick={() => moveMock(-0.01, 0)} style={{ marginRight: 8 }}>←</button>
            <button onClick={() => moveMock(0, 0.01)} style={{ marginRight: 8 }}>↑</button>
            <button onClick={() => moveMock(0, -0.01)}>↓</button>
          </div>
          <div style={{ marginBottom: 8 }}>
            <input
              style={{ width: 320 }}
              placeholder="Paste JWT token (without the word Bearer)"
              value={apiToken}
              onChange={(e) => setApiToken(e.target.value)}
            />
          </div>
          <div style={{ marginBottom: 8 }}>
            <input style={{ width: 150, marginRight: 8 }} placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input style={{ width: 150, marginRight: 8 }} type="password" placeholder="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <button onClick={login}>Login</button>
          </div>
          <div style={{ marginBottom: 8 }}>
            <input
              style={{ width: 140, marginRight: 8 }}
              placeholder="Lat"
              value={inputLat}
              onChange={(e) => setInputLat(e.target.value)}
            />
            <input
              style={{ width: 140, marginRight: 8 }}
              placeholder="Lng"
              value={inputLng}
              onChange={(e) => setInputLng(e.target.value)}
            />
            <button onClick={setCenterFromInputs}>Set center</button>
          </div>
          <div style={{ marginBottom: 8 }}>
            <button onClick={ingestHere} style={{ marginRight: 8 }}>Ingest here</button>
            <button onClick={refreshAlerts} style={{ marginRight: 8 }}>Refresh alerts</button>
            <button onClick={refreshGeofences}>Refresh geofences</button>
          </div>
          <div style={{ marginBottom: 8, fontSize: 12 }}>
            <label>Status:&nbsp;
              <select value={filterStatus} onChange={(e) => { setFilterStatus(e.target.value); setOffset(0); }}>
                <option value="">(all)</option>
                <option value="new">new</option>
                <option value="ack">ack</option>
                <option value="resolved">resolved</option>
              </select>
            </label>
            &nbsp;&nbsp;Risk:&nbsp;
            <select value={filterRisk} onChange={(e) => { setFilterRisk(e.target.value); setOffset(0); }}>
              <option value="">(all)</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
            &nbsp;&nbsp;
            <label><input type="checkbox" checked={autoAckDup} onChange={(e) => setAutoAckDup(e.target.checked)} /> auto-ack duplicates</label>
            &nbsp;&nbsp;
            <label>limit:&nbsp;<input style={{ width: 50 }} value={String(limit)} onChange={(e) => setLimit(Number(e.target.value) || 20)} /></label>
            &nbsp;
            <button onClick={() => { setOffset(Math.max(0, offset - limit)); refreshAlerts() }} disabled={offset === 0}>Prev</button>
            <button onClick={() => { setOffset(offset + limit); refreshAlerts() }} style={{ marginLeft: 6 }}>Next</button>
          </div>
          <div style={{ fontSize: 12, color: '#333' }}>Lat: {gps.lat.toFixed(5)} Lng: {gps.lng.toFixed(5)}</div>
        </div>
        <div style={{ background: 'white', padding: 8, maxHeight: '40vh', overflow: 'auto', minWidth: 360 }}>
          <div style={{ fontWeight: 700, marginBottom: 6 }}>Live Alerts</div>
          {alerts.length === 0 && (<div>No alerts</div>)}
          {alerts.map(a => (
            <div key={a.id} style={{ borderBottom: '1px solid #eee', padding: '6px 0' }}>
              <div style={{ fontSize: 12 }}>
                <b>#{a.id}</b> {a.type} · geofence {a.geofence_id ?? '-'} · user {a.user_id ?? '-'} · sev {a.severity} · status {a.status}
              </div>
              <div>
                <button onClick={() => ackAlert(a.id)} style={{ marginRight: 6 }}>Acknowledge</button>
                <button onClick={() => resolveAlert(a.id)}>Resolve</button>
              </div>
            </div>
          ))}
        </div>
        <div style={{ background: 'white', padding: 8, maxHeight: '40vh', overflow: 'auto', minWidth: 360 }}>
          <div style={{ fontWeight: 700, marginBottom: 6 }}>Geofences</div>
          <div style={{ marginBottom: 8 }}>
            <input style={{ width: 140, marginRight: 8 }} placeholder="Name" value={gfName} onChange={(e) => setGfName(e.target.value)} />
            <select value={gfRisk} onChange={(e) => setGfRisk(e.target.value)} style={{ marginRight: 8 }}>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
            <button onClick={createGeofence}>Create</button>
          </div>
          <div style={{ marginBottom: 8 }}>
            <textarea style={{ width: 340, height: 80 }} value={gfCoords} onChange={(e) => setGfCoords(e.target.value)} />
            <div style={{ fontSize: 12 }}>coords as JSON array of [lng,lat] forming a closed ring</div>
          </div>
          <div style={{ marginBottom: 6 }}>
            <button onClick={listGeofences}>Refresh list</button>
          </div>
          {geofences.map(g => (
            <div key={g.id} style={{ borderBottom: '1px solid #eee', padding: '6px 0', fontSize: 12 }}>
              #{g.id} {g.name} · risk {g.risk_level} · active {String(g.active)}
              <div><button onClick={() => deleteGeofence(g.id)}>Delete</button></div>
            </div>
          ))}
        </div>
      </div>
      <div ref={mapContainer} style={{ height: '100%', width: '100%' }} />
    </div>
  )
}

