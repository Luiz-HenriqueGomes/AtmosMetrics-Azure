import { useState, useEffect } from 'react';
import { Settings, Play, Loader2, CheckCircle2, XCircle, Server, Database, Globe, Calendar, AlertCircle, CloudRain, Wind, Zap } from 'lucide-react';
import { api, type HealthResponse, type ETLResponse } from '../services/api';
import './ConfiguracoesPage.css';

type ETLStatus = 'idle' | 'loading' | 'success' | 'error';

// Estado individual para cada pipeline ETL
interface ETLState {
  status: ETLStatus;
  result: ETLResponse | null;
  error: string | null;
  date: string;
}

function createInitialETLState(): ETLState {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return {
    status: 'idle',
    result: null,
    error: null,
    date: d.toISOString().slice(0, 10),
  };
}

export default function ConfiguracoesPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Estado para cada ETL
  const [etlINPE, setEtlINPE] = useState<ETLState>(createInitialETLState);
  const [etlClima, setEtlClima] = useState<ETLState>(createInitialETLState);
  const [etlAr, setEtlAr] = useState<ETLState>(createInitialETLState);
  const [etlGlobal, setEtlGlobal] = useState<ETLState>(createInitialETLState);

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch(() => setHealth(null))
      .finally(() => setHealthLoading(false));
  }, []);

  // Funções genéricas de execução
  const executeETL = async (
    apiCall: (date?: string) => Promise<ETLResponse>,
    state: ETLState,
    setState: React.Dispatch<React.SetStateAction<ETLState>>
  ) => {
    setState(prev => ({ ...prev, status: 'loading', result: null, error: null }));
    try {
      const result = await apiCall(state.date);
      setState(prev => ({ ...prev, status: 'success', result }));
    } catch (err: any) {
      setState(prev => ({ ...prev, status: 'error', error: err.message || 'Erro desconhecido ao executar o ETL.' }));
    }
  };

  const dbOk = health?.banco === 'conectado';

  // Componente para renderizar um card ETL
  const renderETLCard = (
    title: string,
    description: string,
    icon: React.ReactNode,
    state: ETLState,
    setState: React.Dispatch<React.SetStateAction<ETLState>>,
    onExecute: () => void,
    note?: string,
    accentColor?: string,
  ) => (
    <div className="config-section panel">
      <div className="config-section-title" style={accentColor ? { color: accentColor } : {}}>
        {icon}
        {title}
      </div>
      <p className="config-section-desc">{description}</p>

      {note && (
        <div className="etl-note">
          <AlertCircle size={12} />
          {note}
        </div>
      )}

      <div className="etl-controls">
        <div className="etl-date-wrap">
          <label className="filter-label">
            <Calendar size={11} /> Data para ingestão
          </label>
          <input
            className="filter-input"
            type="date"
            value={state.date}
            onChange={e => setState(prev => ({ ...prev, date: e.target.value }))}
            disabled={state.status === 'loading'}
          />
        </div>
        <button
          className={`etl-btn ${state.status === 'loading' ? 'loading' : ''}`}
          onClick={onExecute}
          disabled={state.status === 'loading' || !state.date}
          style={accentColor && state.status !== 'loading' ? { background: `linear-gradient(135deg, ${accentColor}, ${accentColor}cc)` } : {}}
        >
          {state.status === 'loading' ? (
            <>
              <Loader2 size={14} className="spin" />
              Processando...
            </>
          ) : (
            <>
              <Play size={14} />
              Executar ETL
            </>
          )}
        </button>
      </div>

      {/* Resultado */}
      {state.status === 'success' && state.result && (
        <div className="etl-result success">
          <CheckCircle2 size={16} />
          <div>
            <strong>{state.result.mensagem}</strong>
            <span className="etl-result-detail">
              {state.result.registros} registros processados · Data: {state.result.data}
            </span>
          </div>
        </div>
      )}

      {state.status === 'error' && (
        <div className="etl-result error">
          <XCircle size={16} />
          <div>
            <strong>Erro no ETL</strong>
            <span className="etl-result-detail">{state.error}</span>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="config-page">
      {/* Header */}
      <div className="config-header">
        <div>
          <h1 className="config-title">Configurações</h1>
          <p className="config-subtitle">
            <Settings size={13} style={{ verticalAlign: '-2px' }} />{' '}
            Painel de controle do sistema AtmosMetrics — Pipelines de dados globais
          </p>
        </div>
      </div>

      {/* ETL Cards Grid */}
      <div className="config-grid">
        {/* ETL INPE (original) */}
        {renderETLCard(
          'ETL INPE — Focos de Calor',
          'Dispara o pipeline de ingestão de dados do INPE para a data selecionada. O sistema baixa o arquivo de focos de calor, processa e carrega no banco de dados.',
          <Play size={14} />,
          etlINPE,
          setEtlINPE,
          () => executeETL(api.executarETL, etlINPE, setEtlINPE),
        )}

        {/* ETL Clima (Open-Meteo) */}
        {renderETLCard(
          'ETL Clima — Open-Meteo',
          'Ingere dados climáticos globais da API Open-Meteo: temperatura, umidade, precipitação e vento para todas as localidades cadastradas.',
          <CloudRain size={14} />,
          etlClima,
          setEtlClima,
          () => executeETL(api.executarETLClima, etlClima, setEtlClima),
          undefined,
          '#06b6d4',
        )}

        {/* ETL Qualidade do Ar (OpenWeather) */}
        {renderETLCard(
          'ETL Qualidade do Ar — OpenWeather',
          'Ingere dados de qualidade do ar da API OpenWeatherMap: AQI, PM2.5, PM10, CO e O3 para todas as localidades cadastradas.',
          <Wind size={14} />,
          etlAr,
          setEtlAr,
          () => executeETL(api.executarETLQualidadeAr, etlAr, setEtlAr),
          'Requer chave de API OpenWeatherMap configurada no backend.',
          '#f59e0b',
        )}

        {/* ETL Global (Todos) */}
        {renderETLCard(
          'ETL Global — Todos os Pipelines',
          'Executa TODOS os pipelines de ingestão simultaneamente: INPE, Open-Meteo e OpenWeatherMap. Ideal para a carga inicial do sistema.',
          <Zap size={14} />,
          etlGlobal,
          setEtlGlobal,
          () => executeETL(api.executarETLGlobal, etlGlobal, setEtlGlobal),
          'Pode levar vários minutos dependendo do volume de dados.',
          '#a78bfa',
        )}
      </div>

      {/* Card Status do Sistema */}
      <div className="config-section panel">
        <div className="config-section-title">
          <Server size={14} />
          Status do Sistema
        </div>

        {healthLoading ? (
          <div className="status-grid">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="status-item">
                <div className="skeleton-cell" style={{ width: '100%', height: '40px' }} />
              </div>
            ))}
          </div>
        ) : health ? (
          <div className="status-grid">
            <div className="status-item">
              <div className="status-icon" style={{ background: 'rgba(16,185,129,0.1)', color: 'var(--green)' }}>
                <Globe size={16} />
              </div>
              <div className="status-info">
                <span className="status-label">API</span>
                <span className="status-value">{health.status}</span>
              </div>
            </div>

            <div className="status-item">
              <div className="status-icon" style={{ background: dbOk ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', color: dbOk ? 'var(--green)' : '#ef4444' }}>
                <Database size={16} />
              </div>
              <div className="status-info">
                <span className="status-label">Banco de Dados</span>
                <span className="status-value" style={{ color: dbOk ? 'var(--green)' : '#ef4444' }}>
                  {health.banco}
                </span>
              </div>
            </div>

            <div className="status-item">
              <div className="status-icon" style={{ background: 'rgba(59,130,246,0.1)', color: 'var(--accent)' }}>
                <Server size={16} />
              </div>
              <div className="status-info">
                <span className="status-label">Aplicação</span>
                <span className="status-value">{health.api}</span>
              </div>
            </div>

            <div className="status-item">
              <div className="status-icon" style={{ background: 'rgba(167,139,250,0.1)', color: '#a78bfa' }}>
                <Settings size={16} />
              </div>
              <div className="status-info">
                <span className="status-label">Versão</span>
                <span className="status-value">v{health.versao}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="etl-result error">
            <AlertCircle size={16} />
            <div>
              <strong>API Indisponível</strong>
              <span className="etl-result-detail">
                Não foi possível conectar ao backend. Verifique se o Docker está rodando.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Informações do Projeto */}
      <div className="panel config-about">
        <div className="config-section-title">
          <AlertCircle size={14} />
          Sobre o Projeto
        </div>
        <div className="about-grid">
          <div className="about-item">
            <span className="about-label">Projeto</span>
            <span className="about-value">AtmosMetrics — Dev Web II</span>
          </div>
          <div className="about-item">
            <span className="about-label">Desenvolvedores</span>
            <span className="about-value">Luiz Henrique Gomes de Oliveira · Kaio Correia</span>
          </div>
          <div className="about-item">
            <span className="about-label">Stack</span>
            <span className="about-value">React 19 + FastAPI + PostgreSQL + PostGIS · Open-Meteo · OpenWeatherMap · NASA FIRMS</span>
          </div>
          <div className="about-item">
            <span className="about-label">Fontes de Dados</span>
            <span className="about-value">INPE Programa Queimadas · NASA FIRMS · Open-Meteo (Clima) · OpenWeatherMap (Qualidade do Ar)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
