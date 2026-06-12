# AtmosMetrics

![AtmosMetrics Banner](https://via.placeholder.com/1200x300.png?text=AtmosMetrics+-+Monitoramento+Socioambiental+Global)

> Sistema corporativo de monitoramento socioambiental, climático e de qualidade do ar em tempo real, baseado em dados oficiais de agências espaciais e ambientais.

---

## 🌍 Visão Geral

O **AtmosMetrics** é uma plataforma analítica projetada para fornecer uma visão de alto nível sobre indicadores cruciais do nosso planeta. Integrando dados em tempo real, o sistema processa informações sobre focos de incêndio, índices de qualidade do ar (AQI), anomalias térmicas e clima, apresentando-os em um painel interativo e imersivo.

Nossa missão com o AtmosMetrics é democratizar o acesso a dados ambientais densos e técnicos, transformando-os em visualizações atraentes que facilitam a tomada de decisão para ambientalistas, governos e empresas.

---

## 🏛️ Arquitetura do Sistema

O projeto adota uma arquitetura conteinerizada moderna (Docker), segmentada em três grandes pilares:

### 1. Banco de Dados e Data Warehouse
Utilizamos **PostgreSQL 16** com a extensão espacial **PostGIS 3.4** para armazenamento e cruzamento geográfico dos dados. 
O modelo de dados é construído sob a premissa de um *Star Schema* (Data Warehouse) otimizado para agregações analíticas rápidas:
- **Tabelas Fato:** Focos de Calor, Clima e Qualidade do Ar (AQI).
- **Tabelas Dimensão:** Tempo, Satélites e Localidades.

### 2. Back-end e Pipeline ETL
O back-end foi desenvolvido em **Python 3.12** utilizando **FastAPI**.
Ele opera como o orquestrador do sistema, expondo rotas RESTful síncronas e assíncronas que alimentam o Dashboard.
Além da API, o Back-end abriga nossos **Pipelines de ETL (Extract, Transform, Load)** que capturam dados brutos das seguintes fontes:
- **INPE (Instituto Nacional de Pesquisas Espaciais):** Focos de calor ativos em solo Brasileiro via Satélites.
- **OpenWeatherMap:** Informações globais de qualidade do ar (PM2.5, PM10, Monóxido de Carbono).
- **Open-Meteo:** Dados climáticos globais (Vento, Temperatura).

### 3. Front-end e Dashboard Interativo
A interface do usuário é construída com **React 19** e **Vite**, adotando o poder da tipagem estática do **TypeScript**.
Focada puramente em *User Experience (UX)* e *User Interface (UI)* de alta qualidade, a interface apresenta:
- **Painéis (Bento Box Grids):** Visualizações limpas inspiradas no design moderno de aplicativos.
- **Mapas Interativos GIS (Leaflet):** Mapas topográficos e de satélite interativos que sobrepõem polígonos, heatmaps e partículas de vento georreferenciadas globalmente (arquitetura semelhante a projetos como IQAir e Earth Nullschool).
- **Gráficos Dinâmicos (Recharts):** Métricas acompanhadas visualmente.

---

## 🚀 Tecnologias e Stack

**Infraestrutura:**
- Docker & Docker Compose

**Back-end:**
- Python 3.12
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (Validação de Schemas)
- httpx (Requisições assíncronas de ETL)

**Front-end:**
- React 19
- TypeScript
- Vite
- React Leaflet (Mapas interativos)
- Leaflet Velocity (Física de partículas de vento)
- Recharts (Gráficos)
- Lucide React (Ícones)
- CSS Vanilla (Sistema de design sólido e flexível)

**Banco de Dados:**
- PostgreSQL 16
- PostGIS 3.4

---

## 🛡️ Princípios de Design

1. **Aesthetics & UX:** Acreditamos que relatórios ambientais não precisam ser monótonos. Utilizamos paletas *Dark Mode*, *Glassmorphism* sutil e animações de estado fluidas.
2. **Performático:** Utilização do FastAPI assíncrono e Vite (Rollup) no React para garantir que os dados carreguem quase que instantaneamente.
3. **Escalável e Modulável:** Toda a ingestão de dados (ETL) e a arquitetura das APIs são segmentadas para que novos painéis (ex: Monitoramento de Desmatamento, Chuvas) possam ser acoplados rapidamente no futuro.

---

*Desenvolvido como projeto em Dev Web II, com foco na consolidação de arquiteturas web escaláveis e interativas.*
