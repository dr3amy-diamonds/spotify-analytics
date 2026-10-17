import styles from './KpiCard.module.css';

const fmt = new Intl.NumberFormat('es-CO');

export default function KpiCard({ label, value, sub, loading, icon }) {
  return (
    <div className={styles.card}>
      <div className={styles.top}>
        {icon && <span className={styles.tile} aria-hidden="true">{icon}</span>}
        <span className={styles.label}>{label}</span>
      </div>
      {loading ? (
        <span className={styles.skeleton} aria-label="Cargando" />
      ) : (
        <strong className={styles.value} title={typeof value === 'string' ? value : undefined}>
          {typeof value === 'number' ? fmt.format(value) : value}
        </strong>
      )}
      {sub && <span className={styles.sub}>{sub}</span>}
    </div>
  );
}
