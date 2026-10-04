import React from 'react';
import './AnomalyList.css';

const AnomalyList = ({ anomalies }) => {
  if (!anomalies || anomalies.length === 0) return null;

  return (
    <div className="anomaly-list-container">
      <h3>Anomalies Detected</h3>
      <table className="anomaly-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Actual (kWh)</th>
            <th>Predicted (kWh)</th>
            <th>Deviation</th>
          </tr>
        </thead>
        <tbody>
          {anomalies.map((anomaly, idx) => (
            <tr key={idx}>
              <td>{anomaly.date}</td>
              <td>{anomaly.actual.toFixed(2)}</td>
              <td>{anomaly.predicted.toFixed(2)}</td>
              <td className={anomaly.deviation_pct > 0 ? 'deviation-high' : 'deviation-low'}>
                {anomaly.deviation_pct > 0 ? '+' : ''}{anomaly.deviation_pct.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AnomalyList;
