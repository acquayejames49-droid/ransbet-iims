// Coloured action tiles (like NetSuite's quick-action tiles).
import Icon from './Icon'

export default function Tiles({ canManage }) {
  const tiles = [
    { label: 'Add Product', href: '/products/new', cls: 'tile-green', icon: 'plus' },
    { label: 'Scan Barcode', href: '/scan', cls: 'tile-teal', icon: 'box' },
    canManage
      ? { label: 'Import Data', href: '/data', cls: 'tile-amber', icon: 'download' }
      : { label: 'Movements', href: '/movements', cls: 'tile-amber', icon: 'cart' },
    { label: 'Reports', href: '/reports', cls: 'tile-slate', icon: 'doc' },
  ]
  return (
    <div className="portlet">
      <div className="portlet-head">Quick actions</div>
      <div className="portlet-body">
        <div className="row g-2">
          {tiles.map((t, i) => (
            <div className="col-6 col-xl-3" key={i}>
              <a className={`tile ${t.cls}`} href={t.href}>
                <Icon name={t.icon} size={26} />
                <span className="tile-label">{t.label}</span>
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
