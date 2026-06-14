// The NetSuite-style home: reminders + tiles + KPIs on top, charts in the
// middle, then the actionable restock/forecast/anomaly panels.
import { useEffect, useState } from 'react'
import Reminders from './Reminders'
import Tiles from './Tiles'
import Kpis from './Kpis'
import Gauge from './Gauge'
import TopItems from './TopItems'
import MonthlyTrend from './MonthlyTrend'
import StockStatus from './StockStatus'
import RestockAlerts from './RestockAlerts'
import Forecast from './Forecast'
import Anomalies from './Anomalies'

export default function Dashboard({ me }) {
  const [now, setNow] = useState('')
  useEffect(() => {
    const t = setInterval(() => setNow(new Date().toLocaleTimeString()), 1000)
    return () => clearInterval(t)
  }, [])
  const canManage = me?.role === 'manager' || me?.role === 'owner'

  return (
    <div className="container-fluid py-3">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="mb-0 text-rb-green">Home</h4>
        <span className="text-muted small"><span className="live-dot"></span> Live · {now}</span>
      </div>

      <div className="row">
        <div className="col-lg-3"><Reminders /></div>
        <div className="col-lg-6"><Tiles canManage={canManage} /><Kpis /></div>
        <div className="col-lg-3"><Gauge /><TopItems /></div>
      </div>

      <div className="row">
        <div className="col-lg-8"><MonthlyTrend /></div>
        <div className="col-lg-4"><StockStatus /></div>
      </div>

      <RestockAlerts />
      <Forecast />
      <Anomalies />
    </div>
  )
}
