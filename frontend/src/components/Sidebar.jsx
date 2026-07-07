// Left navigation sidebar (Lovable style): brand, nav links, AI insight, settings.
import { useEffect, useState } from 'react'
import Icon from './Icon'
import { getJSON } from '../lib/api'

export default function Sidebar({ me }) {
  const canManage = me.role === 'manager' || me.role === 'owner'
  const [insight, setInsight] = useState(null)

  useEffect(() => {
    getJSON('/api/reminders').then((r) => {
      const feat = (r.featured || []).find((x) => x.label.startsWith('Predicted'))
      if (feat) setInsight(feat.count)
    }).catch(() => {})
  }, [])

  const nav = [
    { label: 'Overview', icon: 'grid', href: '/dashboard', active: true },
    { label: 'Inventory', icon: 'box', href: '/products' },
    { label: 'Scan', icon: 'scan', href: '/scan' },
    { label: 'Sales', icon: 'cart', href: '/sales' },
    { label: 'Movements', icon: 'move', href: '/movements' },
    { label: 'Suppliers', icon: 'truck', href: '/suppliers' },
    { label: 'Reports', icon: 'doc', href: '/reports' },
  ]
  const manage = [
    { label: 'Categories', icon: 'tag', href: '/categories' },
    { label: 'Audit log', icon: 'doc', href: '/audit' },
    { label: 'Import / Data', icon: 'download', href: '/data' },
  ]

  return (
    <aside className="sidebar">
      <a className="brand" href="/dashboard">
        <span className="brand-logo"><Icon name="box" size={20} /></span>
        <span>
          <div className="brand-name">Ransbet IIMS</div>
          <div className="brand-sub">Tarkwa · Ghana</div>
        </span>
      </a>

      {nav.map((n) => (
        <a key={n.label} className={`nav-item${n.active ? ' active' : ''}`} href={n.href}>
          <Icon name={n.icon} size={19} />
          <span>{n.label}</span>
          {n.active && <Icon name="chevronRight" size={16} />}
        </a>
      ))}

      {canManage && <>
        <div className="nav-label">Manage</div>
        {manage.map((n) => (
          <a key={n.label} className="nav-item" href={n.href}>
            <Icon name={n.icon} size={19} /><span>{n.label}</span>
          </a>
        ))}
      </>}

      <div className="ai-insight">
        <div className="h"><Icon name="zap" size={13} /> AI Insight</div>
        <p>
          {insight != null && insight > 0
            ? `${insight} item${insight === 1 ? '' : 's'} are predicted to run out within 7 days. Review reorder suggestions below.`
            : 'Inventory is well stocked against predicted demand. Keep monitoring the forecast.'}
        </p>
        <a href="#forecast">View forecast →</a>
      </div>
    </aside>
  )
}
