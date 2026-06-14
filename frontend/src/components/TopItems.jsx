// Donut of the best-selling items in the last 90 days (greens palette).
import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { getJSON } from '../lib/api'

const COLORS = ['#14532d', '#15803d', '#16a34a', '#22c55e', '#4ade80',
                '#0f766e', '#14b8a6', '#65a30d', '#84cc16', '#a3e635']

export default function TopItems() {
  const [items, setItems] = useState([])
  useEffect(() => { getJSON('/api/top-items').then(setItems).catch(() => {}) }, [])

  return (
    <div className="portlet">
      <div className="portlet-head">Top items by qty sold
        <span className="small text-muted">90 days</span></div>
      <div className="portlet-body">
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie data={items} dataKey="qty" nameKey="name" innerRadius={45} outerRadius={75} paddingAngle={2}>
              {items.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 10 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
