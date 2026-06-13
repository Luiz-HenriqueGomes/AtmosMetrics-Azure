import { useEffect, useState, useMemo } from 'react';
import { MapPin, AlertCircle, Thermometer, ThermometerSun, Snowflake } from 'lucide-react';
import { MapContainer, TileLayer, Popup, useMap, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import StatCard from '../components/StatCard';
import MapErrorBoundary from '../components/MapErrorBoundary';
import { api, type ClimaItem, type ResumoClimaResponse, type AnomaliaItem } from '../services/api';
import './DashboardPage.css';

// Utilitário para formatar nomes de localidades (Title Case)
const formatLocationName = (str: string | null) => {
  if (!str) return '';
  const prepositions = ['de', 'da', 'do', 'das', 'dos', 'e'];
  return str.toLowerCase().split(' ').map((word, index) => {
    if (index > 0 && prepositions.includes(word)) return word;
    return word.charAt(0).toUpperCase() + word.slice(1);
  }).join(' ');
};

// Utilitário para pegar o nome correto a exibir (Município se Brasil, caso contrário País)
const getLocationLabel = (item: any) => {
  // Se for um foco de calor do INPE ou uma localidade brasileira válida
  if (item.municipio && !item.municipio.startsWith('Grid')) {
    // Se tiver estado (INPE retorna), mostra 'Cidade - UF'
    if (item.estado && item.estado.length === 2) {
      return formatLocationName(item.municipio) + ' - ' + item.estado.toUpperCase();
    }
    return formatLocationName(item.municipio);
  }
  // Se for uma localidade global (tem país)
  if (item.pais) {
    return formatLocationName(item.pais);
  }
  return 'Local Desconhecido';
};

// Componente auxiliar para controlar o mapa dinamicamente
const MapController = ({ center, zoom }: { center: [number, number] | null, zoom: number }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, zoom, { duration: 1.5 });
    }
  }, [center, zoom, map]);
  return null;
};

// Utilitário para determinar cor da temperatura
const getTempColor = (temp: number) => {
  if (temp <= 20) return '#3b82f6'; // Azul
  if (temp >= 28) return '#ef4444'; // Vermelho
  return '#f59e0b'; // Laranja
};



