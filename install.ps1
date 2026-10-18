# 1. Mostrar mensaje de bienvenida
Write-Host "Loading Workstation Software Pro..." -ForegroundColor Cyan

# 2. Descargar el script de Python de tu repositorio directamente a la carpeta temporal
$urlPythonScript = "https://raw.githubusercontent.com/JrFrank3/launcher/refs/heads/main/tolkit.py"
$destinoScript = "$env:TEMP\tolkit.py"

Write-Host "Downloading Components..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $urlPythonScript -OutFile $destinoScript

# 3. Asegurar que las librerías necesarias estén instaladas de forma silenciosa
Write-Host "Checking dependencies (CustomTkinter, Pillow, Gdown)..." -ForegroundColor Yellow
pip install customtkinter pillow gdown --quiet --upgrade

# 4. Ejecutar el script de Python
Write-Host "Opening the launcher..." -ForegroundColor Green
python $destinoScript