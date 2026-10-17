export const themes = {
  dark: {
    bg: '#121214',
    card: '#1E1E24',
    border: '#2A2A32',
    textPrimary: '#F4F4F6',
    textSecondary: '#A1A1AA',
    accentPrimary: '#FF5E97',
    accentSecondary: '#A78BFA',
    gradientD3: ['#1E1E24', '#4C1D95', '#FF5E97'],
  },
  light: {
    bg: '#FAFAFC',
    card: '#FFFFFF',
    border: '#E4E4E8',
    textPrimary: '#18181B',
    textSecondary: '#71717A',
    accentPrimary: '#E02567',
    accentSecondary: '#6D28D9',
    gradientD3: ['#F3F4F6', '#C084FC', '#E02567'],
  },
};

export const themeVars = (theme) => ({
  '--bg': theme.bg,
  '--card': theme.card,
  '--border': theme.border,
  '--text-primary': theme.textPrimary,
  '--text-secondary': theme.textSecondary,
  '--accent-primary': theme.accentPrimary,
  '--accent-secondary': theme.accentSecondary,
});
