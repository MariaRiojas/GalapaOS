import { useState, useEffect } from 'react';

function useJsonData(path) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(path)
      .then(r => {
        if (!r.ok) throw new Error(`Failed to load ${path}`);
        return r.json();
      })
      .then(setData)
      .catch(setError);
  }, [path]);

  return { data, error };
}

export function useForecast() {
  return useJsonData('/data/forecast.json');
}

export function useStations() {
  return useJsonData('/data/stations.json');
}

export function useHistorical() {
  return useJsonData('/data/historical.json');
}

export function useModelInfo() {
  return useJsonData('/data/model_info.json');
}
