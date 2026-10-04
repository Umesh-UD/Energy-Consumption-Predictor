import React, { useState, useEffect } from 'react';
import { fetchZoneACInsightSummary } from '../api';
import './ZoneComparison.css';

const ACInsightComparison = ({ onSelectZone }) => {
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadComparison = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await fetchZoneACInsightSummary();
        setComparisons(data);
      } catch (err) {
        setError('Failed to fetch AC insight summary data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadComparison();
  }, []);

  return (
    <div className="zone-comparison-container">
      <div className="comparison-header">
        <h2>AC Penetration & Cooling Load Ranking</h2>
        <div className="sort-controls">
          <span className="info-text">Sorted by Highest AC Penetration</span>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loader">Loading AC insight data...</div>
      ) : (
        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>AC Penetration (%)</th>
                <th>Avg Consumption (kWh)</th>
                <th>Avg Temperature (°C)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((zone) => (
                <tr key={zone.zone_id}>
                  <td className="zone-name-cell">{zone.zone_id.replace('_', ' ')}</td>
                  <td>
                    <div className="progress-cell">
                       <span>{Math.round(zone.ac_penetration_pct)}%</span>
                       <div className="mini-progress-bar">
                         <div 
                           className="mini-progress-fill" 
                           style={{ width: `${Math.min(zone.ac_penetration_pct, 100)}%` }}
                         ></div>
                       </div>
                    </div>
                  </td>
                  <td>{zone.avg_consumption_kwh.toFixed(2)}</td>
                  <td>{zone.avg_temperature_c.toFixed(1)}</td>
                  <td>
                    <button 
                      className="view-zone-btn"
                      onClick={() => onSelectZone(zone.zone_id)}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ACInsightComparison;
