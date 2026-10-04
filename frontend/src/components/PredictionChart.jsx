import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './HistoryChart.css'; // Reuse styles

const PredictionChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="chart-container">
      <h3>7-Day Prediction</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data}
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
            dataKey="prediction" 
            name="Predicted Consumption (kWh)" 
            stroke="#10b981" 
            strokeDasharray="5 5"
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PredictionChart;
