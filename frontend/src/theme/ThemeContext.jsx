import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { themes, themeVars } from './colors';

const ThemeContext = createContext({ themeName: 'dark', theme: themes.dark, toggleTheme: () => {} });

const STORAGE_KEY = 'spotify-analytics-theme';

function getInitialTheme() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {
    // localStorage no disponible (SSR/tests). Usa dark por defecto.
  }
  return 'dark';
}

export function ThemeProvider({ children }) {
  const [themeName, setThemeName] = useState(getInitialTheme);
  const theme = themes[themeName] ?? themes.dark;

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeName);
    const vars = themeVars(theme);
    Object.entries(vars).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
    try {
      localStorage.setItem(STORAGE_KEY, themeName);
    } catch {
      // Persitencia opcional. Sin localStorage el tema igual aplica.
    }
  }, [themeName, theme]);

  const toggleTheme = useCallback(() => {
    setThemeName((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const value = useMemo(() => ({ themeName, theme, toggleTheme }), [themeName, theme, toggleTheme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
