// The root component. It first asks the server "who am I?" (/api/me). While
// waiting it shows a loading line; once it knows the user it renders the
// green header and the dashboard.
import { useEffect, useState } from 'react'
import { getJSON } from './lib/api'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'

export default function App() {
  const [me, setMe] = useState(null)

  useEffect(() => {
    getJSON('/api/me').then(setMe).catch(() => {})
  }, [])

  if (!me) {
    return <div className="container py-5 text-center text-muted">Loading…</div>
  }

  return (
    <>
      <Navbar me={me} />
      <Dashboard me={me} />
    </>
  )
}
