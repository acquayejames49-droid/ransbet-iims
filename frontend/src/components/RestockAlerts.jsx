// Actionable restock list: products at/below reorder point + suggested qty.
import { useEffect, useState } from 'react'
import { getJSON } from '../lib/api'

export default function RestockAlerts() {
  const [items, setItems] = useState([])
  useEffect(() => {
    function load() { getJSON('/api/restock-alerts').then(setItems).catch(() => {}) }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="portlet">
      <div className="portlet-head">Restock alerts
        <span className="badge bg-danger">{items.length}</span></div>
      <div className="portlet-body p-0">
        {items.length === 0 ? (
          <div className="p-3 text-muted">All products are above their reorder point.</div>
        ) : (
          <table className="table table-hover align-middle mb-0">
            <thead className="table-light">
              <tr><th>Product</th><th>In stock</th><th>Reorder point</th>
                  <th>Suggested</th><th></th></tr>
            </thead>
            <tbody>
              {items.map((a) => (
                <tr key={a.id}>
                  <td>{a.name}</td>
                  <td><span className="badge bg-danger">{a.current_stock} {a.unit}</span></td>
                  <td>{a.reorder_point}</td>
                  <td><strong>{a.suggested} {a.unit}</strong></td>
                  <td className="text-end">
                    <a className="btn btn-sm btn-success" href={`/products/${a.id}/receive`}>Receive</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
