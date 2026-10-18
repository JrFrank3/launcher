# 1. Mostrar mensaje de bienvenida
Write-Host "Iniciando Workstation Software Pro..." -ForegroundColor Cyan

# 2. Descargar el script de Python de tu repositorio directamente a la carpeta temporal
$urlPythonScript = "https://raw.githubusercontent.com/JrFrank3/launcher/refs/heads/main/tolkit.py"
$destinoScript = "$env:TEMP\tolkit.py"

Write-Host "Descargando componentes..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $urlPythonScript -OutFile $destinoScript

# 3. Asegurar que las librerías necesarias estén instaladas de forma silenciosa
Write-Host "Verificando dependencias (CustomTkinter, Pillow, Gdown)..." -ForegroundColor Yellow
pip install customtkinter pillow gdown --quiet --upgrade

# 4. Ejecutar el script de Python
Write-Host "Abriendo el launcher..." -ForegroundColor Green
<<<<<<< HEAD
python $destinoScript
=======
python $destinoScript
>>>>>>> 27b93e96e39d6115970a185dac7b0501dead0a75
