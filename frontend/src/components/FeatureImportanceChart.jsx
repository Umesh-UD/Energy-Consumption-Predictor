import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './HistoryChart.css';

const FeatureImportanceChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  // Sort by importance
  const sortedData = [...data].sort((a, b) => b.importance - a.importance);

  return (
    <div className="chart-container">
      <h3>Key Consumption Drivers</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart
          layout="vertical"
          data={sortedData}
          margin={{ top: 5, right: 30, left: 50, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} horizontal={true} vertical={false} />
          <XAxis type="number" hide />
          <YAxis dataKey="feature" type="category" tick={{fontSize: 12}} width={100} />
          <Tooltip 
            formatter={(value) => value.toFixed(4)}
            contentStyle={{ borderRadius: '8px' }}
          />
          <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureImportanceChart;
