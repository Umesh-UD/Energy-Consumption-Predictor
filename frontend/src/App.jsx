import { useState, useEffect } from 'react'
import { fetchZones, fetchZoneHistory, fetchZonePrediction, fetchZoneFeatures, fetchZoneSuggestion, fetchZoneMetrics, fetchZoneAnomalies } from './api'
import ZoneSelector from './components/ZoneSelector'
import HistoryChart from './components/HistoryChart'
import PredictionChart from './components/PredictionChart'
import FeatureImportanceChart from './components/FeatureImportanceChart'
import SuggestionCard from './components/SuggestionCard'
import AnomalyList from './components/AnomalyList'
import WhatIfSimulator from './components/WhatIfSimulator'
import ZoneComparison from './components/ZoneComparison'
import PeakLoadPanel from './components/PeakLoadPanel'
import ACInsightPanel from './components/ACInsightPanel'
import PeakLoadComparison from './components/PeakLoadComparison'
import ACInsightComparison from './components/ACInsightComparison'
import { Zap, LayoutDashboard, BarChart2, Activity, Wind } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard') // 'dashboard' or 'comparison'
  const [zones, setZones] = useState([])
  const [selectedZone, setSelectedZone] = useState('')
  const [history, setHistory] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [features, setFeatures] = useState(null)
  const [suggestion, setSuggestion] = useState('')
  const [metrics, setMetrics] = useState(null)
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchZones()
      .then(data => setZones(data))
      .catch(err => setError('Failed to load zones from backend. Make sure backend is running.'))
  }, [])

  useEffect(() => {
    if (!selectedZone) return;
    
    const loadZoneData = async () => {
      setLoading(true)
      setError('')
      try {
        const results = await Promise.allSettled([
          fetchZoneHistory(selectedZone),
          fetchZonePrediction(selectedZone),
          fetchZoneFeatures(selectedZone),
          fetchZoneSuggestion(selectedZone),
          fetchZoneMetrics(selectedZone),
          fetchZoneAnomalies(selectedZone)
        ]);

        const [histRes, predRes, featRes, suggRes, metRes, anomRes] = results;
        const failedEndpoints = [];

        if (histRes.status === 'fulfilled') {
          setHistory(histRes.value.history);
        } else {
          setHistory([]);
          failedEndpoints.push('history');
          console.error("Failed to fetch history:", histRes.reason);
        }

        if (predRes.status === 'fulfilled') {
          setPrediction(predRes.value.predictions);
        } else {
          setPrediction([]);
          failedEndpoints.push('predict');
          console.error("Failed to fetch predictions:", predRes.reason);
        }

        if (featRes.status === 'fulfilled') {
          setFeatures(featRes.value.features);
        } else {
          setFeatures([]);
          failedEndpoints.push('features');
          console.error("Failed to fetch features:", featRes.reason);
        }

        if (suggRes.status === 'fulfilled') {
          setSuggestion(suggRes.value.suggestion);
        } else {
          setSuggestion('');
          failedEndpoints.push('suggestion');
          console.error("Failed to fetch suggestion:", suggRes.reason);
        }

        if (metRes.status === 'fulfilled') {
          setMetrics(metRes.value.metrics);
        } else {
          setMetrics(null);
          failedEndpoints.push('metrics');
          console.error("Failed to fetch metrics:", metRes.reason);
        }

        if (anomRes.status === 'fulfilled') {
          setAnomalies(anomRes.value.anomalies);
        } else {
          setAnomalies([]);
          failedEndpoints.push('anomalies');
          console.error("Failed to fetch anomalies:", anomRes.reason);
        }

        if (failedEndpoints.length > 0) {
          if (failedEndpoints.length === results.length) {
            setError(`Failed to connect to backend for ${selectedZone}. All requests failed: ${failedEndpoints.join(', ')}.`);
          } else {
            setError(`Notice: Failed to fetch [${failedEndpoints.join(', ')}] for ${selectedZone}. The rest of the dashboard remains operational.`);
          }
        }
      } catch (err) {
        setError(`Unexpected error loading data for ${selectedZone}: ${err.message || err}`)
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    
    loadZoneData()
  }, [selectedZone])

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <Zap className="logo-icon" size={32} />
          <h1>DISCOM Energy Dashboard</h1>
        </div>
        <p className="subtitle">AI-Powered Zone-wise Consumption Forecasting</p>
      </header>

      <main className="app-main">
        {error && <div className="error-banner">{error}</div>}
        
        <div className="view-toggle">
          <button 
            className={`toggle-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} /> Zone Dashboard
          </button>
          <button 
            className={`toggle-btn ${activeTab === 'comparison' ? 'active' : ''}`}
            onClick={() => setActiveTab('comparison')}
          >
            <BarChart2 size={18} /> Compare Zones
          </button>
          <button 
            className={`toggle-btn ${activeTab === 'peak-risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('peak-risk')}
          >
            <Activity size={18} /> Peak Load Risk
          </button>
          <button 
            className={`toggle-btn ${activeTab === 'ac-insight' ? 'active' : ''}`}
            onClick={() => setActiveTab('ac-insight')}
          >
            <Wind size={18} /> AC Insights
          </button>
        </div>

        {activeTab === 'comparison' && (
          <ZoneComparison 
            onSelectZone={(zoneId) => {
              setSelectedZone(zoneId);
              setActiveTab('dashboard');
            }} 
          />
        )}
        
        {activeTab === 'peak-risk' && (
          <PeakLoadComparison 
            onSelectZone={(zoneId) => {
              setSelectedZone(zoneId);
              setActiveTab('dashboard');
            }} 
          />
        )}

        {activeTab === 'ac-insight' && (
          <ACInsightComparison 
            onSelectZone={(zoneId) => {
              setSelectedZone(zoneId);
              setActiveTab('dashboard');
            }} 
          />
        )}

        {activeTab === 'dashboard' && (
          <>
            <section className="control-panel">
              <ZoneSelector 
                zones={zones} 
                selectedZone={selectedZone} 
                onSelectZone={setSelectedZone} 
              />
            </section>

            {loading && <div className="loader">Loading analytics...</div>}

            {!loading && selectedZone && (
              <div className="dashboard-grid">
                <div className="main-charts">
                  <HistoryChart data={history} anomalies={anomalies} />
                  <PredictionChart data={prediction} />
                  <AnomalyList anomalies={anomalies} />
                </div>
                
                <div className="side-panel">
                  <SuggestionCard suggestion={suggestion} metrics={metrics} />
                  <PeakLoadPanel zoneId={selectedZone} />
                  <ACInsightPanel zoneId={selectedZone} />
                  <WhatIfSimulator zoneId={selectedZone} />
                  <FeatureImportanceChart data={features} />
                </div>
              </div>
            )}
            
            {!selectedZone && !loading && (
              <div className="empty-state">
                <p>Please select a region above to view the forecast.</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
