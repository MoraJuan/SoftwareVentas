import flet as ft
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import json
import os
import platform
import sys

from pages.auth.login import LoginView
from pages.auth.register import RegisterView
from pages import HomeView

#* Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#* Determinar el sistema operativo
IS_WINDOWS = platform.system() == "Windows"
logger.info(f"Sistema operativo detectado: {platform.system()}")

#* Rutas públicas que no requieren autenticación
PUBLIC_ROUTES = ["/login", "/register"]

#* Constantes para el tamaño de la aplicación
MIN_WINDOW_WIDTH = 800  # Ancho mínimo para la aplicación (en pixeles)
MIN_WINDOW_HEIGHT = 600  # Alto mínimo para la aplicación (en pixeles)
DEFAULT_WINDOW_WIDTH = 1024  # Ancho por defecto para escritorio
DEFAULT_WINDOW_HEIGHT = 768  # Alto por defecto para escritorio

def main(page: ft.Page):
    try:
        #* Configurar la página
        if IS_WINDOWS:
            # En Windows, usar el archivo .ico que es mejor soportado
            page.window.icon = "icon_windows.ico"
            logger.info("Usando icono específico para Windows")
            
            # Configuraciones específicas para Windows
            page.window.bgcolor = "#FFFFFF"
            page.window.title_bar_bgcolor = "#2196F3"
            page.window.title_bar_buttons_bgcolor = "#64B5F6"
            page.window.title_bar_icon_color = "#FFFFFF"
            page.window.frameless = False  # Usar marco de ventana estándar
            page.window.focused_border_color = "#2196F3"  # Color de borde con foco
            page.window.opacity = 1.0  # Opacidad completa para mejor legibilidad
            page.window.title_bar_hidden = False  # Mostrar barra de título
        else:
            # En otros sistemas, usar el PNG
            page.window.icon = "icon.png"
        
        page.title = "Sistema de Ventas"
        
        # Iniciar en pantalla completa siempre, independientemente del SO
        page.window.maximized = True
        page.window.fullscreen = True  # Forzar el modo pantalla completa
        
        # Guardar las dimensiones para cuando el usuario salga del modo pantalla completa
        page.window.width = DEFAULT_WINDOW_WIDTH
        page.window.height = DEFAULT_WINDOW_HEIGHT
        
        # Centrar la ventana - no podemos usar screen_height directamente en Flet
        # En su lugar, usamos un enfoque más simple (la ventana se posicionará automáticamente)
        page.window.top = None  # Permitir que el sistema operativo posicione la ventana
        page.window.left = None # Permitir que el sistema operativo posicione la ventana
        
        # Definir tamaños mínimos
        page.window.min_width = MIN_WINDOW_WIDTH
        page.window.min_height = MIN_WINDOW_HEIGHT
        
        # Proveer un botón para maximizar si el usuario lo desea
        page.window.maximizable = True
        
        # Evento para manejar cuando la aplicación cambie de tamaño
        def window_event_handler(e):
            logger.info(f"Evento de ventana: {e.data}")
            # Cuando la ventana cambia de tamaño, forzar un evento de resize para actualizar la UI
            if e.data == "resize":
                logger.info(f"Ventana redimensionada a: {page.window.width}x{page.window.height}")
                # Actualizar variables is_mobile e is_tablet en componentes activos
                _update_responsive_state(page)
                # Forzar actualización de componentes
                if hasattr(page, "on_resize") and page.on_resize is not None:
                    page.on_resize(e)
                page.update()
        
        # Función para actualizar estado responsive en componentes activos
        def _update_responsive_state(page):
            try:
                # Actualizar la propiedad is_mobile en la vista actual y sus controles
                for view in page.views:
                    if hasattr(view, "is_mobile"):
                        view.is_mobile = page.width < 600
                    if hasattr(view, "is_tablet"):
                        view.is_tablet = 600 <= page.width < 1024
                    
                    # Propagar a los controles que tengan estas propiedades
                    for control in view.controls:
                        if hasattr(control, "is_mobile"):
                            control.is_mobile = page.width < 600
                        if hasattr(control, "is_tablet"):
                            control.is_tablet = 600 <= page.width < 1024
                        
                        # Si el control tiene un método handle_resize, llamarlo
                        if hasattr(control, "handle_resize"):
                            control.handle_resize(None)
            except Exception as e:
                logger.error(f"Error al actualizar estado responsive: {str(e)}")
        
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
                
                view = None
                if page.route == "/login":
                    logger.info("Cargando vista de login")
                    view = LoginView(page, session)
                elif page.route == "/register":
                    logger.info("Cargando vista de registro")
                    view = RegisterView(page, session)
                elif page.route == "/":
                    logger.info("Cargando vista de dashboard")
                    view = HomeView(page, session)
                else:
                    logger.info(f"Ruta no encontrada: {page.route}")
                    if is_authenticated():
                        view = HomeView(page, session)
                    else:
                        view = LoginView(page, session)
                
                # Actualizar propiedades responsive de la vista
                if hasattr(view, "is_mobile"):
                    view.is_mobile = page.width < 600
                if hasattr(view, "is_tablet"):
                    view.is_tablet = 600 <= page.width < 1024
                
                page.views.append(view)
                page.update()
                
                # Asegurar que los controles se actualicen después de cargar
                if hasattr(view, "handle_resize"):
                    view.handle_resize(None)
                
            except Exception as e:
                logger.error(f"Error en cambio de ruta: {str(e)}")
                page.views.clear()
                if is_authenticated():
                    view = HomeView(page, session)
                    if hasattr(view, "is_mobile"):
                        view.is_mobile = page.width < 600
                    if hasattr(view, "is_tablet"):
                        view.is_tablet = 600 <= page.width < 1024
                    page.views.append(view)
                else:
                    view = LoginView(page, session)
                    if hasattr(view, "is_mobile"):
                        view.is_mobile = page.width < 600
                    if hasattr(view, "is_tablet"):
                        view.is_tablet = 600 <= page.width < 1024
                    page.views.append(view)
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
    # Flet solo acepta assets_dir como parámetro directo, el resto de configuraciones
    # de ventana deben hacerse dentro de la función main
    ft.app(target=main, assets_dir="assets")