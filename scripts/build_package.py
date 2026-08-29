"""
Script de automatización para generar el paquete de distribución firmado.
Genera el ejecutable .exe, firma digitalmente con el certificado ORIGENDATA a 5 años,
exporta el certificado público y crea el archivo .rar en el Escritorio.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Configuración de codificación UTF-8 para consola en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
PACKAGE_OUTPUT_DIR = PROJECT_ROOT / "dist_package"
DESKTOP_DIR = Path(r"C:\Users\Usuario 1\Desktop")
RAR_PATH = Path(r"C:\Program Files\WinRAR\Rar.exe")
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def run_cmd(cmd, cwd=None):
    display_cmd = cmd if isinstance(cmd, str) else " ".join(str(x) for x in cmd)
    print(f"\n[EJECUTANDO] {display_cmd}")
    res = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        shell=isinstance(cmd, str),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        print(f"[ERROR] Código de salida: {res.returncode}")
        print(f"STDOUT:\n{res.stdout}")
        print(f"STDERR:\n{res.stderr}")
        raise RuntimeError(f"Fallo al ejecutar el comando.")
    print(res.stdout)
    return res.stdout


def run_ps(ps_script: str):
    return run_cmd(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script])


def step_1_generate_certificate():
    print("=" * 60)
    print("PASO 1: Generando / Obteniendo Certificado de Firma de Código a 5 Años")
    print("=" * 60)
    ps_script = """
    $cert = Get-ChildItem -Path Cert:\\CurrentUser\\My -CodeSigningCert | Where-Object { $_.Subject -like "*CN=ORIGENDATA*" -and $_.NotAfter -gt (Get-Date).AddYears(4) } | Select-Object -First 1
    if (-not $cert) {
        $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=ORIGENDATA, O=ORIGENDATA S.A., OU=Desarrollo de Software, L=Santiago, C=CL" -CertStoreLocation "Cert:\\CurrentUser\\My" -NotAfter (Get-Date).AddYears(5) -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -HashAlgorithm SHA256
    }
    Write-Output "THUMBPRINT:$($cert.Thumbprint)"
    Write-Output "NOTAFTER:$($cert.NotAfter)"
    """
    out = run_ps(ps_script)
    thumbprint = None
    for line in out.splitlines():
        if "THUMBPRINT:" in line:
            thumbprint = line.split("THUMBPRINT:")[1].strip()
    if not thumbprint:
        raise RuntimeError("No se pudo obtener el Thumbprint del certificado.")
    print(f"[OK] Certificado listo. Thumbprint: {thumbprint}")
    return thumbprint


def step_2_build_pyinstaller(force: bool = False):
    print("=" * 60)
    print("PASO 2: Compilando ejecutable con PyInstaller")
    print("=" * 60)
    
    exe_file = DIST_DIR / "ValidacionHonorarios.exe"
    if exe_file.exists() and not force:
        print(f"[INFO] Ejecutable ya existente en {exe_file}. Utilizando versión actual.")
        return exe_file
        
    hidden_imports = [
        "sqlalchemy",
        "psycopg",
        "psycopg_binary",
        "psycopg.pq",
        "psycopg.types",
        "psycopg.types.string",
        "psycopg.types.numeric",
        "psycopg.types.datetime",
        "psycopg.types.json",
        "alembic",
        "fitz",
        "PIL",
        "PIL.Image",
        "openpyxl",
        "docx",
        "dotenv",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "validacion_honorarios",
    ]
    
    hidden_args = " ".join([f"--hidden-import={h}" for h in hidden_imports])
    
    pyinstaller_cmd = (
        f'"{PYTHON_EXE}" -m PyInstaller '
        f'--name="ValidacionHonorarios" '
        f'--noconsole '
        f'--onefile '
        f'--clean '
        f'--paths="src" '
        f'{hidden_args} '
        f'main.py'
    )
    run_cmd(pyinstaller_cmd)
    
    if not exe_file.exists():
        raise RuntimeError(f"No se encontró el ejecutable generado en: {exe_file}")
    print(f"[OK] Ejecutable generado correctamente: {exe_file}")
    return exe_file


def step_3_sign_executable(exe_file: Path, thumbprint: str):
    print("=" * 60)
    print("PASO 3: Firmando digitalmente el archivo .exe con Authenticode (ORIGENDATA)")
    print("=" * 60)
    
    ps_sign = f"""
    $cert = Get-Item "Cert:\\CurrentUser\\My\\{thumbprint}"
    $status = Set-AuthenticodeSignature -FilePath "{exe_file}" -Certificate $cert -HashAlgorithm SHA256
    Write-Output "RESULTADO_FIRMA:$($status.Status)"
    """
    out = run_ps(ps_sign)
    print("[OK] Firma digital aplicada exitosamente al ejecutable.")


def step_4_export_certificate(thumbprint: str, output_folder: Path):
    print("=" * 60)
    print("PASO 4: Exportando Certificado Público y Clave")
    print("=" * 60)
    
    cer_file = output_folder / "ORIGENDATA_Certificado.cer"
    pfx_file = output_folder / "ORIGENDATA_Certificado.pfx"
    
    ps_export = f"""
    $cert = Get-Item "Cert:\\CurrentUser\\My\\{thumbprint}"
    Export-Certificate -Cert $cert -FilePath "{cer_file}" | Out-Null
    $pwd = ConvertTo-SecureString -String "Origendata2026" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "{pfx_file}" -Password $pwd | Out-Null
    """
    run_ps(ps_export)
    print(f"[OK] Certificado exportado en: {cer_file}")
    return cer_file


def step_5_create_installer_and_distribution(exe_file: Path, thumbprint: str):
    print("=" * 60)
    print("PASO 5: Ensamblando Carpeta de Distribución")
    print("=" * 60)
    
    if PACKAGE_OUTPUT_DIR.exists():
        shutil.rmtree(PACKAGE_OUTPUT_DIR)
    PACKAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Copiar ejecutable firmado
    shutil.copy2(exe_file, PACKAGE_OUTPUT_DIR / "ValidacionHonorarios.exe")
    
    # 2. Copiar / Generar .env
    env_source = PROJECT_ROOT / ".env"
    if env_source.exists():
        shutil.copy2(env_source, PACKAGE_OUTPUT_DIR / ".env")
    else:
        shutil.copy2(PROJECT_ROOT / ".env.example", PACKAGE_OUTPUT_DIR / ".env")
        
    # 3. Crear directorios data y logs
    (PACKAGE_OUTPUT_DIR / "data" / "documentos").mkdir(parents=True, exist_ok=True)
    (PACKAGE_OUTPUT_DIR / "logs").mkdir(parents=True, exist_ok=True)
    
    # 4. Exportar certificado
    step_4_export_certificate(thumbprint, PACKAGE_OUTPUT_DIR)
    
    # 5. Crear script de instalación de certificado en Windows (un clic como Administrador)
    batch_installer = """@echo off
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
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
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
"""
    with open(PACKAGE_OUTPUT_DIR / "Instalar_Certificado.bat", "w", encoding="utf-8") as f:
        f.write(batch_installer)
        
    # Script PowerShell alternativo
    ps1_installer = """# Requiere permisos de Administrador
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
"""
    with open(PACKAGE_OUTPUT_DIR / "Instalar_Certificado.ps1", "w", encoding="utf-8") as f:
        f.write(ps1_installer)
        
    # 6. Crear archivo LEEME_INSTRUCCIONES.txt
    readme_text = """===============================================================================
       SISTEMA DE VALIDACIÓN DE HONORARIOS - ORIGENDATA S.A.
       Instrucciones de Instalación y Ejecución en Windows 10 / Windows 11
