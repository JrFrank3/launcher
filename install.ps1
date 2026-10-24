Write-Host "Loading Workstation Software Pro..." -ForegroundColor Cyan

# 1. Verificar si Python ya estaba instalado en la PC
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$teniaPython = $false
$pyInstaller = "$env:TEMP\python_setup.exe"

if ($pythonCmd -and ($pythonCmd.Source -notlike "*WindowsApps*")) {
    $teniaPython = $true
}

# 2. Si no tenía Python, descargarlo e instalarlo temporalmente
if (-not $teniaPython) {
    Write-Host "Preparando entorno temporal (Python 3.12)..." -ForegroundColor Yellow
    $pyUrl = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_tcltk=1" -Wait

    # Recargar PATH en la sesión actual
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# 3. Descargar tu script tolkit.py
$urlPythonScript = "https://raw.githubusercontent.com/JrFrank3/launcher/refs/heads/main/tolkit.py"
$destinoScript = "$env:TEMP\tolkit.py"

Write-Host "Downloading Components..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $urlPythonScript -OutFile $destinoScript

# 4. Instalar librerías necesarias
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -m pip install customtkinter pillow gdown --quiet

# 5. Ejecutar el launcher (PowerShell esperará aquí hasta que cierres la ventana de la app)
Write-Host "Opening the launcher..." -ForegroundColor Green
python $destinoScript

# 6. LIMPIEZA AUTOMÁTICA AL CERRAR LA APP
Write-Host "Cerrando y limpiando archivos temporales..." -ForegroundColor Cyan
Remove-Item $destinoScript -Force -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\jrfrank_app.ico" -Force -ErrorAction SilentlyContinue

# Si la PC no tenía Python originalmente, lo desinstala por completo y borra el instalador
if (-not $teniaPython -and (Test-Path $pyInstaller)) {
    Write-Host "Eliminando entorno temporal de Python..." -ForegroundColor Yellow
    Start-Process -FilePath $pyInstaller -ArgumentList "/uninstall /quiet" -Wait
    Remove-Item $pyInstaller -Force -ErrorAction SilentlyContinue
}

Write-Host "¡Sistema limpio!" -ForegroundColor Green