import { useEffect, useState, useMemo } from 'react';
import { MapPin, Search, Globe } from 'lucide-react';
import { api, type Localidade, type PaisOut, type ContinenteOut } from '../services/api';
import './LocalidadesPage.css';

// Continentes disponíveis para abas
const CONTINENTES = [
  'Todos',
  'América do Sul',
  'América do Norte',
  'Europa',
  'África',
  'Ásia',
  'Oceania',
  'Ártico',
  'Antártica',
];

// Cores por continente
const continentColors: Record<string, string> = {
  'América do Sul':   '#10b981',
  'América do Norte': '#3b82f6',
  'Europa':           '#a78bfa',
  'África':           '#f97316',
  'Ásia':             '#06b6d4',
  'Oceania':          '#ec4899',
  'Ártico':           '#60a5fa',
  'Antártica':        '#94a3b8',
};

// Emojis de bandeira simples (baseado em código ISO de 2 letras)
function flagEmoji(iso: string | null): string {
  if (!iso || iso.length !== 2) return '🌍';
  const codePoints = [...iso.toUpperCase()].map(c => 127397 + c.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

export default function LocalidadesPage() {
  const [paises, setPaises] = useState<PaisOut[]>([]);
  // continentes backend state was removed as it's not being used
  const [localidades, setLocalidades] = useState<Localidade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [continenteFiltro, setContinenteFiltro] = useState('Todos');
  const [busca, setBusca] = useState('');
  const [paisExpandido, setPaisExpandido] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getPaises().catch(() => [] as PaisOut[]),
      api.getContinentes().catch(() => [] as ContinenteOut[]),
      api.getLocalidades().catch(() => [] as Localidade[]),
    ])
      .then(([p, , l]) => {
        setPaises(p);
        // continentes response is ignored as it's not being used
        setLocalidades(l);
      })
      .catch(() => setError('Não foi possível carregar as localidades.'))
      .finally(() => setLoading(false));
  }, []);

  // Conta localidades por país
  const contagemPorPais = useMemo(() => {
    return localidades.reduce<Record<string, number>>((acc, l) => {
      const p = l.pais || 'Brasil';
      acc[p] = (acc[p] || 0) + 1;
      return acc;
    }, {});
  }, [localidades]);

  // Localidades por país (para expansão do card Brasil)
  const localidadesPorPais = useMemo(() => {
    return localidades.reduce<Record<string, Localidade[]>>((acc, l) => {
      const p = l.pais || 'Brasil';
      if (!acc[p]) acc[p] = [];
      acc[p].push(l);
      return acc;
    }, {});
  }, [localidades]);

  // Continentes reais do backend para montar as tabs
  const continentesReais = useMemo(() => {
    const set = new Set<string>();
    paises.forEach(p => set.add(p.continente));
    // Também conta o Brasil se não houver países globais
    localidades.forEach(l => {
      if (l.continente) set.add(l.continente);
    });
    return set;
  }, [paises, localidades]);

  // Tabs filtradas: mostra apenas continentes que existem nos dados
  const tabsVisiveis = CONTINENTES.filter(c => c === 'Todos' || continentesReais.has(c));

  // Filtra países pelo continente e busca
  const paisesFiltrados = useMemo(() => {
    // Agrupa por país: se temos dados da tabela paises, usa eles; senão, gera do localidades
    const paisMap = new Map<string, { pais: string; continente: string; codigo_iso: string | null }>();

    paises.forEach(p => {
      paisMap.set(p.pais, p);
    });

    // Adiciona Brasil se não estiver na lista de países globais
    if (!paisMap.has('Brasil')) {
      paisMap.set('Brasil', { pais: 'Brasil', continente: 'América do Sul', codigo_iso: 'BR' });
    }

    let resultado = Array.from(paisMap.values());

    // Filtro por continente
    if (continenteFiltro !== 'Todos') {
      resultado = resultado.filter(p => p.continente === continenteFiltro);
    }

    // Filtro por busca
    if (busca) {
      const buscaLower = busca.toLowerCase();
      resultado = resultado.filter(p =>
        p.pais.toLowerCase().includes(buscaLower) ||
        p.continente.toLowerCase().includes(buscaLower)
      );
    }

    // Ordena alfabeticamente
    resultado.sort((a, b) => a.pais.localeCompare(b.pais, 'pt-BR'));

    return resultado;
  }, [paises, continenteFiltro, busca, localidades]);

  return (
    <div className="localidades-page">
      {/* Header */}
      <div className="loc-header">
        <div>
          <h1 className="loc-title">Localidades Globais</h1>
          <p className="loc-subtitle">
            <Globe size={13} style={{ verticalAlign: '-2px' }} />{' '}
            Países e localidades monitorados — {paises.length > 0 ? `${paises.length} países` : ''} · {localidades.length} localidades
          </p>
        </div>
      </div>

      {/* Barra de filtros */}
      <div className="loc-toolbar panel">
        <div className="loc-search-wrap">
          <Search size={14} className="loc-search-icon" />
          <input
            className="loc-search"
            type="text"
            placeholder="Buscar país ou cidade..."
            value={busca}
            onChange={e => setBusca(e.target.value)}
          />
        </div>
        <div className="loc-region-tabs">
          {tabsVisiveis.map(c => (
            <button
              key={c}
              className={`region-tab ${continenteFiltro === c ? 'active' : ''}`}
              onClick={() => setContinenteFiltro(c)}
              style={continenteFiltro === c && c !== 'Todos' ? { borderColor: continentColors[c], color: continentColors[c] } : {}}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Erro */}
      {error && (
        <div className="error-banner">
          <MapPin size={16} />
          {error}
        </div>
      )}

      {/* Grid de cards */}
      {loading ? (
        <div className="loc-grid">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="loc-card skeleton-card">
              <div className="skeleton-cell" style={{ width: '40px', height: '40px', borderRadius: '10px' }} />
              <div className="skeleton-cell" style={{ width: '70%', height: '16px' }} />
              <div className="skeleton-cell" style={{ width: '50%', height: '12px' }} />
            </div>
          ))}
        </div>
      ) : paisesFiltrados.length === 0 ? (
        <div className="panel" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          Nenhum país encontrado para o filtro selecionado.
        </div>
      ) : (
        <div className="loc-grid">
          {paisesFiltrados.map(p => {
            const cor = continentColors[p.continente] || '#94a3b8';
            const numLocalidades = contagemPorPais[p.pais] || 0;
            const isExpanded = paisExpandido === p.pais;
            const cidadesDoPais = localidadesPorPais[p.pais] || [];

            return (
              <div
                key={p.pais}
                className={`loc-card ${isExpanded ? 'expanded' : ''}`}
                style={{ '--card-accent': cor, '--card-glow': `radial-gradient(circle at top left, ${cor}11, transparent 60%)` } as React.CSSProperties}
                onClick={() => setPaisExpandido(isExpanded ? null : p.pais)}
              >
                <div className="loc-card-bar" style={{ background: cor }} />
                <div className="loc-card-top">
                  <div className="loc-uf-badge" style={{ background: `${cor}18`, color: cor, fontSize: '1.4rem' }}>
                    {flagEmoji(p.codigo_iso)}
                  </div>
                  <span className="loc-region-tag" style={{ color: cor }}>{p.continente}</span>
                </div>
                <h3 className="loc-card-name">{p.pais}</h3>
                <div className="loc-card-meta">
                  <span><MapPin size={11} /> {numLocalidades} localidades</span>
                  {p.codigo_iso && <span style={{ opacity: 0.5 }}>ISO: {p.codigo_iso}</span>}
                </div>

                {/* Expansão: mostra cidades quando clicado */}
                {isExpanded && cidadesDoPais.length > 0 && (
                  <div className="loc-card-cities">
                    {cidadesDoPais.slice(0, 20).map((l, i) => (
                      <span key={i} className="bioma-tag">
                        {l.municipio}{l.uf ? ` (${l.uf})` : ''}
                      </span>
                    ))}
                    {cidadesDoPais.length > 20 && (
                      <span className="bioma-tag" style={{ opacity: 0.5 }}>
                        +{cidadesDoPais.length - 20} mais
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
