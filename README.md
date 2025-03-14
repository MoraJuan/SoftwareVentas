# Sistema de Gestión de Ventas DiagSoft

Este es un sistema de gestión de ventas desarrollado con Python y Flet.

## Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## Instalación
1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Window

1. Clonar el repositorio
2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Inicializar la base de datos:
   ```
   python init_db.py
   ```

## Ejecución

Para ejecutar la aplicación:

```
python main.py
```

## Credenciales por defecto

- Usuario: admin
- Contraseña: admin123

## Funcionalidades

- **Dashboard**: Vista general del sistema
- **Ventas**: Gestión de ventas y clientes
- **Inventario**: Gestión de productos y stock
- **Reportes**: Informes de ventas, gastos, inventario y clientes
- **Proveedores**: Gestión de proveedores

## Rutas disponibles

- `/`: Dashboard
- `/login`: Inicio de sesión
- `/register`: Registro de usuarios
- `/ver_ventas`: Gestión de ventas
- `/realizar_venta`: Realizar una nueva venta
- `/ver_inventario`: Gestión de inventario
- `/ver_reportes`: Reportes generales
- `/ver_reportes/ventas`: Reportes de ventas
- `/ver_reportes/gastos`: Reportes de gastos
- `/ver_proveedores`: Gestión de proveedores

## Solución de problemas

Si la aplicación no muestra la pantalla de inicio de sesión, puede forzar el cierre de sesión descomentando la siguiente línea en `main.py`:

```python
# page.client_storage.remove("token")
```