export default function DashboardPage() {
  const [anomalias, setAnomalias] = useState<ClimaItem[]>([]);
  const [focosCalor, setFocosCalor] = useState<AnomaliaItem[]>([]);
  const [resumoClima, setResumoClima] = useState<ResumoClimaResponse | null>(null);
  const [mapFocus, setMapFocus] = useState<[number, number] | null>(null);
  const [activeFoco, setActiveFoco] = useState<ClimaItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [extremas, clima, focos] = await Promise.all([
          api.getClimaExtremas({ limit: 500 }),
          api.getResumoClima(),
          api.getAnomalias({ limit: 1000 })
        ]);
        // Protege contra respostas inesperadas da API
        setAnomalias(Array.isArray(extremas) ? extremas : []);
        setFocosCalor(Array.isArray(focos) ? focos : []);
        setResumoClima(clima && typeof clima === 'object' && 'total_registros' in clima ? clima : null);
      } catch {
        setError('Não foi possível carregar os dados climáticos. Execute o ETL ou verifique a API.');
      }

      try {
        await api.getResumoQualidadeAr();
      } catch {
        // API de qualidade do ar pode não estar configurada ainda
      }

      setLoading(false);
    };

    loadData();
  }, []);

  // Filtra dados únicos para não repetir a mesma cidade/país no Top 10
  const getUniqueTop = (list: ClimaItem[], type: 'max' | 'min') => {
    const unique = new Map();
    list.forEach(item => {
      if ((type === 'max' && item.temperatura_max === null) || (type === 'min' && item.temperatura_min === null)) return;
      
      const locationName = getLocationLabel(item);
      const locationKey = item.municipio !== null && item.pais === 'Brasil' && !item.municipio.startsWith('Grid') 
          ? `${locationName} - ${formatLocationName(item.pais)}` 
          : locationName;
      
      const currentTemp = type === 'max' ? Number(item.temperatura_max) : Number(item.temperatura_min);
      
      if (!unique.has(locationKey)) {
        unique.set(locationKey, item);
      } else {
        const existing = unique.get(locationKey);
        const existingTemp = type === 'max' ? Number(existing.temperatura_max) : Number(existing.temperatura_min);
        if (type === 'max' && currentTemp > existingTemp) {
          unique.set(locationKey, item);
        } else if (type === 'min' && currentTemp < existingTemp) {
          unique.set(locationKey, item);
        }
      }
    });
    const result = Array.from(unique.values());
    return result.sort((a, b) => {
      if (type === 'max') return Number(b.temperatura_max) - Number(a.temperatura_max);
      return Number(a.temperatura_min) - Number(b.temperatura_min);
    }).slice(0, 10);
  };

  const topQuentes = getUniqueTop(anomalias, 'max');
  const topFrios = getUniqueTop(anomalias.filter(a => a.pais !== 'Antártica'), 'min');

  // Encontra recordes do dia
  const hottestPlace = topQuentes[0];
  const coldestPlace = topFrios[0];

  // Encontra localidade com maior variação climática (amplitude térmica)
  const maiorVariacao = [...anomalias]
    .filter(a => a.temperatura_max !== null && a.temperatura_min !== null)
    .sort((a, b) => {
      const diffA = Number(a.temperatura_max) - Number(a.temperatura_min);
      const diffB = Number(b.temperatura_max) - Number(b.temperatura_min);
      return diffB - diffA;
    })[0];

  // ⬇️ useMemo no TOPO DO COMPONENTE (não dentro de JSX condicional!)
  // Isso garante que o hook é chamado em TODAS as renders, respeitando as Rules of Hooks.
  const mapMarkers = useMemo(() => anomalias.map(foco => {
    if (!foco.latitude || !foco.longitude) return null;
    const temp = Number(foco.temperatura_media);
    const color = getTempColor(temp);
    const radius = Math.max(6, Math.min(18, Math.abs(temp - 20) / 2));
    
    return (
      <CircleMarker
        key={`clima-${foco.id_clima}`}
        center={[parseFloat(foco.latitude), parseFloat(foco.longitude)]}
        radius={radius}
        pathOptions={{ 
          color: '#ffffff',
          opacity: 0.6,
          fillColor: color, 
          fillOpacity: 0.85, 
          weight: 1.5
        }}
      >
        <Popup className="custom-popup">
          <div style={{ textAlign: 'center', minWidth: '130px' }}>
            <strong style={{ fontSize: '14px', display: 'block', paddingBottom: '4px', marginBottom: '4px', borderBottom: '1px solid #e2e8f0' }}>{getLocationLabel(foco)}</strong>
            <div style={{ fontSize: '13px', lineHeight: '1.4' }}>
              <div><strong>Atual:</strong> {String(foco.temperatura_media)}°C</div>
              <div><strong>Mín/Máx:</strong> {String(foco.temperatura_min)}°C / {String(foco.temperatura_max)}°C</div>
              <div><strong>Umidade:</strong> {String(foco.umidade_media)}%</div>
            </div>
          </div>
        </Popup>
      </CircleMarker>
    );
  }), [anomalias]);

  const focosMarkers = useMemo(() => focosCalor.map(foco => {
    if (!foco.latitude || !foco.longitude) return null;
    return (
      <CircleMarker
        key={`foco-${foco.id_anomalia}`}
        center={[parseFloat(foco.latitude), parseFloat(foco.longitude)]}
        radius={5}
        pathOptions={{ 
          color: '#ffffff',
          opacity: 0.6,
          fillColor: '#ef4444', 
          fillOpacity: 0.9, 
          weight: 1
        }}
      >
        <Popup className="custom-popup">
          <div style={{ textAlign: 'center', minWidth: '130px' }}>
            <strong style={{ fontSize: '14px', display: 'block', paddingBottom: '4px', marginBottom: '4px', borderBottom: '1px solid #fca5a5', color: '#ef4444' }}>
              🔥 {getLocationLabel(foco)}
            </strong>
            <div style={{ fontSize: '13px', lineHeight: '1.4' }}>
              <div><strong>Foco de Calor</strong></div>
              <div><strong>Satélite:</strong> {String(foco.nome_satelite)}</div>
              {foco.frp_megawatts && <div><strong>FRP:</strong> {foco.frp_megawatts} MW</div>}
            </div>
          </div>
        </Popup>
      </CircleMarker>
    );
  }), [focosCalor]);

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Monitoramento Global</h1>
          <p className="dashboard-subtitle">
            Análise meteorológica e de qualidade do ar em tempo real — Fontes: Open-Meteo, OpenWeatherMap
          </p>
        </div>
        <div className="dashboard-badge">
          <span className="badge-dot" />
          Dados Globais Ativos
        </div>
      </div>

      {/* Erro */}
      {error && (
        <div className="error-banner">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {/* Stat Cards - Apenas 4 Blocos Essenciais */}
      <div className="stat-grid">
        <StatCard
          label="Regiões Monitoradas"
          value={(resumoClima?.total_registros ?? 0) + focosCalor.length}
          sub="🌍 Locais com dados climáticos e alertas"
          icon={MapPin}
          accent="var(--accent)"
          iconBg="rgba(59,130,246,0.12)"
          loading={loading}
        />
        <StatCard
          label="Pico de Calor"
          value={hottestPlace ? `${hottestPlace.temperatura_max}°C` : '—'}
          sub={hottestPlace ? `🔥 ${getLocationLabel(hottestPlace)}` : '—'}
          icon={ThermometerSun}
          accent="#ef4444"
          iconBg="rgba(239,68,68,0.12)"
          loading={loading}
        />
        <StatCard
          label="Pico de Frio"
          value={coldestPlace ? `${coldestPlace.temperatura_min}°C` : '—'}
          sub={coldestPlace ? `❄️ ${getLocationLabel(coldestPlace)}` : '—'}
          icon={Snowflake}
          accent="#3b82f6"
          iconBg="rgba(59,130,246,0.12)"
          loading={loading}
        />
        <StatCard
          label="Maior Variação (Dia)"
          value={maiorVariacao ? `${maiorVariacao.temperatura_min}°C / ${maiorVariacao.temperatura_max}°C` : '—'}
          sub={maiorVariacao ? `🔄 ${getLocationLabel(maiorVariacao)} (Variação: ${(Number(maiorVariacao.temperatura_max) - Number(maiorVariacao.temperatura_min)).toFixed(1)}°C)` : '—'}
          icon={Thermometer}
          accent="#8b5cf6"
          iconBg="rgba(139,92,246,0.12)"
          loading={loading}
        />
      </div>

      {/* Mapa Interativo — Visão Global */}
      <div className="panel" style={{ height: '450px', padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            Carregando mapa...
          </div>
        ) : (
          <MapErrorBoundary fallbackHeight="450px">
            <MapContainer 
              preferCanvas={true}
              center={[20, 0]} 
              zoom={2.5} 
              minZoom={2}
              style={{ height: '100%', width: '100%', zIndex: 0, background: '#1e293b' }}
            >
              <MapController center={mapFocus} zoom={6} />
              <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                attribution='&copy; Esri'
                className="map-tiles-dark-overlay"
              />

              {activeFoco && activeFoco.latitude && activeFoco.longitude && (
                <Popup 
                  position={[parseFloat(activeFoco.latitude), parseFloat(activeFoco.longitude)]}
                  className="custom-popup"
                >
                  <div style={{ textAlign: 'center', minWidth: '130px' }}>
                    <strong style={{ fontSize: '14px', display: 'block', paddingBottom: '4px', marginBottom: '4px', borderBottom: '1px solid #e2e8f0' }}>{getLocationLabel(activeFoco)}</strong>
                    <div style={{ fontSize: '13px', lineHeight: '1.4' }}>
                      <div><strong>Atual:</strong> {String(activeFoco.temperatura_media)}°C</div>
                      <div><strong>Mín/Máx:</strong> {String(activeFoco.temperatura_min)}°C / {String(activeFoco.temperatura_max)}°C</div>
                      <div><strong>Umidade:</strong> {String(activeFoco.umidade_media)}%</div>
                    </div>
                  </div>
                </Popup>
              )}

              {mapMarkers}
              {focosMarkers}
            </MapContainer>
          </MapErrorBoundary>
        )}
      </div>

      {/* Rankings de Temperaturas Extremas */}
      <div className="charts-grid">
        <div className="panel">
          <div className="panel-title" style={{ color: '#ef4444' }}>
            <ThermometerSun size={14} />
            Top 10: Mais Quentes
          </div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Carregando...</p>
          ) : topQuentes.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Nenhum dado disponível.</p>
          ) : (
            <div className="rank-list">
              {topQuentes.map((item, i) => (
                <div 
                  className="rank-item" 
                  key={item.id_clima}
                  onClick={() => {
                    if (item.latitude && item.longitude) {
                      setMapFocus([parseFloat(item.latitude), parseFloat(item.longitude)]);
                      setActiveFoco(item);
                    }
                  }}
                  style={{ cursor: 'pointer' }}
                  title="Clique para ver no mapa"
                >
                  <span className="rank-pos">#{i + 1}</span>
                  <span className="rank-label">
                    {getLocationLabel(item)}
                  </span>
                  <span className="rank-value" style={{ color: '#ef4444', fontWeight: 'bold' }}>
                    {String(item.temperatura_max)}°C
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-title" style={{ color: '#3b82f6' }}>
            <Snowflake size={14} />
            Top 10: Mais Frios
          </div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Carregando...</p>
          ) : topFrios.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Nenhum dado disponível.</p>
          ) : (
            <div className="rank-list">
              {topFrios.map((item, i) => (
                <div 
                  className="rank-item" 
                  key={item.id_clima}
                  onClick={() => {
                    if (item.latitude && item.longitude) {
                      setMapFocus([parseFloat(item.latitude), parseFloat(item.longitude)]);
                      setActiveFoco(item);
                    }
                  }}
                  style={{ cursor: 'pointer' }}
                  title="Clique para ver no mapa"
                >
                  <span className="rank-pos">#{i + 1}</span>
                  <span className="rank-label">
                    {getLocationLabel(item)}
                  </span>
                  <span className="rank-value" style={{ color: '#3b82f6', fontWeight: 'bold' }}>
                    {String(item.temperatura_min)}°C
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
