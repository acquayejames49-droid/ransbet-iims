// Two-tier green header (NetSuite-style): brand + search + user on top,
// menu links below.
export default function Navbar({ me }) {
  const canManage = me.role === 'manager' || me.role === 'owner'
  return (
    <header>
      <div className="rb-header d-flex align-items-center px-3 py-2 gap-3">
        <a className="rb-brand fs-5" href="/dashboard">
          Ransbet <span style={{ fontWeight: 400, opacity: .85 }}>IIMS</span>
        </a>
        <input className="rb-search form-control form-control-sm flex-grow-1"
               placeholder="Search…" style={{ maxWidth: 480 }} />
        <div className="ms-auto d-flex align-items-center gap-2 text-white">
          <span className="small d-none d-md-inline">
            {me.name} <span className="badge bg-light text-dark text-capitalize">{me.role}</span>
          </span>
          <a className="btn btn-sm btn-outline-light" href="/logout">Logout</a>
        </div>
      </div>
      <nav className="rb-menu px-2 d-flex flex-wrap">
        <a className="active" href="/dashboard">Home</a>
        <a href="/products">Inventory</a>
        <a href="/scan">Scan</a>
        <a href="/sales">Sales</a>
        <a href="/reports">Reports</a>
        <a href="/movements">Movements</a>
        <a href="/suppliers">Suppliers</a>
        {canManage && <a href="/categories">Categories</a>}
        {canManage && <a href="/audit">Audit</a>}
        {canManage && <a href="/data">Import / Data</a>}
      </nav>
    </header>
  )
}
