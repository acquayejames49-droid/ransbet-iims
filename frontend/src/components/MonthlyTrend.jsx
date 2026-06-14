// Monthly revenue (bars) + units (line) for the last 12 months.
import { useEffect, useState } from 'react'
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts'
import { getJSON } from '../lib/api'

export default function MonthlyTrend() {
  const [data, setData] = useState([])
  useEffect(() => { getJSON('/api/monthly-trend').then(setData).catch(() => {}) }, [])

  return (
    <div className="portlet">
      <div className="portlet-head">Monthly sales trend</div>
      <div className="portlet-body">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" fontSize={11} />
            <YAxis yAxisId="left" fontSize={11} />
            <YAxis yAxisId="right" orientation="right" fontSize={11} />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="revenue" name="Revenue (GHS)" fill="#16a34a" radius={[3, 3, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="units" name="Units" stroke="#14532d" strokeWidth={2} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
