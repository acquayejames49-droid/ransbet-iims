// Green hero banner with the AI forecast headline.
import Icon from './Icon'

export default function Hero({ overview }) {
  const pct = overview?.optimal_pct ?? 0
  return (
    <div className="hero">
      <svg className="hero-leaf" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C3 8 8 5.25 17 8z" />
      </svg>
      <span className="badge-live"><Icon name="zap" size={13} /> AI FORECAST LIVE</span>
      <h1>{pct}% of your products are at healthy stock levels.</h1>
      <p>Based on 108 products with sales history from January 2025, using Prophet demand forecasts and Isolation Forest anomaly detection.</p>
      <div className="hero-actions">
        <a className="btn-white" href="#forecast">View forecast <Icon name="arrowUpRight" size={16} /></a>
        <a className="btn-ghost" href="/reports"><Icon name="download" size={16} /> Export report</a>
      </div>
    </div>
  )
}
