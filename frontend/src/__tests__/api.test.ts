import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ============================================================
// API Service Tests
// Tests the fetchAPI base function indirectly through the
// public api methods exported from src/services/api.ts.
// ============================================================

// We need to mock fetch before importing the module
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Import after stubbing fetch
const { api } = await import('../services/api');

const BASE_URL = 'http://localhost:8000/api/v1';

beforeEach(() => {
  mockFetch.mockReset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('api.getResumo (fetchAPI wrapper)', () => {
  it('returns parsed JSON on successful response', async () => {
    const mockData = {
      total_focos: 1234,
      por_uf: [],
      por_bioma: [],
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await api.getResumo();
    expect(result).toEqual(mockData);
    expect(mockFetch).toHaveBeenCalledWith(`${BASE_URL}/anomalias/resumo`);
  });

  it('throws error when response is not ok', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });

    await expect(api.getResumo()).rejects.toThrow('Erro na API: 500 Internal Server Error');
  });

  it('propagates network errors', async () => {
    mockFetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));

    await expect(api.getResumo()).rejects.toThrow('Failed to fetch');
  });
});

describe('api.getLocalidades', () => {
  it('calls the correct endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    await api.getLocalidades();
    expect(mockFetch).toHaveBeenCalledWith(`${BASE_URL}/localidades/`);
  });
});

describe('api.getAnomalias', () => {
  it('builds query params with defaults', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    await api.getAnomalias();
    const calledUrl = mockFetch.mock.calls[0][0] as string;
    expect(calledUrl).toContain('/anomalias/?');
    expect(calledUrl).toContain('limit=100');
    expect(calledUrl).toContain('offset=0');
  });

  it('includes custom filter parameters', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    await api.getAnomalias({ uf: 'SP', bioma: 'Cerrado', limit: 50, offset: 10 });
    const calledUrl = mockFetch.mock.calls[0][0] as string;
    expect(calledUrl).toContain('uf=SP');
    expect(calledUrl).toContain('bioma=Cerrado');
    expect(calledUrl).toContain('limit=50');
    expect(calledUrl).toContain('offset=10');
  });
});

describe('api.getClima', () => {
  it('builds query params for clima endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    await api.getClima({ pais: 'Brasil', limit: 200 });
    const calledUrl = mockFetch.mock.calls[0][0] as string;
    expect(calledUrl).toContain('/clima/?');
    expect(calledUrl).toContain('pais=Brasil');
    expect(calledUrl).toContain('limit=200');
  });
});

describe('api.getResumoClima', () => {
  it('calls the correct endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ temperatura_media_global: '25.0', total_registros: 10, por_continente: [], por_pais: [] }),
    });

    await api.getResumoClima();
    expect(mockFetch).toHaveBeenCalledWith(`${BASE_URL}/clima/resumo`);
  });
});

describe('api.getQualidadeAr', () => {
  it('builds query params for air quality endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([]),
    });

    await api.getQualidadeAr({ continente: 'Europa' });
    const calledUrl = mockFetch.mock.calls[0][0] as string;
    expect(calledUrl).toContain('/qualidade-ar/?');
    expect(calledUrl).toContain('continente=Europa');
  });
});
