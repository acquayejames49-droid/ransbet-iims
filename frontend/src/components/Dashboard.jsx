// The redesigned "Overview" dashboard (Lovable style) — every existing panel is
// preserved below under "More insights".
import { useEffect, useState } from 'react'
import { getJSON } from '../lib/api'
import TopHeader from './TopHeader'
import Hero from './Hero'
import KpiRow from './KpiRow'
import SalesForecast from './SalesForecast'
import AnomalyFeed from './AnomalyFeed'
import InventoryIntelligence from './InventoryIntelligence'
import Reminders from './Reminders'
import MonthlyTrend from './MonthlyTrend'
import TopItems from './TopItems'
import StockStatus from './StockStatus'
import Gauge from './Gauge'
import RestockAlerts from './RestockAlerts'

export default function Dashboard({ me }) {
  const [overview, setOverview] = useState(null)
  useEffect(() => {
    function load() { getJSON('/api/overview').then(setOverview).catch(() => {}) }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])

  return (
    <>
      <TopHeader me={me} overview={overview} />
      <Hero overview={overview} />
      <KpiRow overview={overview} />

      <div className="row g-3 row-stretch">
        <div className="col-lg-8"><SalesForecast /></div>
        <div className="col-lg-4"><AnomalyFeed /></div>
      </div>

      <InventoryIntelligence />

      <h5 className="text-rb-green mt-4 mb-3" style={{ fontWeight: 700 }}>More insights</h5>
      <div className="row g-3 row-stretch">
        <div className="col-lg-4"><Reminders /></div>
        <div className="col-lg-8"><MonthlyTrend /></div>
      </div>
      <div className="row g-3">
        <div className="col-lg-4"><Gauge /></div>
        <div className="col-lg-4"><TopItems /></div>
        <div className="col-lg-4"><StockStatus /></div>
      </div>
      <RestockAlerts />

      <div className="app-footer">
        Ransbet Intelligent Inventory Management System · <b>University of Mines and Technology, Tarkwa</b>
      </div>
    </>
  )
}
