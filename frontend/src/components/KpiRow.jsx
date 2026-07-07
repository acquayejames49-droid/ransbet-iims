// The four headline KPI cards.
import Icon from './Icon'

const fmt = (n) => Number(n).toLocaleString()

export default function KpiRow({ overview }) {
  const k = overview?.kpis
  if (!k) return null
  const cards = [
    { label: 'Forecasted Revenue', value: `₵${fmt(Math.round(k.forecasted_revenue.value))}`,
      change: k.forecasted_revenue.change, sub: k.forecasted_revenue.sub },
    { label: 'Units in Stock', value: fmt(k.units_in_stock.value),
      change: k.units_in_stock.change, sub: k.units_in_stock.sub },
    { label: 'Stockout Risk', value: `${k.stockout_risk.value} items`,
      change: k.stockout_risk.change, sub: k.stockout_risk.sub },
    { label: 'Forecast Accuracy', value: k.forecast_accuracy.value != null ? `${k.forecast_accuracy.value}%` : '—',
      change: k.forecast_accuracy.change, sub: k.forecast_accuracy.sub },
  ]
  return (
    <div className="kpi-grid">
      {cards.map((c, i) => (
        <div className="kpi" key={i}>
          {c.change != null && (
            <span className={`chg ${c.change >= 0 ? 'up' : 'down'}`}>
              <Icon name={c.change >= 0 ? 'arrowUpRight' : 'arrowDown'} size={12} />
              {Math.abs(c.change)}%
            </span>
          )}
          <div className="label">{c.label}</div>
          <div className="value">{c.value}</div>
          <div className="sub">{c.sub}</div>
        </div>
      ))}
    </div>
  )
}
