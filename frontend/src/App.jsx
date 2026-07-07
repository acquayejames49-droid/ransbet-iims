// Root: asks "who am I?" then renders the sidebar + the dashboard.
import { useEffect, useState } from 'react'
import { getJSON } from './lib/api'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'

export default function App() {
  const [me, setMe] = useState(null)

  useEffect(() => {
    getJSON('/api/me').then(setMe).catch(() => {})
  }, [])

  if (!me) return <div className="p-5 text-center text-muted">Loading…</div>

  return (
    <div className="app-shell">
      <Sidebar me={me} />
      <main className="main"><Dashboard me={me} /></main>
    </div>
  )
}
