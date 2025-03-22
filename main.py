import flet as ft
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import json
import os

from pages.auth.login import LoginView
from pages.auth.register import RegisterView
from pages import HomeView

#* Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#* Rutas públicas que no requieren autenticación
PUBLIC_ROUTES = ["/login", "/register"]

def main(page: ft.Page):
    try:
        #* Configurar la página
        page.title = "Sistema de Ventas"
        page.window.width = 1200  
        page.window.height = 800  
        page.window.center()
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.update()

        #* Crear conexión a la base de datos
        engine = create_engine('sqlite:///ventas.db')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        #* Tema de la aplicación
        #? Cargar preferencia de tema guardada
        def load_theme_preference():
            try:
                if os.path.exists('theme_preference.json'):
                    with open('theme_preference.json', 'r') as f:
                        data = json.load(f)
                        return data.get('theme_mode', 'light')
                return 'light'
            except Exception as e:
                logger.error(f"Error al cargar preferencia de tema: {str(e)}")
                return 'light'

        #? Guardar preferencia de tema
        def save_theme_preference(theme_mode):
            try:
                with open('theme_preference.json', 'w') as f:
                    json.dump({'theme_mode': theme_mode}, f)
            except Exception as e:
                logger.error(f"Error al guardar preferencia de tema: {str(e)}")

        #? Cambiar el tema de la aplicación
        def toggle_theme():
            try:
                page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
                save_theme_preference('dark' if page.theme_mode == ft.ThemeMode.DARK else 'light')
                page.update()
            except Exception as e:
                logger.error(f"Error al cambiar tema: {str(e)}")

        #? Hacer la función de tema disponible globalmente
        page.toggle_theme = toggle_theme

        #? Establecer tema inicial desde preferencia guardada
        theme_preference = load_theme_preference()
        page.theme_mode = ft.ThemeMode.DARK if theme_preference == 'dark' else ft.ThemeMode.LIGHT
        page.update()
        
        #* Autenticación
        #? Verificar si el usuario está autenticado
        def is_authenticated():
            token = page.client_storage.get("token")
            return token is not None

        #* Vistas
        #? Cambiar de vista según la ruta
        def route_change(route):
            try:
                page.views.clear()

                if page.route == "/login":
                    logger.info("Cargando vista de login")
                    page.views.append(LoginView(page, session))
                elif page.route == "/register":
                    logger.info("Cargando vista de registro")
                    page.views.append(RegisterView(page, session))
                elif page.route == "/":
                    logger.info("Cargando vista de dashboard")
                    home_view = HomeView(page, session)  # Crear instancia de HomeView
                    page.views.append(home_view)  # Agregar HomeView a las vistas
                else:
                    logger.info(f"Ruta no encontrada: {page.route}")
                    if is_authenticated():
                        home_view = HomeView(page, session)  # Crear instancia de HomeView
                        page.views.append(home_view)  # Agregar HomeView a las vistas
                    else:
                        page.views.append(LoginView(page, session))

                page.update()
            except Exception as e:
                logger.error(f"Error en cambio de ruta: {str(e)}")
                page.views.clear()
                if is_authenticated():
                    home_view = HomeView(page, session)  # Crear instancia de HomeView
                    page.views.append(home_view)  # Agregar HomeView a las vistas
                else:
                    page.views.append(LoginView(page, session))
        page.update()

        #? Manejar el botón de retroceso
        def view_pop(view):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        #? Configurar manejadores de eventos
        page.on_route_change = route_change
        page.on_view_pop = view_pop

        #? Iniciar en login o dashboard según autenticación
        if is_authenticated():
            logger.info("Usuario autenticado, iniciando en dashboard")
            page.go('/')
        else:
            logger.info("Usuario no autenticado, iniciando en login")
            page.go('/login')

    #! Mostrar mensaje de error en la página
    except Exception as e:
        logger.error(f"Error en la inicialización de la aplicación: {str(e)}")
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=64),
                    ft.Text(
                        "Error al iniciar la aplicación",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Text(
                        str(e),
                        color=ft.colors.ON_SURFACE
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center
            )
        )
        page.update()

if __name__ == '__main__':
    ft.app(target=main)