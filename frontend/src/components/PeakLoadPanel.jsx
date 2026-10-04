import React, { useEffect, useState } from 'react';
import { fetchZonePeakLoad } from '../api';
import { AlertTriangle, Activity } from 'lucide-react';
import './PeakLoadPanel.css';

const PeakLoadPanel = ({ zoneId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!zoneId) return;
    const loadData = async () => {
      setLoading(true);
      setError(false);
      try {
        const result = await fetchZonePeakLoad(zoneId);
        setData(result);
      } catch (err) {
        console.error("Failed to load peak load data", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [zoneId]);

  if (loading) return <div className="peak-load-panel loader">Loading Peak Data...</div>;
  if (error || !data) return <div className="peak-load-panel loader">Peak load data unavailable</div>;

  const ratioPct = (data.peak_ratio * 100).toFixed(1);
  
  return (
    <div className={`peak-load-panel ${data.at_risk ? 'risk' : 'safe'}`}>
      <div className="panel-header">
        <Activity size={20} className="icon-main" />
        <h3>Peak Load Analysis</h3>
        {data.at_risk && (
          <div className="risk-badge">
            <AlertTriangle size={16} /> At Risk
          </div>
        )}
      </div>
      
      <div className="peak-stats">
        <div className="stat-row">
          <span className="stat-label">Total Average Load:</span>
          <span className="stat-val">{data.total_consumption_kwh.toFixed(1)} kWh</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Peak Hours Load:</span>
          <span className="stat-val">{data.peak_hours_usage_kwh.toFixed(1)} kWh</span>
        </div>
      </div>

      <div className="peak-visual">
        <div className="ratio-text">
          <span className="ratio-number">{ratioPct}%</span> of load occurs during peak hours
        </div>
        <div className="progress-bar-bg">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${Math.min(data.peak_ratio * 100, 100)}%` }}
          ></div>
          <div 
            className="threshold-marker" 
            style={{ left: `${data.threshold * 100}%` }}
            title={`Risk Threshold: ${(data.threshold * 100).toFixed(0)}%`}
          ></div>
        </div>
        <p className="threshold-desc">Threshold for grid stress is {(data.threshold * 100).toFixed(0)}%.</p>
      </div>
    </div>
  );
};

export default PeakLoadPanel;
