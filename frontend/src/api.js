import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const fetchZones = async () => {
  const response = await axios.get(`${API_URL}/zones`);
  return response.data;
};

export const fetchZoneHistory = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/history`);
  return response.data;
};

export const fetchZonePrediction = async (zoneId, days = 7) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/predict?days=${days}`);
  return response.data;
};

export const fetchZoneFeatures = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/features`);
  return response.data;
};

export const fetchZoneSuggestion = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/suggestion`);
  return response.data;
};

export const fetchZoneMetrics = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/metrics`);
  return response.data;
};

export const fetchZoneAnomalies = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/anomalies`);
  return response.data;
};

export const simulateZonePrediction = async (zoneId, inputs) => {
  const response = await axios.post(`${API_URL}/zones/${zoneId}/simulate`, inputs);
  return response.data;
};

export const fetchZoneComparison = async (sortBy = 'change') => {
  const response = await axios.get(`${API_URL}/zones/comparison?sort_by=${sortBy}`);
  return response.data;
};

export const fetchZonePeakLoad = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/peak-load`);
  return response.data;
};

export const fetchZonePeakLoadSummary = async () => {
  const response = await axios.get(`${API_URL}/zones/peak-load/summary`);
  return response.data;
};

export const fetchZoneACInsight = async (zoneId) => {
  const response = await axios.get(`${API_URL}/zones/${zoneId}/ac-insight`);
  return response.data;
};

export const fetchZoneACInsightSummary = async () => {
  const response = await axios.get(`${API_URL}/zones/ac-insight/summary`);
  return response.data;
};
