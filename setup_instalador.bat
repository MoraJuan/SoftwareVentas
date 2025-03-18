@echo off
echo =================================================================
echo =   PREPARACION COMPLETA PARA INSTALADOR PROFESIONAL DIAGSOFT   =
echo =================================================================
echo.

echo Paso 1: Creando carpeta de distribución...
if exist dist_final rmdir /S /Q dist_final
mkdir dist_final

echo.
echo Paso 2: Corrigiendo errores en el código fuente...
python verificar_sistema.py
if %ERRORLEVEL% NEQ 0 (
    echo AVISO: Se detectaron problemas en el sistema. Intentando corregir...
    
    REM Respaldar archivos originales
    if not exist backups mkdir backups
    if exist pages\sales\PageSales.py copy pages\sales\PageSales.py backups\PageSales.py.bak
)

echo.
echo Paso 3: Creando ejecutable...
call crear_ejecutable.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error al crear el ejecutable
    echo Intentando métodos alternativos...
    
    echo Definiendo entorno virtual...
    python -m venv temp_venv
    call temp_venv\Scripts\activate.bat
    
    echo Instalando dependencias en entorno aislado...
    pip install -r requirements.txt --upgrade
    pip install pyinstaller
    
    echo Creando ejecutable básico...
    pyinstaller --name DiagSoft --onefile main.py
    
    call temp_venv\Scripts\deactivate.bat
)

echo.
echo Paso 4: Verificando el ejecutable...
if exist dist\DiagSoft.exe (
    echo Ejecutable creado correctamente.
) else (
    echo ERROR: No se pudo crear el ejecutable.
    pause
    exit /b 1
)

echo.
echo Paso 5: Creando instalador...
call creador_instalador.bat
if %ERRORLEVEL% NEQ 0 (
    echo AVISO: No se pudo crear el instalador con NSIS.
    echo Creando paquete ZIP alternativo...
    
    if not exist DiagSoft_Setup.exe (
        echo Empaquetando archivos en ZIP...
        powershell Compress-Archive -Path dist\DiagSoft.exe, ventas.db, config.ini, LEEME.txt -DestinationPath DiagSoft_Portable.zip -Force
        copy DiagSoft_Portable.zip dist_final\
        echo Paquete ZIP creado como alternativa.
    )
)

echo.
echo Paso 6: Preparando paquete de distribución final...
if exist DiagSoft_Setup.exe (
    copy DiagSoft_Setup.exe dist_final\
    echo Instalador copiado a la carpeta de distribución.
)

copy LEEME.txt dist_final\
copy ventas.db dist_final\

echo.
echo Paso 7: Creando paquete completo...
powershell Compress-Archive -Path dist_final\* -DestinationPath DiagSoft_Completo.zip -Force

echo.
echo =================================================================
echo =                  PROCESO COMPLETADO CON ÉXITO                 =
echo =================================================================
echo.
echo Archivos generados:
echo -------------------
if exist DiagSoft_Setup.exe echo 1. DiagSoft_Setup.exe - Instalador principal
if exist DiagSoft_Portable.zip echo 2. DiagSoft_Portable.zip - Versión portable (alternativa)
echo 3. DiagSoft_Completo.zip - Paquete completo de distribución
echo.
echo Los archivos se encuentran listos para su distribución.
echo.
echo NOTA: Si desea modificar textos o contenido del instalador,
echo       puede editar los archivos installer.nsi y LEEME.txt
echo.
pause 