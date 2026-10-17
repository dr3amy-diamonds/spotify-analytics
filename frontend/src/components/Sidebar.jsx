import styles from './Sidebar.module.css';

const ITEMS = ['Overview', 'Songs', 'Albums', 'Members', 'Charts', 'Playlists', 'About'];

export default function Sidebar() {
  return (
    <nav className={styles.sidebar} aria-label="Navegación principal">
      <div className={styles.brand}>
        <span className={styles.mark} aria-hidden="true">SA</span>
        <div className={styles.brandText}>
          <span className={styles.brandName}>Spotify Analytics</span>
          <span className={styles.brandSub}>Gold Layer</span>
        </div>
      </div>
      {ITEMS.map((item) => (
        <span key={item} className={item === 'Overview' ? `${styles.item} ${styles.active}` : styles.item}>
          {item}
        </span>
      ))}
    </nav>
  );
}
