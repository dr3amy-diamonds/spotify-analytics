import { useEffect, useState } from 'react';
import { getHealth } from '../api/statsApi';
import { useTheme } from '../theme/ThemeContext';
import styles from './Header.module.css';

export default function Header() {
  const { themeName, toggleTheme } = useTheme();
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    const check = async () => {
      try {
        const res = await getHealth(controller.signal);
        if (active) setStatus(res?.database_connected ? 'connected' : 'disconnected');
      } catch {
        if (active) setStatus('disconnected');
      }
    };

    check();
    const id = setInterval(check, 30000);
    return () => {
      active = false;
      controller.abort();
      clearInterval(id);
    };
  }, []);

  return (
    <header className={styles.header}>
      <div>
        <h1 className={styles.title}>Spotify Analytics</h1>
        <p className={styles.subtitle}>Historial de reproducción 2019–2026 · Capa Gold</p>
      </div>
      <div className={styles.actions}>
        <span
          className={`${styles.dot} ${styles[status]}`}
          title={status === 'connected' ? 'Conectado' : status === 'disconnected' ? 'Desconectado' : 'Cargando'}
        />
        <button type="button" className={styles.toggle} onClick={toggleTheme} aria-label="Cambiar tema">
          {themeName === 'dark' ? 'Light' : 'Dark'}
        </button>
      </div>
    </header>
  );
}
