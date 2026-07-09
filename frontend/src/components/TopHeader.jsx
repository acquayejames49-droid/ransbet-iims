// Page header: title, welcome + date, search, notifications, user chip (logout).
import Icon from './Icon'

export default function TopHeader({ me, overview }) {
  const initials = (me.name || 'U').split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase()
  const first = overview?.user_first || (me.name || '').split(' ')[0]
  return (
    <div className="topbar">
      <div>
        <h1 className="page-title">Overview</h1>
        <div className="page-sub">
          Welcome back, {first}{overview?.date ? ` · ${overview.date}` : ''}
        </div>
      </div>
      <div className="topbar-right">
        <form className="search-box" action="/products" method="get" role="search">
          <Icon name="search" size={18} />
          <input name="q" placeholder="Search products or barcodes…" aria-label="Search products" />
        </form>
        <a className="icon-btn" href="#anomalies" title="View anomaly alerts">
          <Icon name="bell" size={19} /><span className="dot"></span>
        </a>
        <a className="user-chip" href="/logout" title="Click to log out">
          <span className="avatar">{initials}</span>
          <span className="nm">{me.name}</span>
        </a>
      </div>
    </div>
  )
}
