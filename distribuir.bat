@echo off
echo =================================================
echo =      PREPARACION DE DIAGSOFT PARA DISTRIBUCION     =
echo =================================================
echo.

echo Fase 0: Verificando el sistema...
python verificar_sistema.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: El sistema no cumple con los requisitos necesarios.
    echo Por favor, corrija los problemas mencionados antes de continuar.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Fase 1: Preparando archivos para distribucion...
python preparar_distribucion.py
if %ERRORLEVEL% NEQ 0 (
    echo Error al preparar archivos para distribucion
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Fase 2: Entrando al directorio de distribucion...
cd distribucion

echo.
echo Fase 3: Creando el ejecutable...
call crear_ejecutable.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error al crear el ejecutable
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Fase 4: Copiando el ejecutable al directorio principal...
copy dist\DiagSoft.exe ..\DiagSoft.exe
if %ERRORLEVEL% NEQ 0 (
    echo Error al copiar el ejecutable
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Fase 5: Creando archivo ZIP para distribucion...
cd ..
echo Empaquetando DiagSoft.exe y ventas.db...
powershell Compress-Archive -Path DiagSoft.exe, ventas.db -DestinationPath DiagSoft.zip -Force
if %ERRORLEVEL% NEQ 0 (
    echo Error al crear el archivo ZIP
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Volviendo al directorio principal...
cd ..

echo.
echo =================================================
echo =          PROCESO COMPLETADO CON EXITO         =
echo =================================================
echo.
echo El ejecutable DiagSoft.exe se ha creado correctamente.
echo El archivo DiagSoft.zip contiene el ejecutable y la base de datos.
echo.
echo Para distribuir el sistema:
echo 1. Comparta el archivo DiagSoft.zip con el usuario
echo 2. El usuario solo necesita extraer el ZIP y ejecutar DiagSoft.exe
echo.
echo NOTA: La primera ejecución puede tardar unos segundos mientras 
echo se inicializan los recursos.
echo.
pause 