// Anomaly feed (Lovable style): recent unusual events from the AI, live.
import { useEffect, useState } from 'react'
import Icon from './Icon'
import { getJSON } from '../lib/api'

function timeAgo(dstr) {
  const diff = Math.round((Date.now() - new Date(dstr).getTime()) / 86400000)
  if (diff <= 0) return 'today'
  if (diff === 1) return '1 day ago'
  if (diff < 30) return `${diff} days ago`
  return new Date(dstr).toLocaleDateString()
}

export default function AnomalyFeed() {
  const [items, setItems] = useState([])
  useEffect(() => {
    function load() { getJSON('/api/anomalies').then((a) => setItems(a.slice(0, 6))).catch(() => {}) }
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="card2" id="anomalies">
      <div className="card2-head">
        <h3 className="card2-title">Anomaly Feed</h3>
        <span className="text-muted" style={{ fontSize: 13, display: 'flex', alignItems: 'center' }}>
          <span className="live-dot"></span>Live
        </span>
      </div>
      <div className="card2-body">
        {items.length === 0 ? (
          <p className="text-muted mb-0">No anomalies detected.</p>
        ) : items.map((a) => (
          <div className="anom" key={a.id}>
            <span className="ic"><Icon name="alert" size={18} /></span>
            <div>
              <div className="t">Unusual {a.reason} in {a.product} sales</div>
              <div className="time">{timeAgo(a.date)} · {a.quantity} sold vs ~{a.expected} expected</div>
            </div>
          </div>
        ))}
        <a className="link-green" href="#inventory">View all anomalies →</a>
      </div>
    </div>
  )
}
