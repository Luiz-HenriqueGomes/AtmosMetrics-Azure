import { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import FocosPage from './pages/FocosPage';
import QualidadeArPage from './pages/QualidadeArPage';
import LocalidadesPage from './pages/LocalidadesPage';
import SatelitesPage from './pages/SatelitesPage';
import ConfiguracoesPage from './pages/ConfiguracoesPage';
import CustomCursor from './components/CustomCursor';
import { api } from './services/api';
import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'loading'>('loading');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Atualiza o atributo no DOM para o CSS global (Dark/Light Mode)
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Verifica o status da API ao iniciar
  useEffect(() => {
    api.getHealth()
      .then(data => setApiStatus(data.banco === 'conectado' ? 'online' : 'offline'))
      .catch(() => setApiStatus('offline'));
  }, []);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':     return <DashboardPage />;
      case 'anomalias':     return <FocosPage />;
      case 'qualidade_ar':  return <QualidadeArPage />;
      case 'localidades':   return <LocalidadesPage />;
      case 'satelites':     return <SatelitesPage />;
      case 'configuracoes': return <ConfiguracoesPage />;
      default:
        return (
          <div style={{ color: 'var(--text-secondary)', padding: '2rem', textAlign: 'center' }}>
            <p>🚧 Página "<strong>{activePage}</strong>" em construção.</p>
          </div>
        );
    }
  };

  return (
    <div className="app-layout">
      <CustomCursor />
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        apiStatus={apiStatus}
        theme={theme}
        toggleTheme={toggleTheme}
      />
      <main className="app-main">
        <AnimatePresence mode="wait">
          <motion.div
            key={activePage}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            style={{ width: '100%', height: '100%' }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
