export const themeStorageKey = 'visual-report-theme';

/** Runs in `<head>` before first paint, so a stored light theme never flashes dark. */
export const themeScript = `try{if(localStorage.getItem('${themeStorageKey}')==='light')document.documentElement.classList.remove('dark')}catch{}`;