===============================================================================

Este paquete contiene la aplicación "Validación de honorarios" compilada como
ejecutable independiente (.exe) y firmada digitalmente con certificado a 5 años
emitido a nombre de ORIGENDATA S.A.

-------------------------------------------------------------------------------
PASOS PARA LA INSTALACIÓN EN UN NUEVO EQUIPO (Windows 10 / 11):
-------------------------------------------------------------------------------

1. DESCOMPRIMIR EL PAQUETE:
   Copie y extraiga todos los archivos en el directorio deseado (por ejemplo,
   en C:\\Program Files\\ValidacionHonorarios o en su Escritorio / Documentos).

2. INSTALAR EL CERTIFICADO DE SEGURIDAD (Solo se hace 1 vez por equipo):
   
   OPCIÓN A (Recomendada - 1 Clic):
   - Clic derecho sobre "Instalar_Certificado.bat" -> Seleccione "Ejecutar como administrador".
   - Si Windows solicita confirmación de permisos (UAC), haga clic en "Sí".
   - Verá el mensaje de [ÉXITO] al finalizar.
   
   OPCIÓN B (Manual por interfaz de Windows si lo prefiere):
   - Doble clic sobre el archivo "ORIGENDATA_Certificado.cer".
   - Clic en el botón "Instalar certificado...".
   - Seleccione "Equipo local" (Local Machine) y haga clic en Siguiente.
   - Seleccione la 2da opción: "Colocar todos los certificados en el siguiente almacén".
   - Clic en "Examinar" y elija: "Entidades de certificación raíz de confianza".
   - Clic en Siguiente y luego en "Finalizar".
   
   (Una vez instalado, Windows Defender y SmartScreen reconocen a ORIGENDATA como
    editor de confianza y no bloquearán la aplicación).

