import { useArtists } from '../hooks/useStats';
import styles from './FilterBar.module.css';

const YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];

export default function FilterBar({ filters, onChange }) {
  const { data: artists = [], loading } = useArtists({ limit: 200 });

  const update = (patch) => onChange({ ...filters, ...patch });

  return (
    <div className={styles.bar}>
      <label className={styles.field}>
        Año
        <select
          value={filters.anio ?? ''}
          onChange={(e) => update({ anio: e.target.value === '' ? null : Number(e.target.value) })}
        >
          <option value="">Todos</option>
          {YEARS.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        Artista
        <select
          value={filters.artist_id ?? ''}
          onChange={(e) => update({ artist_id: e.target.value === '' ? null : Number(e.target.value) })}
          disabled={loading}
        >
          <option value="">Todos</option>
          {artists.map((a) => (
            <option key={a.artist_id} value={a.artist_id}>{a.nombre_artista}</option>
          ))}
        </select>
      </label>

      <label className={styles.switch}>
        <input
          type="checkbox"
          checked={!!filters.include_skips}
          onChange={(e) => update({ include_skips: e.target.checked })}
          aria-label="Incluir skips"
        />
        Incluir skips
      </label>
    </div>
  );
}
