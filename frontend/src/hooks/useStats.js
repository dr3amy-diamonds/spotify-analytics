import { useEffect, useState } from 'react';
import { getMonthly, getHourly, getFlow, getArtists, getTopTracks } from '../api/statsApi';

function useQuery(fetcher, params) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const key = JSON.stringify(params ?? {});

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setLoading(true);
    setError(null);

    fetcher(JSON.parse(key), controller.signal)
      .then((res) => {
        if (active) setData(res ?? []);
      })
      .catch((err) => {
        if (err?.code === 'ERR_CANCELED' || err?.name === 'CanceledError') return;
        if (active) setError(err);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return { data, loading, error };
}

export const useMonthly = (params) => useQuery(getMonthly, params);
export const useHourly = (params) => useQuery(getHourly, params);
export const useFlow = (params) => useQuery(getFlow, params);
export const useArtists = (params) => useQuery(getArtists, params);
export const useTopTracks = (params) => useQuery(getTopTracks, params);

export default useQuery;