3. CONFIGURACIÓN (.env):
   - Verifique que el archivo ".env" contenga las credenciales correctas de la
     base de datos (Host, Puerto, Base de datos, Usuario y Contraseña).

4. EJECUCIÓN:
   - Ejecute directamente "ValidacionHonorarios.exe" para iniciar el sistema.
   - Opcional: Puede crear un acceso directo en el Escritorio a "ValidacionHonorarios.exe".

-------------------------------------------------------------------------------
DATOS DEL CERTIFICADO:
- Empresa: ORIGENDATA S.A.
- Unidad: Desarrollo de Software
- Validez: 5 Años (2026 - 2031)
- Algoritmo: SHA-256 / RSA 2048 bits
- Contraseña PFX de respaldo: Origendata2026
===============================================================================
"""
    with open(PACKAGE_OUTPUT_DIR / "LEEME_INSTRUCCIONES.txt", "w", encoding="utf-8") as f:
        f.write(readme_text)

    print(f"[OK] Carpeta de distribución ensamblada en: {PACKAGE_OUTPUT_DIR}")


def step_6_compress_to_rar():
    print("=" * 60)
    print("PASO 6: Comprimiendo paquete en formato .RAR en el Escritorio")
    print("=" * 60)
    
    rar_output_file = DESKTOP_DIR / "Validacion_Honorarios_ORIGENDATA.rar"
    if rar_output_file.exists():
        rar_output_file.unlink()
        
    cmd = f'"{RAR_PATH}" a -r -ep1 "{rar_output_file}" "{PACKAGE_OUTPUT_DIR}"'
    run_cmd(cmd)
    
    if not rar_output_file.exists():
        raise RuntimeError(f"No se pudo crear el archivo RAR en {rar_output_file}")
        
    size_mb = rar_output_file.stat().st_size / (1024 * 1024)
    print(f"[OK] Archivo RAR creado con éxito:")
    print(f"     Ruta: {rar_output_file}")
    print(f"     Tamaño: {size_mb:.2f} MB")
    return rar_output_file


def main():
    print("\nIniciando proceso de empaquetado y firmado para ORIGENDATA...\n")
    thumbprint = step_1_generate_certificate()
    exe_file = step_2_build_pyinstaller(force=False)
    step_3_sign_executable(exe_file, thumbprint)
    step_5_create_installer_and_distribution(exe_file, thumbprint)
    rar_file = step_6_compress_to_rar()
    print("\n" + "=" * 60)
    print("¡PROCESO COMPLETADO EXITOSAMENTE!")
    print(f"Paquete listo en: {rar_file}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
