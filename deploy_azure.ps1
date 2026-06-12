# ============================================================
# Script de Deploy para Azure App Service
# Faz o build do Frontend e compacta o Backend em app.zip
# ============================================================

Write-Host "Iniciando processo de empacotamento para Azure..."

# 1. Build do Frontend
Write-Host "1/3 Fazendo build do Frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Verifica se a pasta static foi gerada no backend
if (-Not (Test-Path "backend\app\static\index.html")) {
    Write-Host "Erro: O build do frontend falhou ou os arquivos nao foram gerados em backend/app/static"
    exit 1
}

# 3. Compactar o Backend (que agora contem o Frontend embutido)
Write-Host "2/3 Compactando arquivos do backend em app.zip..."
if (Test-Path "app.zip") {
    Remove-Item "app.zip" -Force
}

# Muda para a pasta do backend para zipar a partir da raiz (requisito do App Service)
cd backend
# Zipa as pastas app/, etl/ e o arquivo requirements.txt (ignora ambientes virtuais se houver)
Compress-Archive -Path "app", "etl", "requirements.txt", "Dockerfile" -DestinationPath "..\app.zip" -Force
cd ..

Write-Host "3/3 Concluido! O arquivo app.zip foi gerado na raiz do projeto."
Write-Host "Agora voce pode enviar este arquivo pelo Deployment Center (Zip Deploy) no Azure Portal."
