# Sistema de Ventas e Inventario

Sistema completo para la gestión de ventas, inventario, productos, categorías y más. Desarrollado con Python y Flet.

## Características

- Gestión de productos y categorías
- Control de inventario con historial de movimientos
- Sistema de ventas y facturación
- Gestión de clientes y proveedores
- Reportes y estadísticas
- Interfaz responsiva para dispositivos móviles y de escritorio

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Inicializar la base de datos:
```bash
python init_db.py
```

4. Ejecutar la aplicación:
```bash
python main.py
```

## Credenciales por defecto

- Usuario: admin
- Contraseña: admin123

## Estructura del proyecto

```
sistema_ventas/
├── assets/          # Recursos gráficos y estáticos
├── config/          # Configuraciones generales
├── database/        # Configuración de base de datos
├── models/          # Modelos de datos
├── pages/           # Vistas de la aplicación
│   ├── auth/        # Autenticación
│   ├── categories/  # Gestión de categorías
│   ├── inventory/   # Gestión de inventario
│   ├── reports/     # Reportes y estadísticas
│   └── sales/       # Módulo de ventas
├── services/        # Lógica de negocio
├── ui/              # Componentes de interfaz
└── utils/           # Utilidades generales
```

## Desarrollo

Para desarrollo, puedes utilizar el archivo `pyproject.toml` para gestionar las dependencias y metadatos del proyecto:

```bash
# Instalación en modo desarrollo
pip install -e .
```

## Empaquetado y distribución

Para crear un ejecutable independiente:

```bash
flet pack main.py --name "SistemaVentas" --icon assets/icon.png
```