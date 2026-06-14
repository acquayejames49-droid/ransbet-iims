// A semicircular gauge (the "KPI meter") drawn with plain SVG, showing the
// total inventory value against a scale.
import { useEffect, useState } from 'react'
import { getJSON } from '../lib/api'

function polar(cx, cy, r, a) {            // a: 0=left … 180=right, over the top
  const rad = (a * Math.PI) / 180
  return [cx - r * Math.cos(rad), cy - r * Math.sin(rad)]
}
function arc(cx, cy, r, a0, a1) {
  const [x1, y1] = polar(cx, cy, r, a0)
  const [x2, y2] = polar(cx, cy, r, a1)
  const large = a1 - a0 > 180 ? 1 : 0
  return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`
}

export default function Gauge() {
  const [g, setG] = useState(null)
  useEffect(() => {
    function load() { getJSON('/api/kpis').then((d) => setG(d.gauge)).catch(() => {}) }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])
  if (!g) return null

  const frac = Math.max(0, Math.min(1, g.value / g.max))
  return (
    <div className="portlet">
      <div className="portlet-head">Inventory KPI meter</div>
      <div className="portlet-body text-center">
        <svg viewBox="0 0 200 120" width="100%" style={{ maxWidth: 280 }}>
          <path d={arc(100, 100, 80, 0, 180)} fill="none" stroke="#e5e7eb"
                strokeWidth="16" strokeLinecap="round" />
          <path d={arc(100, 100, 80, 0, 180 * frac)} fill="none" stroke="#16a34a"
                strokeWidth="16" strokeLinecap="round" />
          <text x="100" y="90" textAnchor="middle" fontSize="20" fontWeight="700" fill="#14532d">
            GHS {Math.round(g.value).toLocaleString()}
          </text>
          <text x="100" y="108" textAnchor="middle" fontSize="9" fill="#6b7280">{g.label}</text>
        </svg>
      </div>
    </div>
  )
}
