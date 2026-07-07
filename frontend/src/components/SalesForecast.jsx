// Sales forecast card: recent ACTUAL sales (solid green) + Prophet FORECAST
// (dashed) for a chosen product, split by a "Today" divider, plus confidence
// and vs-last-period stats. All from real /api/forecast data.
import { useEffect, useState } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  ReferenceLine,
} from 'recharts'
import { getJSON } from '../lib/api'

const RANGES = [7, 14, 30]

export default function SalesForecast() {
  const [products, setProducts] = useState([])
  const [pid, setPid] = useState(null)
  const [data, setData] = useState(null)
  const [range, setRange] = useState(14)

  useEffect(() => {
    getJSON('/api/products').then((l) => { setProducts(l); if (l.length) setPid(l[0].id) }).catch(() => {})
  }, [])
  useEffect(() => {
    if (pid == null) return
    setData(null)
    getJSON(`/api/forecast/${pid}`).then(setData).catch(() => {})
  }, [pid])

  // Recent actual days + the forecast days, drawn on one timeline.
  const hist = data ? data.history.slice(-range) : []
  const fc = data ? data.forecast.slice(0, range) : []
  const chart = [
    ...hist.map((h) => ({ date: h.date.slice(5), actual: Math.round(h.qty) })),
    ...fc.map((f) => ({ date: f.date.slice(5), forecast: Math.round(f.yhat) })),
  ]
  // Bridge the two lines so the dashed forecast starts where the solid actual ends.
  const boundary = hist.length ? hist[hist.length - 1].date.slice(5) : null
  if (hist.length && fc.length) chart[hist.length - 1].forecast = Math.round(hist[hist.length - 1].qty)
  const step = Math.max(0, Math.round(chart.length / 7) - 1)

  const predicted = fc.reduce((a, f) => a + f.yhat, 0)
  const recentSum = hist.reduce((a, h) => a + h.qty, 0)
  const vsLast = recentSum > 0 ? Math.round((predicted - recentSum) / recentSum * 100) : null
  const mape = data?.metric?.mape
  const acc = mape != null ? Math.max(0, Math.round(100 - mape)) : null
  const conf = acc == null ? '—' : acc >= 85 ? 'High' : acc >= 70 ? 'Medium' : 'Low'

  return (
    <div className="card2 fc-card" id="forecast">
      <div className="card2-head">
        <div>
          <h3 className="card2-title">Sales Forecast — Next {range} days</h3>
          <div className="card2-sub">Facebook Prophet{data ? ` · ${data.product}` : ' · loading…'}</div>
        </div>
        <div className="d-flex align-items-center gap-2 flex-wrap">
          <select className="form-select form-select-sm" style={{ width: 'auto' }}
                  value={pid ?? ''} onChange={(e) => setPid(Number(e.target.value))}>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <div className="seg">
            {RANGES.map((r) => (
              <button key={r} className={r === range ? 'on' : ''} onClick={() => setRange(r)}>{r}d</button>
            ))}
          </div>
        </div>
      </div>
      <div className="card2-body fc-body">
        {!data ? <p className="text-muted mb-0">Loading forecast…</p> : (
          <>
            <div className="fc-legend">
              <span><i className="sw sw-actual" />Actual (recorded)</span>
              <span><i className="sw sw-fc" />Forecast (predicted)</span>
            </div>
            <div className="fc-chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chart} margin={{ left: -18, right: 8, top: 8 }}>
                  <defs>
                    <linearGradient id="aFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#16a34a" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#16a34a" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="fFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#22c55e" stopOpacity={0.16} />
                      <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eef2ef" />
                  <XAxis dataKey="date" fontSize={11} tickLine={false} axisLine={false} interval={step} />
                  <YAxis fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip />
                  {boundary && (
                    <ReferenceLine x={boundary} stroke="#94a3b8" strokeDasharray="4 4"
                      label={{ value: 'Today', position: 'top', fontSize: 11, fill: '#64748b' }} />
                  )}
                  <Area type="monotone" dataKey="actual" name="Actual" stroke="#15803d" strokeWidth={2.5}
                        fill="url(#aFill)" connectNulls={false} dot={false} />
                  <Area type="monotone" dataKey="forecast" name="Forecast" stroke="#15803d" strokeWidth={2.5}
                        strokeDasharray="6 4" fill="url(#fFill)" connectNulls={false} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="fc-stats">
              <div><div className="l">Predicted units</div><div className="v">{Math.round(predicted).toLocaleString()}</div></div>
              <div><div className="l">Confidence</div><div className="v text-rb-green">{conf}{acc != null ? ` · ${acc}%` : ''}</div></div>
              <div>
                <div className="l">vs Last period</div>
                <div className="v" style={{ color: vsLast != null && vsLast < 0 ? '#dc2626' : '#15803d' }}>
                  {vsLast == null ? '—' : `${vsLast >= 0 ? '+' : ''}${vsLast}%`}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
