import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000', timeout: 10000 });

const cleanParams = (params = {}) => {
  const out = {};
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') out[k] = v;
  });
  return out;
};

export const getMonthly = (params, signal) =>
  api.get('/stats/monthly', { params: cleanParams(params), signal }).then((r) => r.data);
export const getHourly = (params, signal) =>
  api.get('/stats/hourly', { params: cleanParams(params), signal }).then((r) => r.data);
export const getFlow = (params, signal) =>
  api.get('/stats/flow', { params: cleanParams(params), signal }).then((r) => r.data);
export const getArtists = (params, signal) =>
  api.get('/stats/artists', { params: cleanParams(params), signal }).then((r) => r.data);
export const getTopTracks = (params, signal) =>
  api.get('/stats/top-tracks', { params: cleanParams(params), signal }).then((r) => r.data);
export const getHealth = (signal) => api.get('/health', { signal }).then((r) => r.data);

export default api;
