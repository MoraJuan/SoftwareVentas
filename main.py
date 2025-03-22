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

#* Constantes para el tamaño de la aplicación
MIN_WINDOW_WIDTH = 600  # Ancho mínimo para la aplicación (en pixeles)
MIN_WINDOW_HEIGHT = 800  # Alto mínimo para la aplicación (en pixeles)
# No es necesario definir tamaños por defecto si usaremos pantalla completa

def main(page: ft.Page):
    try:
        #* Configurar la página
        page.window.icon = "icon.png"  # Ruta relativa al assets_dir
        page.title = "Sistema de Ventas"
        
        # Establecer pantalla completa al iniciar
        page.window.maximized = True
        
        # Mantener tamaños mínimos para cuando el usuario salga del modo pantalla completa
        page.window.min_width = MIN_WINDOW_WIDTH
        page.window.min_height = MIN_WINDOW_HEIGHT
        
        # Evento para manejar cuando la aplicación cambie de tamaño
        def window_event_handler(e):
            logger.info(f"Evento de ventana: {e.data}")
            # Cuando la ventana cambia de tamaño, forzar un evento de resize para actualizar la UI
            if e.data == "resize":
                logger.info(f"Ventana redimensionada a: {page.window.width}x{page.window.height}")
                # Forzar actualización de componentes
                if hasattr(page, "on_resize") and page.on_resize is not None:
                    page.on_resize(e)
                page.update()
                
        # Registrar el manejador de eventos de ventana
        page.window.on_event = window_event_handler
        
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.update()

        #* Crear conexión a la base de datos
        engine = create_engine('sqlite:///ventas.db')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        #* Tema de la aplicación
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

        def save_theme_preference(theme_mode):
            try:
                with open('theme_preference.json', 'w') as f:
                    json.dump({'theme_mode': theme_mode}, f)
            except Exception as e:
                logger.error(f"Error al guardar preferencia de tema: {str(e)}")

        def toggle_theme():
            try:
                page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
                save_theme_preference('dark' if page.theme_mode == ft.ThemeMode.DARK else 'light')
                page.update()
            except Exception as e:
                logger.error(f"Error al cambiar tema: {str(e)}")

        page.toggle_theme = toggle_theme

        theme_preference = load_theme_preference()
        page.theme_mode = ft.ThemeMode.DARK if theme_preference == 'dark' else ft.ThemeMode.LIGHT
        page.update()
        
        #* Autenticación
        def is_authenticated():
            token = page.client_storage.get("token")
            return token is not None

        #* Vistas
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
                    home_view = HomeView(page, session)
                    page.views.append(home_view)
                else:
                    logger.info(f"Ruta no encontrada: {page.route}")
                    if is_authenticated():
                        home_view = HomeView(page, session)
                        page.views.append(home_view)
                    else:
                        page.views.append(LoginView(page, session))
                page.update()
            except Exception as e:
                logger.error(f"Error en cambio de ruta: {str(e)}")
                page.views.clear()
                if is_authenticated():
                    home_view = HomeView(page, session)
                    page.views.append(home_view)
                else:
                    page.views.append(LoginView(page, session))
        page.update()

        def view_pop(view):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop

        if is_authenticated():
            logger.info("Usuario autenticado, iniciando en dashboard")
            page.go('/')
        else:
            logger.info("Usuario no autenticado, iniciando en login")
            page.go('/login')

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
    ft.app(target=main, assets_dir="assets")  # Agregar assets_dir para la correcta carga de recursos