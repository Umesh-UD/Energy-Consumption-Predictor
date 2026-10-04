import React, { useState, useEffect } from 'react';
import { fetchZoneComparison } from '../api';
import './ZoneComparison.css';

const ZoneComparison = ({ onSelectZone }) => {
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('change');
  const [error, setError] = useState('');

  useEffect(() => {
    const loadComparison = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await fetchZoneComparison(sortBy);
        setComparisons(data);
      } catch (err) {
        setError('Failed to fetch zone comparison data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadComparison();
  }, [sortBy]);

  return (
    <div className="zone-comparison-container">
      <div className="comparison-header">
        <h2>Zone Comparison & Ranking</h2>
        <div className="sort-controls">
          <label>Sort By:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="change">Percentage Change (Predicted Growth)</option>
            <option value="predicted">Highest Predicted Avg</option>
            <option value="zone_name">Zone Name</option>
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loader">Loading comparison data...</div>
      ) : (
        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Historical Avg (kWh)</th>
                <th>Predicted Avg (kWh)</th>
                <th>Growth / Change</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((zone) => (
                <tr key={zone.zone_id}>
                  <td className="zone-name-cell">{zone.zone_name}</td>
                  <td>{zone.historical_avg.toFixed(2)}</td>
                  <td>{zone.predicted_avg.toFixed(2)}</td>
                  <td className={zone.percentage_change > 0 ? 'growth-positive' : 'growth-negative'}>
                    {zone.percentage_change > 0 ? '+' : ''}{zone.percentage_change.toFixed(2)}%
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

export default ZoneComparison;
