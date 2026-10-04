import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './HistoryChart.css';

const CustomDot = (props) => {
  const { cx, cy, payload } = props;
  if (payload.isAnomaly) {
    return <circle cx={cx} cy={cy} r={5} stroke="red" strokeWidth={2} fill="red" />;
  }
  return <circle cx={cx} cy={cy} r={3} stroke="#3b82f6" strokeWidth={1} fill="#fff" />;
};

const HistoryChart = ({ data, anomalies = [] }) => {
  if (!data || data.length === 0) return <div className="no-data">No history data available</div>;

  const anomalyDates = new Set(anomalies.map(a => a.date));
  const mergedData = data.map(d => ({
    ...d,
    isAnomaly: anomalyDates.has(d.date)
  }));

  return (
    <div className="chart-container">
      <h3>Historical Consumption</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={mergedData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="date" tick={{fontSize: 12}} />
          <YAxis label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '8px' }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="consumption" 
            name="Actual Consumption (kWh)" 
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={<CustomDot />}
            activeDot={{ r: 6 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HistoryChart;
