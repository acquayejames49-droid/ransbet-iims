// Doughnut showing how many products are in stock / low / need reorder.
import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { getJSON } from '../lib/api'

const COLORS = ['#16a34a', '#f59e0b', '#dc3545']

export default function StockStatus() {
  const [data, setData] = useState([])
  useEffect(() => {
    function load() {
      getJSON('/api/stock-status').then((s) => setData([
        { name: 'In stock', value: s.ok },
        { name: 'Low', value: s.low },
        { name: 'Reorder', value: s.reorder },
      ])).catch(() => {})
    }
    load()
    const id = setInterval(load, 8000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="portlet">
      <div className="portlet-head">Stock status</div>
      <div className="portlet-body">
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
              {data.map((e, i) => <Cell key={i} fill={COLORS[i]} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
