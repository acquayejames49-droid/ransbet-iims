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
        <div className="search-box">
          <Icon name="search" size={18} />
          <input placeholder="Search products, SKUs, suppliers…" />
        </div>
        <div className="icon-btn" title="Notifications">
          <Icon name="bell" size={19} /><span className="dot"></span>
        </div>
        <a className="user-chip" href="/logout" title="Click to log out">
          <span className="avatar">{initials}</span>
          <span className="nm">{me.name}</span>
        </a>
      </div>
    </div>
  )
}
