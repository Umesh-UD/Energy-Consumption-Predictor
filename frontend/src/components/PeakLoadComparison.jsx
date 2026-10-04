import React, { useState, useEffect } from 'react';
import { fetchZonePeakLoadSummary } from '../api';
import './ZoneComparison.css';

const PeakLoadComparison = ({ onSelectZone }) => {
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadComparison = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await fetchZonePeakLoadSummary();
        setComparisons(data);
      } catch (err) {
        setError('Failed to fetch peak load summary data.');
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
        <h2>Peak Load Risk Ranking</h2>
        <div className="sort-controls">
          <span className="info-text">Sorted by Highest Risk (Peak Ratio)</span>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loader">Loading peak load risk data...</div>
      ) : (
        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Avg Total Load (kWh)</th>
                <th>Peak Load (kWh)</th>
                <th>Peak Ratio</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((zone) => (
                <tr key={zone.zone_id} className={zone.at_risk ? 'risk-row' : ''}>
                  <td className="zone-name-cell">{zone.zone_id.replace('_', ' ')}</td>
                  <td>{zone.total_consumption_kwh.toFixed(2)}</td>
                  <td>{zone.peak_hours_usage_kwh.toFixed(2)}</td>
                  <td>{(zone.peak_ratio * 100).toFixed(1)}%</td>
                  <td>
                    {zone.at_risk ? (
                       <span className="risk-badge">At Risk</span>
                    ) : (
                       <span className="safe-badge">Safe</span>
                    )}
                  </td>
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

export default PeakLoadComparison;
