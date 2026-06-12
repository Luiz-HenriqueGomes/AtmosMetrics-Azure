import { useEffect, useState } from 'react';
import { Thermometer, Filter, X, Download, ThermometerSun, Snowflake } from 'lucide-react';
import { api, type ClimaItem, type PaisOut, type ContinenteOut } from '../services/api';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import Papa from 'papaparse';
import './FocosPage.css';

const PAGE_SIZE = 1000;

const formatLocationName = (str: string | null) => {
  if (!str) return '';
  const prepositions = ['de', 'da', 'do', 'das', 'dos', 'e'];
  return str.toLowerCase().split(' ').map((word, index) => {
    if (index > 0 && prepositions.includes(word)) return word;
    return word.charAt(0).toUpperCase() + word.slice(1);
  }).join(' ');
};

export default function FocosPage() {
  const [data, setData] = useState<ClimaItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [filtersOpen, setFiltersOpen] = useState(false);

  // Agrupa os dados processados na página atual por país
  const groupedData = data.reduce((acc, item) => {
    const country = item.pais || 'Desconhecido';
    if (!acc[country]) acc[country] = [];
    acc[country].push(item);
    return acc;
  }, {} as Record<string, ClimaItem[]>);

  // Filtros
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [continente, setContinente] = useState('');
  const [pais, setPais] = useState('');

  // Opções para selects
  const [paises, setPaises] = useState<PaisOut[]>([]);
  const [continentes, setContinentes] = useState<ContinenteOut[]>([]);

  // Carrega opções de filtro ao montar
  useEffect(() => {
    api.getPaises().then(setPaises).catch(() => {});
    api.getContinentes().then(setContinentes).catch(() => {});
  }, []);

  // Países filtrados pelo continente selecionado
  const paisesFiltrados = continente
    ? paises.filter(p => p.continente === continente)
    : paises;

  // Carrega dados quando filtros ou offset mudam
  useEffect(() => {
    setLoading(true);
    setError(null);

    const filters = {
      limit: PAGE_SIZE,
      offset,
      ...(dataInicio && { data_inicio: dataInicio }),
      ...(dataFim && { data_fim: dataFim }),
      ...(pais && { pais }),
      ...(continente && { continente }),
    };

    api.getClimaExtremas(filters)
      .then(setData)
      .catch(() => setError('Não foi possível carregar as temperaturas extremas.'))
      .finally(() => setLoading(false));
  }, [offset, dataInicio, dataFim, pais, continente]);

  const handleFilter = () => {
    setOffset(0); // Reset para página 1 ao filtrar
  };

  const clearFilters = () => {
    setDataInicio('');
    setDataFim('');
    setContinente('');
    setPais('');
    setOffset(0);
  };

  // Ao mudar continente, reseta o país
  const handleContinenteChange = (value: string) => {
    setContinente(value);
    setPais('');
    handleFilter();
  };

  const exportPDF = () => {
    if (data.length === 0) return;
    const doc = new jsPDF();
    doc.text('Relatório de Temperaturas Extremas - AtmosMetrics', 14, 15);
    
    const tableData = data.map(item => [
      item.data_completa ?? '-',
      item.pais ?? '-',
      item.continente ?? '-',
      (item.pais === 'Brasil' && !item.municipio?.startsWith('Grid')) ? (item.municipio ?? '-') : '—',
      item.temperatura_max ? `${Number(item.temperatura_max).toFixed(1)}°C` : '-',
      item.temperatura_min ? `${Number(item.temperatura_min).toFixed(1)}°C` : '-',
      item.velocidade_vento ? `${Number(item.velocidade_vento).toFixed(1)} km/h` : '-'
    ]);

    autoTable(doc, {
      head: [['Data', 'País', 'Continente', 'Município', 'Temp Máx', 'Temp Mín', 'Vento']],
      body: tableData,
      startY: 20,
      styles: { fontSize: 8 },
    });

    doc.save('atmosmetrics_temperaturas_extremas.pdf');
  };

  const exportCSV = () => {
    if (data.length === 0) return;
    const csvData = data.map(item => ({
      Data: item.data_completa,
      Pais: item.pais,
      Continente: item.continente,
      Municipio: (item.pais === 'Brasil' && !item.municipio?.startsWith('Grid')) ? item.municipio : '—',
      Latitude: item.latitude,
      Longitude: item.longitude,
      TempMax: item.temperatura_max,
      TempMin: item.temperatura_min,
      Precipitacao: item.precipitacao_mm,
      Vento: item.velocidade_vento
    }));
    const csv = Papa.unparse(csvData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'atmosmetrics_temperaturas_extremas.csv';
    link.click();
  };

  const hasActiveFilters = dataInicio || dataFim || pais || continente;
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;

  // Cálculos de KPI
  const maxTempObj = data.length > 0 ? data.reduce((prev, current) => (Number(prev.temperatura_max) > Number(current.temperatura_max)) ? prev : current) : null;
  const minTempObj = data.length > 0 ? data.reduce((prev, current) => (Number(prev.temperatura_min) < Number(current.temperatura_min)) ? prev : current) : null;
  const totalAlerts = data.length;

  return (
    <div className="focos-page">
      {/* Header */}
      <div className="focos-header">
        <div>
          <h1 className="focos-title">Temperaturas Extremas</h1>
          <p className="focos-subtitle">
            Monitoramento global de ondas de calor (≥ 35°C) e frio extremo (≤ 0°C)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button className="focos-filter-toggle" onClick={exportCSV} disabled={data.length === 0 || loading} title="Exportar para CSV">
            <Download size={14} /> CSV
          </button>
          <button className="focos-filter-toggle" onClick={exportPDF} disabled={data.length === 0 || loading} title="Exportar para PDF">
            <Download size={14} /> PDF
          </button>
          <button
            className={`focos-filter-toggle ${filtersOpen ? 'active' : ''}`}
            onClick={() => setFiltersOpen(!filtersOpen)}
          >
            <Filter size={14} />
            Filtros
            {hasActiveFilters && <span className="filter-badge" />}
          </button>
        </div>
      </div>

      {/* Filtros */}
      {filtersOpen && (
        <div className="focos-filters panel">
          <div className="filters-grid">
            <div className="filter-group">
              <label className="filter-label">Continente</label>
              <select className="filter-input" value={continente} onChange={e => handleContinenteChange(e.target.value)}>
                <option value="">Todos</option>
                {continentes.map(c => (
                  <option key={c.continente} value={c.continente}>{c.continente}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label className="filter-label">País</label>
              <select className="filter-input" value={pais} onChange={e => { setPais(e.target.value); handleFilter(); }}>
                <option value="">Todos</option>
                {paisesFiltrados.map(p => (
                  <option key={p.pais} value={p.pais}>{p.pais}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label className="filter-label">Data Início</label>
              <input
                className="filter-input"
                type="date"
                value={dataInicio}
                onChange={e => { setDataInicio(e.target.value); handleFilter(); }}
              />
            </div>

            <div className="filter-group">
              <label className="filter-label">Data Fim</label>
              <input
                className="filter-input"
                type="date"
                value={dataFim}
                onChange={e => { setDataFim(e.target.value); handleFilter(); }}
              />
            </div>

            {hasActiveFilters && (
              <div className="filter-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button className="filter-clear" onClick={clearFilters}>
                  <X size={12} />
                  Limpar filtros
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Erro */}
      {error && (
        <div className="error-banner">
          <Thermometer size={16} />
          {error}
        </div>
      )}

      {/* KPIs */}
      <div className="focos-kpi-row">
        <div className="kpi-card hot">
          <div className="kpi-icon"><ThermometerSun size={24} /></div>
          <div className="kpi-content">
            <span className="kpi-label">Pico de Calor</span>
            <span className="kpi-value">{maxTempObj ? `${Number(maxTempObj.temperatura_max).toFixed(1)}°C` : '—'}</span>
            <span className="kpi-desc">{maxTempObj ? formatLocationName(maxTempObj.municipio || maxTempObj.pais) : 'Sem dados'}</span>
          </div>
        </div>
        <div className="kpi-card cold">
          <div className="kpi-icon"><Snowflake size={24} /></div>
          <div className="kpi-content">
            <span className="kpi-label">Pico de Frio</span>
            <span className="kpi-value">{minTempObj ? `${Number(minTempObj.temperatura_min).toFixed(1)}°C` : '—'}</span>
            <span className="kpi-desc">{minTempObj ? formatLocationName(minTempObj.municipio || minTempObj.pais) : 'Sem dados'}</span>
          </div>
        </div>
        <div className="kpi-card neutral">
          <div className="kpi-icon"><Thermometer size={24} /></div>
          <div className="kpi-content">
            <span className="kpi-label">Alertas Globais</span>
            <span className="kpi-value">{totalAlerts}</span>
            <span className="kpi-desc">Cidades em extremos listadas</span>
          </div>
        </div>
      </div>

      {/* Grid Bento Box */}
      <div className="bento-container panel">
        <div className="focos-table-header">
          <span className="focos-table-count">
            {loading ? 'Analisando satélites...' : `${data.length} localidades extremas mapeadas na página`}
            {hasActiveFilters && ' (com filtro ativo)'}
          </span>
          <span className="focos-table-page">Página {currentPage}</span>
        </div>

        <div className="bento-grid">
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', gridColumn: '1 / -1' }}>
              Carregando dados globais...
            </div>
          ) : data.length === 0 ? (
            <div className="focos-empty" style={{ gridColumn: '1 / -1' }}>
              <Thermometer size={20} />
              <span>Nenhum registro extremo encontrado com os filtros atuais.</span>
            </div>
          ) : (
            Object.entries(groupedData)
              .sort(([countryA], [countryB]) => {
                if (countryA === 'Antártica') return 1;
                if (countryB === 'Antártica') return -1;
                return countryA.localeCompare(countryB);
              })
              .map(([country, items]) => {
                // Filtra cidades duplicadas no mesmo país para não repetir ex: "Antártica" 10 vezes
                const uniqueItemsMap = new Map();
                for (const item of items) {
                  const cityName = (item.pais === 'Brasil' && !item.municipio?.startsWith('Grid')) 
                    ? formatLocationName(item.municipio) 
                    : formatLocationName(item.pais);
                  
                  // Se a cidade já existe, mantemos a que tem a temperatura mais extrema (maior max ou menor min)
                  if (uniqueItemsMap.has(cityName)) {
                    const existing = uniqueItemsMap.get(cityName);
                    const existingMax = Number(existing.temperatura_max) || 0;
                    const existingMin = Number(existing.temperatura_min) || 0;
                    const itemMax = Number(item.temperatura_max) || 0;
                    const itemMin = Number(item.temperatura_min) || 0;
                    
                    const existingExtreme = Math.max(Math.abs(existingMax), Math.abs(existingMin));
                    const itemExtreme = Math.max(Math.abs(itemMax), Math.abs(itemMin));
                    
                    if (itemExtreme > existingExtreme) {
                      uniqueItemsMap.set(cityName, { ...item, cityName });
                    }
                  } else {
                    uniqueItemsMap.set(cityName, { ...item, cityName });
                  }
                }
                const uniqueItems = Array.from(uniqueItemsMap.values());

                // Verifica a tendência do país (se tem mais frio ou calor)
                const hotCount = uniqueItems.filter(i => Number(i.temperatura_max) >= 35).length;
                const coldCount = uniqueItems.filter(i => Number(i.temperatura_min) <= 0).length;
                const theme = hotCount > coldCount ? 'theme-hot' : (coldCount > hotCount ? 'theme-cold' : 'theme-neutral');

                return (
                  <div key={country} className={`bento-card ${theme}`}>
                    <div className="bento-card-header">
                      <h3 className="bento-country">{country}</h3>
                      <span className="bento-badge">{uniqueItems.length} locais</span>
                    </div>
                    <div className="bento-card-body">
                      {uniqueItems.map(item => {
                        const maxT = Number(item.temperatura_max) || 0;
                        const minT = Number(item.temperatura_min) || 0;
                        const cityName = item.cityName;

                        // Calcula % da barra considerando um range de -20 a 50
                        const rangeMin = -20;
                        const rangeMax = 50;
                        const rangeTotal = rangeMax - rangeMin;
                        
                        const isHot = maxT >= 35;
                        const isCold = minT <= 0;
                        const displayTemp = isHot ? maxT : (isCold ? minT : Math.max(maxT, minT));
                        
                        const styleClass = displayTemp >= 28 ? 'hot' : (displayTemp <= 15 ? 'cold' : 'neutral');
                        
                        let pct = ((displayTemp - rangeMin) / rangeTotal) * 100;
                        if (pct < 0) pct = 0;
                        if (pct > 100) pct = 100;

                        return (
                          <div key={item.id_clima} className="bento-city-item">
                            <div className="bento-city-info">
                              <span className="city-name" title={cityName}>{cityName}</span>
                              <span className={`city-temp ${styleClass}-text`}>
                                {displayTemp.toFixed(1)}°C
                              </span>
                            </div>
                            <div className="temp-bar-bg">
                              <div 
                                className={`temp-bar-fill fill-${styleClass}`} 
                                style={{ width: `${pct}%` }} 
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
            })
          )}
        </div>

      </div>
    </div>
  );
}
