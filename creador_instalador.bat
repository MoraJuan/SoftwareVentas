@echo off
echo =========================================================
echo =    CREACION DE INSTALADOR PROFESIONAL PARA DIAGSOFT   =
echo =========================================================
echo.

REM Comprobar si NSIS está instalado
echo Verificando instalación de NSIS...
where makensis > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: NSIS no está instalado o no está en el PATH.
    echo Por favor, instale NSIS desde https://nsis.sourceforge.io/Download
    echo y asegúrese de agregarlo a la variable PATH del sistema.
    pause
    exit /b 1
)

REM Preparar el entorno
echo.
echo Fase 1: Verificando dependencias...
python verificar_sistema.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: Verificación de sistema fallida.
    pause
    exit /b %ERRORLEVEL%
)

REM Crear ejecutable
echo.
echo Fase 2: Creando ejecutable de la aplicación...
call crear_ejecutable.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error al crear el ejecutable
    pause
    exit /b %ERRORLEVEL%
)

REM Crear directorio de construcción
echo.
echo Fase 3: Preparando archivos para el instalador...
if not exist build mkdir build
copy dist\DiagSoft.exe build\
copy ventas.db build\
copy config.ini build\
copy installer.nsi build\

REM Ir al directorio de construcción
cd build

REM Compilar el instalador NSIS
echo.
echo Fase 4: Generando instalador...
makensis installer.nsi
if %ERRORLEVEL% NEQ 0 (
    echo Error al generar el instalador con NSIS
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

REM Mover el instalador generado al directorio principal
echo.
echo Fase 5: Finalizando...
move DiagSoft_Setup.exe ..\DiagSoft_Setup.exe

REM Volver al directorio principal
cd ..

echo.
echo =========================================================
echo =                INSTALADOR CREADO                      =
echo =========================================================
echo.
echo El instalador ha sido creado correctamente como "DiagSoft_Setup.exe"
echo.
echo Este instalador se puede distribuir a cualquier usuario para instalar
echo DiagSoft en su sistema Windows.
echo.
echo Características del instalador:
echo  - Instalación y desinstalación completa
echo  - Accesos directos en menú inicio y escritorio
echo  - Registro correcto en el sistema
echo  - Interfaz moderna y profesional
echo  - Soporte para actualización de versiones anteriores
echo.
pause 