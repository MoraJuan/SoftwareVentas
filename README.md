# DiagSoft - Sistema de Gestión

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar el proyecto en modo desarrollo:
```bash
pip install -e .
```

3. Configurar variables de entorno:
- Copiar `.env.example` a `.env`
- Actualizar las variables con tus valores

4. Inicializar la base de datos y crear admin:
```bash
python scripts/init_admin.py
```

5. Ejecutar la aplicación:
```bash
python main.py
```

## Credenciales por defecto

- Usuario: admin
- Contraseña: admin123

## Estructura del proyecto

```
diagsoft/
├── database/         # Configuración de base de datos
├── models/          # Modelos de datos
├── pages/           # Vistas de la aplicación
├── services/        # Lógica de negocio
├── ui/             # Componentes de interfaz
└── scripts/        # Scripts de utilidad
```