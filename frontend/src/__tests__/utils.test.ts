import { describe, it, expect } from 'vitest';
import { formatLocationName, getAqiStatus, getTempColor, flagEmoji } from '../utils';

// ============================================================
// formatLocationName
// ============================================================
describe('formatLocationName', () => {
  it('returns empty string for null input', () => {
    expect(formatLocationName(null)).toBe('');
  });

  it('returns empty string for empty string input', () => {
    expect(formatLocationName('')).toBe('');
  });

  it('converts a simple word to Title Case', () => {
    expect(formatLocationName('brasilia')).toBe('Brasilia');
  });

  it('converts multiple words to Title Case', () => {
    expect(formatLocationName('SAO PAULO')).toBe('Sao Paulo');
  });

  it('keeps Portuguese prepositions lowercase when not the first word', () => {
    expect(formatLocationName('RIO DE JANEIRO')).toBe('Rio de Janeiro');
  });

  it('capitalizes preposition when it is the first word', () => {
    // "de" at position 0 should still be capitalised
    expect(formatLocationName('de janeiro')).toBe('De Janeiro');
  });

  it('handles all Portuguese prepositions correctly', () => {
    expect(formatLocationName('FEIRA DE SANTANA')).toBe('Feira de Santana');
    expect(formatLocationName('VARGEM DA SERRA')).toBe('Vargem da Serra');
    expect(formatLocationName('RIO DO SUL')).toBe('Rio do Sul');
    expect(formatLocationName('CAMPOS DAS GOYTACAZES')).toBe('Campos das Goytacazes');
    expect(formatLocationName('ANGRA DOS REIS')).toBe('Angra dos Reis');
    expect(formatLocationName('TRINIDADE E TOBAGO')).toBe('Trinidade e Tobago');
  });
});

// ============================================================
// getAqiStatus
// ============================================================
describe('getAqiStatus', () => {
  it('returns "Bom" for AQI 0-50', () => {
    const result = getAqiStatus(25);
    expect(result.class).toBe('good');
    expect(result.label).toBe('Bom');
    expect(result.color).toBe('#10b981');
  });

  it('returns "Bom" for boundary AQI = 50', () => {
    expect(getAqiStatus(50).class).toBe('good');
  });

  it('returns "Moderado" for AQI 51-100', () => {
    const result = getAqiStatus(75);
    expect(result.class).toBe('moderate');
    expect(result.label).toBe('Moderado');
    expect(result.color).toBe('#facc15');
  });

  it('returns "Moderado" for boundary AQI = 100', () => {
    expect(getAqiStatus(100).class).toBe('moderate');
  });

  it('returns "Insalubre p/ Sensíveis" for AQI 101-150', () => {
    const result = getAqiStatus(120);
    expect(result.class).toBe('sensitive');
    expect(result.label).toBe('Insalubre p/ Sensíveis');
    expect(result.color).toBe('#f97316');
  });

  it('returns "Insalubre" for AQI 151-200', () => {
    const result = getAqiStatus(180);
    expect(result.class).toBe('unhealthy');
    expect(result.label).toBe('Insalubre');
    expect(result.color).toBe('#ef4444');
  });

  it('returns "Muito Insalubre" for AQI 201-300', () => {
    const result = getAqiStatus(250);
    expect(result.class).toBe('very');
    expect(result.label).toBe('Muito Insalubre');
    expect(result.color).toBe('#8b5cf6');
  });

  it('returns "Perigoso" for AQI 301+', () => {
    const result = getAqiStatus(400);
    expect(result.class).toBe('hazardous');
    expect(result.label).toBe('Perigoso');
    expect(result.color).toBe('#9f1239');
  });

  it('returns "Perigoso" for extreme AQI = 500', () => {
    expect(getAqiStatus(500).class).toBe('hazardous');
  });
});

// ============================================================
// getTempColor
// ============================================================
describe('getTempColor', () => {
  it('returns blue for cold temperatures (<=20)', () => {
    expect(getTempColor(10)).toBe('#3b82f6');
    expect(getTempColor(20)).toBe('#3b82f6');
    expect(getTempColor(-5)).toBe('#3b82f6');
  });

  it('returns red for hot temperatures (>=28)', () => {
    expect(getTempColor(28)).toBe('#ef4444');
    expect(getTempColor(35)).toBe('#ef4444');
    expect(getTempColor(50)).toBe('#ef4444');
  });

  it('returns orange for moderate temperatures (21-27)', () => {
    expect(getTempColor(21)).toBe('#f59e0b');
    expect(getTempColor(25)).toBe('#f59e0b');
    expect(getTempColor(27)).toBe('#f59e0b');
  });
});

// ============================================================
// flagEmoji
// ============================================================
describe('flagEmoji', () => {
  it('returns Brazilian flag for "BR"', () => {
    const flag = flagEmoji('BR');
    // Brazil flag = 🇧🇷
    expect(flag).toBe('🇧🇷');
  });

  it('returns US flag for "US"', () => {
    const flag = flagEmoji('US');
    // US flag = 🇺🇸
    expect(flag).toBe('🇺🇸');
  });

  it('handles lowercase input by converting to uppercase', () => {
    const flag = flagEmoji('br');
    expect(flag).toBe('🇧🇷');
  });

  it('returns globe emoji for null input', () => {
    expect(flagEmoji(null)).toBe('🌍');
  });

  it('returns globe emoji for invalid length input', () => {
    expect(flagEmoji('A')).toBe('🌍');
    expect(flagEmoji('ABC')).toBe('🌍');
  });

  it('returns globe emoji for empty string', () => {
    expect(flagEmoji('')).toBe('🌍');
  });
});
