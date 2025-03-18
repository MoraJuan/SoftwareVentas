@echo off
echo ===== Creando ejecutable de DiagSoft =====
echo.
echo 1. Instalando dependencias...
pip install -r requirements.txt --upgrade
pip install pyinstaller

echo.
echo 2. Creando ejecutable...
pyinstaller --name DiagSoft --icon=assets/icon.ico --onefile --noconsole ^
  --add-data "assets;assets" ^
  --add-data "database;database" ^
  --add-data "models;models" ^
  --add-data "pages;pages" ^
  --add-data "services;services" ^
  --add-data "ui;ui" ^
  --add-data "utils;utils" ^
  --add-data "requirements.txt;." ^
  --add-data "ventas.db;." ^
  --hidden-import pandas ^
  --hidden-import matplotlib ^
  --hidden-import sqlalchemy ^
  --hidden-import bcrypt ^
  --hidden-import pillow ^
  --hidden-import reportlab ^
  main.py

echo.
echo 3. Limpiando archivos temporales...
del /s /q DiagSoft.spec

echo.
echo ===== Ejecutable creado con éxito =====
echo El archivo ejecutable se encuentra en la carpeta "dist"
echo.
pause 