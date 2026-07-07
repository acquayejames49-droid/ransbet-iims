// Inventory intelligence table: real-time stock (with a bar) vs predicted demand,
// and a health status pill. Real data.
import { useEffect, useState } from 'react'
import Icon from './Icon'
import { getJSON } from '../lib/api'

const S = {
  Healthy: { pill: 'ok', fill: 'fill-ok' },
  Low: { pill: 'low', fill: 'fill-low' },
  Critical: { pill: 'crit', fill: 'fill-crit' },
}

export default function InventoryIntelligence() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    function load() { getJSON('/api/inventory-intelligence').then(setRows).catch(() => {}) }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="card2" id="inventory">
      <div className="card2-head">
        <div>
          <h3 className="card2-title">Inventory Intelligence</h3>
          <div className="card2-sub">Real-time stock vs predicted demand</div>
        </div>
        <a className="link-green" href="/products">Manage inventory <Icon name="chevronRight" size={15} /></a>
      </div>
      <div className="card2-body" style={{ overflowX: 'auto' }}>
        <table className="inv">
          <thead>
            <tr><th>Product</th><th>SKU</th><th>Stock</th><th>Predicted demand (7d)</th><th>Status</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const s = S[r.status] || S.Healthy
              return (
                <tr key={r.id}>
                  <td className="pname">{r.name}</td>
                  <td className="sku">{r.sku}</td>
                  <td>
                    <div className="stockcell">
                      <b>{r.stock.toLocaleString()}</b>
                      <span className="bar"><span className={s.fill} style={{ width: `${r.stock_pct}%` }}></span></span>
                    </div>
                  </td>
                  <td><span className="demand"><Icon name="trending" size={15} />{r.predicted.toLocaleString()} units</span></td>
                  <td><span className={`pill ${s.pill}`}>{r.status}</span></td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
