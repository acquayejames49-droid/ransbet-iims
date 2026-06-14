// Reminders portlet (NetSuite-style): a "featured" group with large counts
// on top, then a denser secondary list below — all from live data.
import { useEffect, useState } from 'react'
import { getJSON } from '../lib/api'

export default function Reminders() {
  const [data, setData] = useState(null)
  useEffect(() => {
    function load() { getJSON('/api/reminders').then(setData).catch(() => {}) }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="portlet">
      <div className="portlet-head">Reminders</div>
      <div className="portlet-body pt-1">
        {!data ? (
          <span className="text-muted small">Loading…</span>
        ) : (
          <>
            {data.featured.map((r, i) => (
              <a key={i} className={`reminder ${r.color}`} href={r.href}>
                <span className="count">{r.count}</span>
                <span>{r.label}</span>
              </a>
            ))}
            <hr className="my-2" />
            {data.list.map((r, i) => (
              <a key={i} className={`reminder-sm ${r.color}`} href={r.href}>
                <span className="count-sm">{r.count}</span>
                <span>{r.label}</span>
              </a>
            ))}
          </>
        )}
      </div>
    </div>
  )
}
