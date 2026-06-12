// ============================================================
// AtmosMetrics — Utility Functions
// Copied from page components for testability.
// DO NOT remove the originals from the page components.
// ============================================================

/**
 * Formats a location name to Title Case, keeping Portuguese
 * prepositions (de, da, do, das, dos, e) in lowercase.
 * Copied from DashboardPage.tsx / FocosPage.tsx / QualidadeArPage.tsx.
 */
export const formatLocationName = (str: string | null): string => {
  if (!str) return '';
  const prepositions = ['de', 'da', 'do', 'das', 'dos', 'e'];
  return str.toLowerCase().split(' ').map((word, index) => {
    if (index > 0 && prepositions.includes(word)) return word;
    return word.charAt(0).toUpperCase() + word.slice(1);
  }).join(' ');
};

/**
 * Returns an EPA-style AQI status object (class, label, color)
 * based on the numeric AQI value.
 * Copied from QualidadeArPage.tsx.
 */
export const getAqiStatus = (aqi: number): { class: string; label: string; color: string } => {
  if (aqi <= 50) return { class: 'good', label: 'Bom', color: '#10b981' };
  if (aqi <= 100) return { class: 'moderate', label: 'Moderado', color: '#facc15' };
  if (aqi <= 150) return { class: 'sensitive', label: 'Insalubre p/ Sensíveis', color: '#f97316' };
  if (aqi <= 200) return { class: 'unhealthy', label: 'Insalubre', color: '#ef4444' };
  if (aqi <= 300) return { class: 'very', label: 'Muito Insalubre', color: '#8b5cf6' };
  return { class: 'hazardous', label: 'Perigoso', color: '#9f1239' };
};

/**
 * Returns a hex color string based on temperature:
 * - <= 20 → blue (#3b82f6)
 * - >= 28 → red (#ef4444)
 * - between → orange (#f59e0b)
 * Copied from DashboardPage.tsx.
 */
export const getTempColor = (temp: number): string => {
  if (temp <= 20) return '#3b82f6'; // Azul
  if (temp >= 28) return '#ef4444'; // Vermelho
  return '#f59e0b'; // Laranja
};

/**
 * Converts a 2-letter ISO country code into a flag emoji.
 * Returns 🌍 for invalid or missing codes.
 * Copied from LocalidadesPage.tsx.
 */
export function flagEmoji(iso: string | null): string {
  if (!iso || iso.length !== 2) return '🌍';
  const codePoints = [...iso.toUpperCase()].map(c => 127397 + c.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}
