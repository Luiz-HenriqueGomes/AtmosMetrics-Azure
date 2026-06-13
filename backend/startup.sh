#!/bin/bash
# ============================================================
# AtmosMetrics — startup.sh
# Script de inicialização para Azure App Service
# ============================================================
# O Azure App Service (Linux) executa este script para iniciar
# a aplicação. Garante que o PYTHONPATH e o módulo estejam
# corretamente configurados independente do startup command
# configurado no portal.
# ============================================================

set -e

APP_ROOT="/home/site/wwwroot"

# Ativa o virtualenv se existir (criado pelo Oryx durante o build)
if [ -f "$APP_ROOT/antenv/bin/activate" ]; then
    source "$APP_ROOT/antenv/bin/activate"
fi

# Garante que a raiz do projeto está no PYTHONPATH
# (necessário para que 'from app.xxx import ...' funcione)
export PYTHONPATH="$APP_ROOT:${PYTHONPATH}"

# Vai para a raiz onde ficam os pacotes app/ e etl/
cd "$APP_ROOT"

echo "🚀 Iniciando AtmosMetrics API..."
echo "   PYTHONPATH: $PYTHONPATH"
echo "   Working dir: $(pwd)"
echo "   Python: $(python --version)"

# Inicia o servidor
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
