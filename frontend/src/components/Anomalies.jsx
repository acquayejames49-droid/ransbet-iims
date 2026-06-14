// Anomaly alerts: recent unusual sales events flagged by the Isolation Forest
// model. A "spike" is an unexpectedly high day; a "drop" is unexpectedly low.
import { useEffect, useState } from 'react'
import { getJSON } from '../lib/api'

export default function Anomalies() {
  const [items, setItems] = useState([])

  useEffect(() => {
    function load() { getJSON('/api/anomalies').then(setItems).catch(() => {}) }
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="portlet">
      <div className="portlet-head">
        <span>Anomaly alerts</span>
        <span className="badge bg-warning text-dark">{items.length}</span>
      </div>
      <div className="portlet-body p-0">
        {items.length === 0 ? (
          <div className="p-4 text-center text-muted">No anomalies detected.</div>
        ) : (
          <table className="table table-sm table-hover mb-0 align-middle">
            <thead className="table-light">
              <tr><th>Date</th><th>Product</th><th>Type</th>
                  <th className="text-end">Actual</th><th className="text-end">Expected</th></tr>
            </thead>
            <tbody>
              {items.map((a) => (
                <tr key={a.id}>
                  <td className="small">{a.date}</td>
                  <td>{a.product}</td>
                  <td>{a.reason === 'spike'
                    ? <span className="badge bg-danger">Spike</span>
                    : <span className="badge bg-secondary">Drop</span>}</td>
                  <td className="text-end">{a.quantity}</td>
                  <td className="text-end text-muted">{a.expected}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
