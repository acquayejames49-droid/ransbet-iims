// KPI portlet: four metric cards with sparklines, plus a comparison table
// (Indicator / Period / Current / Previous / Change) like NetSuite.
import { useEffect, useState } from 'react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { getJSON } from '../lib/api'

function fmt(v, money) {
  if (v == null) return '—'
  return money
    ? Number(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : Math.round(v).toLocaleString()
}

function Spark({ data }) {
  return (
    <ResponsiveContainer width="100%" height={36}>
      <LineChart data={data.map((v, i) => ({ i, v }))}>
        <Line type="monotone" dataKey="v" stroke="#16a34a" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default function Kpis() {
  const [data, setData] = useState(null)
  useEffect(() => {
    function load() { getJSON('/api/kpis').then(setData).catch(() => {}) }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])
  if (!data) return null

  return (
    <div className="portlet">
      <div className="portlet-head">Key Performance Indicators</div>
      <div className="portlet-body">
        <div className="row g-2 mb-3">
          {data.kpis.map((k, i) => (
            <div className="col-6 col-xl-3" key={i}>
              <div className="kpi-card h-100">
                <div className="kpi-label">{k.label}</div>
                <div className="kpi-value">{k.money ? 'GHS ' : ''}{fmt(k.current, k.money)}</div>
                <div className="d-flex justify-content-between align-items-end">
                  <small className={k.change >= 0 ? 'kpi-up' : 'kpi-down'}>
                    {k.change == null ? '' : (k.change >= 0 ? '▲ ' : '▼ ') + Math.abs(k.change) + '%'}
                  </small>
                  <div style={{ width: 70 }}>{k.spark.length > 0 && <Spark data={k.spark} />}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <table className="table table-sm align-middle mb-0">
          <thead>
            <tr className="text-muted small">
              <th>Indicator</th><th>Period</th>
              <th className="text-end">Current</th><th className="text-end">Previous</th>
              <th className="text-end">Change</th>
            </tr>
          </thead>
          <tbody>
            {data.kpis.filter((k) => k.previous != null).map((k, i) => (
              <tr key={i}>
                <td>{k.label}</td>
                <td className="small text-muted">{k.period}</td>
                <td className="text-end">{k.money ? 'GHS ' : ''}{fmt(k.current, k.money)}</td>
                <td className="text-end">{k.money ? 'GHS ' : ''}{fmt(k.previous, k.money)}</td>
                <td className={`text-end ${k.change >= 0 ? 'kpi-up' : 'kpi-down'}`}>
                  {k.change == null ? '—' : (k.change >= 0 ? '▲ ' : '▼ ') + Math.abs(k.change) + '%'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
