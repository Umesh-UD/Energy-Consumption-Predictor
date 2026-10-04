import React, { useEffect, useState } from 'react';
import { fetchZoneACInsight } from '../api';
import { Wind, Thermometer } from 'lucide-react';
import './ACInsightPanel.css';

const ACInsightPanel = ({ zoneId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!zoneId) return;
    const loadData = async () => {
      setLoading(true);
      setError(false);
      try {
        const result = await fetchZoneACInsight(zoneId);
        setData(result);
      } catch (err) {
        console.error("Failed to load AC insight", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [zoneId]);

  if (loading) return <div className="ac-insight-panel loader">Loading AC Insights...</div>;
  if (error || !data) return <div className="ac-insight-panel loader">AC insights unavailable</div>;

  return (
    <div className="ac-insight-panel">
      <div className="panel-header">
        <Wind size={20} className="icon-main" />
        <h3>Cooling Load Insight</h3>
      </div>
      
      <div className="ac-stats">
        <div className="stat-box primary">
          <div className="stat-value">{Math.round(data.ac_penetration_pct)}%</div>
          <div className="stat-label">AC Penetration</div>
        </div>
        
        <div className="stat-box secondary">
          <div className="stat-value"><Thermometer size={16} /> {data.avg_temperature_c.toFixed(1)}°C</div>
          <div className="stat-label">Avg Temp</div>
        </div>
      </div>

      <div className="insight-desc">
        <p>
          Currently, <strong>{Math.round(data.ac_penetration_pct)}%</strong> of households in this zone own an Air Conditioner. 
          This heavily influences the average consumption of <strong>{data.avg_consumption_kwh.toFixed(1)} kWh</strong>.
        </p>
        <p className="hint">
          Use the <em>What-If Simulator</em> to see how rising AC adoption impacts future load.
        </p>
      </div>
    </div>
  );
};

export default ACInsightPanel;
