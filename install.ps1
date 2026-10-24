# Desactivar la barra de cálculo de PowerShell (acelera las descargas hasta 10x)
$ProgressPreference = 'SilentlyContinue'

Write-Host "Loading Workstation Software Pro..." -ForegroundColor Cyan

# 1. Verificar si Python ya está instalado
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$tienePython = $false
$pyInstaller = "$env:TEMP\python_setup.exe"

if ($pythonCmd -and ($pythonCmd.Source -notlike "*WindowsApps*")) {
    $tienePython = $true
}

# 2. Si no tiene Python, descargarlo e instalarlo mostrando cada etapa
if (-not $tienePython) {
    Write-Host "[1/3] Descargando instalador de Python 3.12..." -ForegroundColor Yellow
    $pyUrl = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller

    Write-Host "[2/3] Instalando Python en segundo plano (espera 1 minuto)..." -ForegroundColor Yellow
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_tcltk=1" -Wait

    # Actualizar variables de entorno en la sesión actual
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# 3. Instalar dependencias con barra de progreso visible
Write-Host "[3/3] Verificando librerias (CustomTkinter, Pillow, Gdown)..." -ForegroundColor Yellow
python -m pip install customtkinter pillow gdown --quiet --disable-pip-version-check

# 4. Descargar la versión más reciente de tolkit.py (sin caché)
$timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$urlPythonScript = "https://raw.githubusercontent.com/JrFrank3/launcher/refs/heads/main/tolkit.py?t=$timestamp"
$destinoScript = "$env:TEMP\tolkit.py"

Write-Host "Downloading latest tolkit.py..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $urlPythonScript -OutFile $destinoScript -Headers @{"Cache-Control"="no-cache"}

# 5. Ejecutar el launcher
Write-Host "Opening the launcher..." -ForegroundColor Green
python $destinoScript

# 6. Limpiar archivos temporales al cerrar la app
Remove-Item $destinoScript -Force -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\jrfrank_app.ico" -Force -ErrorAction SilentlyContinue