import React from 'react';
import { Lightbulb, AlertTriangle, Activity } from 'lucide-react';
import './SuggestionCard.css';

const SuggestionCard = ({ suggestion, metrics }) => {
  if (!suggestion) return null;

  const isPeak = suggestion.toLowerCase().includes('peak load');
  const isLower = suggestion.toLowerCase().includes('trending lower');
  
  let icon = <Activity className="icon stable" />;
  let cardClass = "stable-card";
  
  if (isPeak) {
    icon = <AlertTriangle className="icon warning" />;
    cardClass = "warning-card";
  } else if (isLower) {
    icon = <Lightbulb className="icon success" />;
    cardClass = "success-card";
  }

  return (
    <div className={`suggestion-card ${cardClass}`}>
      <div className="suggestion-content">
        <div className="icon-wrapper">
          {icon}
        </div>
        <div>
          <h4>AI Recommendation</h4>
          <p>{suggestion}</p>
        </div>
      </div>
      
      {metrics && (
        <div className="metrics-box">
          <h5>Model Metrics (Test Set)</h5>
          <div className="metrics-grid">
            <div className="metric-item">
              <span className="metric-label">R² Score</span>
              <span className="metric-value">{metrics.R2}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">RMSE</span>
              <span className="metric-value">{metrics.RMSE}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">MAE</span>
              <span className="metric-value">{metrics.MAE}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuggestionCard;
