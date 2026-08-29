# Requiere permisos de Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[INFO] Solicitando permisos de Administrador..." -ForegroundColor Yellow
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$certFile = Join-Path $PSScriptRoot "ORIGENDATA_Certificado.cer"
if (-not (Test-Path $certFile)) {
    Write-Host "[ERROR] No se encontro: $certFile" -ForegroundColor Red
    pause
    exit
}

Write-Host "Instalando certificado ORIGENDATA en Windows..." -ForegroundColor Cyan
& certutil.exe -f -addstore "ROOT" $certFile | Out-Null
& certutil.exe -f -addstore "TrustedPublisher" $certFile | Out-Null
& certutil.exe -f -user -addstore "ROOT" $certFile | Out-Null
& certutil.exe -f -user -addstore "TrustedPublisher" $certFile | Out-Null

Write-Host "`n[EXITO] Certificado ORIGENDATA instalado correctamente!" -ForegroundColor Green
Write-Host "Windows 10/11 ahora confia plenamente en ValidacionHonorarios.exe`n" -ForegroundColor Green
Read-Host "Presione Enter para salir..."
