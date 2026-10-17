import { useMemo, useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import FilterBar from './components/FilterBar';
import KpiCard from './components/KpiCard';
import RankingList from './components/RankingList';
import TimeSeriesChart from './charts/TimeSeriesChart';
import HourlyHeatmap from './charts/HourlyHeatmap';
import SankeyFlow from './charts/SankeyFlow';
import { useMonthly, useHourly, useFlow } from './hooks/useStats';
import styles from './App.module.css';

const fmtCompact = new Intl.NumberFormat('es-CO', { notation: 'compact' });

const iconProps = {
  viewBox: '0 0 24 24',
  width: 16,
  height: 16,
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

const IconPlay = (
  <svg {...iconProps}>
    <path d="M6 4l14 8-14 8z" />
  </svg>
);

const IconClock = (
  <svg {...iconProps}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </svg>
);

const IconMic = (
  <svg {...iconProps}>
    <path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z" />
    <path d="M5 11a7 7 0 0 0 14 0" />
    <path d="M12 18v3" />
  </svg>
);

export default function App() {
  const [filters, setFilters] = useState({ anio: null, artist_id: null, include_skips: false });

  const monthlyParams = { anio: filters.anio, artist_id: filters.artist_id, include_skips: filters.include_skips };
  const hourlyParams = { artist_id: filters.artist_id, include_skips: filters.include_skips };
  const flowParams = { limit: 20, include_skips: filters.include_skips };

  const monthly = useMonthly(monthlyParams);
  const hourly = useHourly(hourlyParams);
  const flow = useFlow(flowParams);

  const kpis = useMemo(() => {
    const rows = monthly.data ?? [];
    const totalEscuchas = rows.reduce((s, r) => s + (Number(r.total_escuchas) || 0), 0);
    const minutos = rows.reduce((s, r) => s + (Number(r.minutos_totales) || 0), 0);
    const byArtist = new Map();
    rows.forEach((r) => {
      const cur = byArtist.get(r.nombre_artista) ?? 0;
      byArtist.set(r.nombre_artista, cur + (Number(r.minutos_totales) || 0));
    });
    let top = '—';
    let topMin = 0;
    byArtist.forEach((m, a) => {
      if (m > topMin) { topMin = m; top = a; }
    });
    return { totalEscuchas, minutos, top, topMin };
  }, [monthly.data]);

  return (
    <div className={styles.layout}>
      <Sidebar />
      <main className={styles.main}>
        <Header />
        <FilterBar filters={filters} onChange={setFilters} />
        <section className={styles.kpis}>
          <KpiCard label="Reproducciones" value={kpis.totalEscuchas} icon={IconPlay} loading={monthly.loading} />
          <KpiCard label="Minutos" value={fmtCompact.format(kpis.minutos)} sub={`${kpis.minutos.toFixed(0)} min exactos`} icon={IconClock} loading={monthly.loading} />
          <KpiCard label="Top Artista" value={kpis.top} sub={`${kpis.topMin.toFixed(1)} min`} icon={IconMic} loading={monthly.loading} />
        </section>
        <section className={styles.grid2}>
          <TimeSeriesChart data={monthly.data ?? []} loading={monthly.loading} />
          <SankeyFlow data={flow.data ?? []} loading={flow.loading} />
        </section>
        <section className={styles.grid2}>
          <HourlyHeatmap data={hourly.data ?? []} loading={hourly.loading} />
          <RankingList filters={filters} />
        </section>
      </main>
    </div>
  );
}
