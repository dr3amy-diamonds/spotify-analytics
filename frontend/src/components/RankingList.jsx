import { useTopTracks } from '../hooks/useStats';
import styles from './RankingList.module.css';

const fmt = new Intl.NumberFormat('es-CO');

export default function RankingList({ filters }) {
  const { data = [], loading, error } = useTopTracks({ limit: 10, anio: filters.anio, artist_id: filters.artist_id, include_skips: filters.include_skips });
  const max = Math.max(1, ...data.map((d) => Number(d.total_escuchas) || 0));

  if (loading) return <div className={styles.card}>Cargando ranking…</div>;
  if (error) return <div className={styles.card}>Error al cargar el ranking.</div>;
  if (!data.length) return <div className={styles.card}>Sin datos para filtros actuales.</div>;

  return (
    <div className={styles.card}>
      <div className={styles.head}>
        <h2 className={styles.title}>Top Tracks</h2>
        <span className={styles.hint}>Top 10 por escuchas</span>
      </div>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.rank}>#</th>
              <th>Canción</th>
              <th>Artista</th>
              <th className={styles.num}>Escuchas</th>
              <th className={styles.num}>Min</th>
              <th className={styles.barHead}>Proporción</th>
            </tr>
          </thead>
          <tbody>
            {data.map((t, i) => (
              <tr key={t.track_id ?? i}>
                <td className={styles.rank}>{i + 1}</td>
                <td className={styles.song} title={t.nombre_cancion}>{t.nombre_cancion}</td>
                <td className={styles.artist} title={t.nombre_artista}>{t.nombre_artista}</td>
                <td className={styles.num}>{fmt.format(Number(t.total_escuchas))}</td>
                <td className={styles.num}>{fmt.format(Number(t.minutos_totales))}</td>
                <td className={styles.barCell}>
                  <div className={styles.barRow} title={`${t.nombre_cancion}: ${t.total_escuchas}`}>
                    <div className={styles.bar} style={{ width: `${(Number(t.total_escuchas) / max) * 100}%` }} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
