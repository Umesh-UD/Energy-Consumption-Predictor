import React from 'react';
import './ZoneSelector.css';

const ZoneSelector = ({ zones, selectedZone, onSelectZone }) => {
  return (
    <div className="zone-selector">
      <label htmlFor="zone-select">Select Region:</label>
      <select 
        id="zone-select" 
        value={selectedZone} 
        onChange={(e) => onSelectZone(e.target.value)}
      >
        <option value="" disabled>Select a zone</option>
        {zones.map((zone) => (
          <option key={zone.id} value={zone.id}>
            {zone.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ZoneSelector;
