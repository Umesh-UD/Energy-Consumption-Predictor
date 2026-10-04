import React, { useState } from 'react';
import './WhatIfSimulator.css';
import { simulateZonePrediction, fetchZoneACInsight } from '../api';

const WhatIfSimulator = ({ zoneId }) => {
  const [temperature, setTemperature] = useState(28);
  const [dayOfWeek, setDayOfWeek] = useState(0); // 0 is Monday
  const [isHoliday, setIsHoliday] = useState(false);
  const [simulatedResult, setSimulatedResult] = useState(null);
  const [adjustedResult, setAdjustedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [acPenetration, setAcPenetration] = useState(0);

  React.useEffect(() => {
    if (!zoneId) return;
    const loadAC = async () => {
      try {
        const insight = await fetchZoneACInsight(zoneId);
        if (insight && insight.ac_penetration_pct !== undefined) {
          setAcPenetration(Math.round(insight.ac_penetration_pct));
        }
      } catch (err) {
        console.error("Failed to load AC insight", err);
      }
    };
    loadAC();
  }, [zoneId]);

  const handleSimulate = async () => {
    if (!zoneId) return;
    setLoading(true);
    try {
      const inputs = {
        temperature: parseFloat(temperature),
        day_of_week: parseInt(dayOfWeek, 10),
        is_holiday: isHoliday ? 1 : 0,
        ac_penetration_pct: parseFloat(acPenetration)
      };
      const res = await simulateZonePrediction(zoneId, inputs);
      setSimulatedResult(res.baseline_prediction);
      setAdjustedResult(res.adjusted_prediction);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulator-container">
      <h3>What-If Simulator</h3>
      <p className="simulator-desc">Adjust conditions to see how predicted consumption changes.</p>
      
      <div className="simulator-controls">
        <div className="control-group">
          <label>Temperature (°C): {temperature}</label>
          <input 
            type="range" 
            min="10" 
            max="45" 
            value={temperature} 
            onChange={(e) => setTemperature(e.target.value)} 
          />
        </div>

        <div className="control-group">
          <label>Day of Week:</label>
          <select value={dayOfWeek} onChange={(e) => setDayOfWeek(e.target.value)}>
            <option value={0}>Monday</option>
            <option value={1}>Tuesday</option>
            <option value={2}>Wednesday</option>
            <option value={3}>Thursday</option>
            <option value={4}>Friday</option>
            <option value={5}>Saturday</option>
            <option value={6}>Sunday</option>
          </select>
        </div>

        <div className="control-group checkbox-group">
          <label>
            <input 
              type="checkbox" 
              checked={isHoliday} 
              onChange={(e) => setIsHoliday(e.target.checked)} 
            />
            Is Holiday?
          </label>
        </div>

        <div className="control-group">
          <label>AC Penetration (%): {acPenetration}</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={acPenetration} 
            onChange={(e) => setAcPenetration(e.target.value)} 
          />
        </div>

        <button 
          className="simulate-btn" 
          onClick={handleSimulate} 
          disabled={loading || !zoneId}
        >
          {loading ? 'Simulating...' : 'Simulate'}
        </button>
      </div>

      {simulatedResult !== null && (
        <div className="simulation-result">
          <h4>Predicted Consumption:</h4>
          {adjustedResult && Math.abs(simulatedResult - adjustedResult) > 0.01 ? (
             <div className="result-value-compare">
               <span className="baseline-val">{simulatedResult.toFixed(2)}</span>
               <span className="arrow"> → </span>
               <span className="adjusted-val">{adjustedResult.toFixed(2)}</span> <span className="unit">kWh</span>
             </div>
          ) : (
            <div className="result-value">{simulatedResult.toFixed(2)} <span className="unit">kWh</span></div>
          )}
        </div>
      )}
    </div>
  );
};

export default WhatIfSimulator;
