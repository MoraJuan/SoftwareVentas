import importlib
import sys
import subprocess
import os
import platform

def check_module(module_name):
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def check_all_dependencies():
    # Obtener el sistema operativo actual
    os_name = platform.system()
    print(f"Sistema operativo detectado: {os_name}")
    
    # Leer el archivo requirements.txt
    print("\n=== Verificando dependencias ===")
    with open("requirements.txt", "r") as file:
        dependencies = [line.strip() for line in file.readlines() if line.strip() and not line.strip().startswith('#')]
    
    missing_dependencies = []
    for dep in dependencies:
        # Extraer el nombre del módulo (antes de ==, >=, etc.)
        parts = dep.split(';')[0].strip()  # Manejar condicionales como 'pywin32>=300; platform_system=="Windows"'
        if any(operator in parts for operator in ['==', '>=', '<=', '>', '<', '~=']):
            module_name = parts.split(next(op for op in ['==', '>=', '<=', '>', '<', '~='] if op in parts))[0].strip()
        else:
            module_name = parts
            
        # Ajustes para nombres de módulos especiales
        module_map = {
            'python-jose[cryptography]': 'jose',
            'python-multipart': 'multipart',
            'sqlalchemy-utils': 'sqlalchemy_utils',
            'python-dotenv': 'dotenv',
            'typing-extensions': 'typing_extensions'
        }
        
        if module_name.lower() in module_map:
            module_name = module_map[module_name.lower()]
        
        # Verificar si el módulo está instalado
        is_installed = check_module(module_name)
        status = "✓" if is_installed else "✗"
        print(f"{status} {module_name}")
        
        if not is_installed:
            missing_dependencies.append(dep)
    
    # Resumen
    if missing_dependencies:
        print("\n=== Dependencias faltantes ===")
        for dep in missing_dependencies:
            print(f"- {dep}")
        print("\nEjecutando: pip install -r requirements.txt --upgrade")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"])
        
        # Verificar PyInstaller por separado
        if not check_module("PyInstaller"):
            print("\nInstalando PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    else:
        print("\n✅ Todas las dependencias están instaladas correctamente")
    
    # Verificar que existan las carpetas requeridas
    print("\n=== Verificando estructura de carpetas ===")
    required_folders = ["assets", "database", "models", "pages", "services", "ui", "utils"]
    missing_folders = []
    
    for folder in required_folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            print(f"✓ {folder}")
        else:
            print(f"✗ {folder}")
            missing_folders.append(folder)
    
    if missing_folders:
        print("\n❌ Faltan algunas carpetas requeridas. Por favor, asegúrate de que existan:")
        for folder in missing_folders:
            print(f"- {folder}")
        return False
    
    # Verificar que exista el archivo principal
    if not os.path.exists("main.py"):
        print("\n❌ No se encontró el archivo main.py")
        return False
        
    print("\n✅ La estructura del proyecto es correcta")
    return True

if __name__ == "__main__":
    if check_all_dependencies():
        print("\n✅ El sistema está listo para crear el ejecutable")
        print("Puede ejecutar 'crear_ejecutable.bat' para generar el archivo .exe")
    else:
        print("\n❌ Por favor, corrija los problemas mencionados antes de crear el ejecutable")
        sys.exit(1) 