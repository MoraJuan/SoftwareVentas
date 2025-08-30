import flet as ft
import logging
import json
import os
import platform
import sys

from pages.auth.login import LoginView
from pages.auth.register import RegisterView
from pages import HomeView
from database.connection import SessionLocal, init_db

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"
logger.info(f"Sistema operativo detectado: {platform.system()}")

MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_WIDTH = 1024
DEFAULT_WINDOW_HEIGHT = 768


def main(page: ft.Page):
    try:
        # Configuración de ventana
        if IS_WINDOWS:
            page.window.icon = "icon_windows.ico"
            page.window.bgcolor = "#FFFFFF"
            page.window.title_bar_bgcolor = "#2196F3"
            page.window.title_bar_buttons_bgcolor = "#64B5F6"
            page.window.title_bar_icon_color = "#FFFFFF"
            page.window.frameless = False
            page.window.focused_border_color = "#2196F3"
            page.window.opacity = 1.0
            page.window.title_bar_hidden = False
        else:
            page.window.icon = "icon.png"

        page.title = "Sistema de Ventas"
        page.window.maximized = True
        page.window.fullscreen = True
        page.window.width = DEFAULT_WINDOW_WIDTH
        page.window.height = DEFAULT_WINDOW_HEIGHT
        page.window.top = None
        page.window.left = None
        page.window.min_width = MIN_WINDOW_WIDTH
        page.window.min_height = MIN_WINDOW_HEIGHT
        page.window.maximizable = True

        def window_event_handler(e):
            logger.info(f"Evento de ventana: {e.data}")
            if e.data == "resize":
                logger.info(f"Ventana redimensionada a: {page.window.width}x{page.window.height}")
                _update_responsive_state(page)
                if hasattr(page, "on_resize") and page.on_resize is not None:
                    page.on_resize(e)
                page.update()

        def _update_responsive_state(page):
            try:
                for view in page.views:
                    if hasattr(view, "is_mobile"):
                        view.is_mobile = page.width < 600
                    if hasattr(view, "is_tablet"):
                        view.is_tablet = 600 <= page.width < 1024
                    for control in getattr(view, "controls", []):
                        if hasattr(control, "is_mobile"):
                            control.is_mobile = page.width < 600
                        if hasattr(control, "is_tablet"):
                            control.is_tablet = 600 <= page.width < 1024
                        if hasattr(control, "handle_resize"):
                            control.handle_resize(None)
            except Exception as e:
                logger.error(f"Error al actualizar estado responsive: {str(e)}")

        page.window.on_event = window_event_handler
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.update()

        # Base de datos: crear tablas y sesión
        init_db()
        session = SessionLocal()

        # Preferencia de tema
        def load_theme_preference():
            try:
                if os.path.exists("theme_preference.json"):
                    with open("theme_preference.json", "r") as f:
                        data = json.load(f)
                        return data.get("theme_mode", "light")
                return "light"
            except Exception as e:
                logger.error(f"Error al cargar preferencia de tema: {str(e)}")
                return "light"

        def save_theme_preference(theme_mode):
            try:
                with open("theme_preference.json", "w") as f:
                    json.dump({"theme_mode": theme_mode}, f)
            except Exception as e:
                logger.error(f"Error al guardar preferencia de tema: {str(e)}")

        def toggle_theme():
            try:
                page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
                save_theme_preference("dark" if page.theme_mode == ft.ThemeMode.DARK else "light")
                page.update()
            except Exception as e:
                logger.error(f"Error al cambiar tema: {str(e)}")

        page.toggle_theme = toggle_theme
        theme_preference = load_theme_preference()
        page.theme_mode = ft.ThemeMode.DARK if theme_preference == "dark" else ft.ThemeMode.LIGHT
        page.update()

        # Auth helpers
        def is_authenticated():
            token = page.client_storage.get("token")
            return token is not None

        # Navegación
        def route_change(route):
            try:
                page.views.clear()
                view = None
                if page.route == "/login":
                    view = LoginView(page, session)
                elif page.route == "/register":
                    view = RegisterView(page, session)
                elif page.route == "/":
                    view = HomeView(page, session)
                else:
                    if is_authenticated():
                        view = HomeView(page, session)
                    else:
                        view = LoginView(page, session)

                if hasattr(view, "is_mobile"):
                    view.is_mobile = page.width < 600
                if hasattr(view, "is_tablet"):
                    view.is_tablet = 600 <= page.width < 1024

                page.views.append(view)
                page.update()

                if hasattr(view, "handle_resize"):
                    view.handle_resize(None)
            except Exception as e:
                logger.error(f"Error en cambio de ruta: {str(e)}")
                page.views.clear()
                fallback = HomeView(page, session) if is_authenticated() else LoginView(page, session)
                if hasattr(fallback, "is_mobile"):
                    fallback.is_mobile = page.width < 600
                if hasattr(fallback, "is_tablet"):
                    fallback.is_tablet = 600 <= page.width < 1024
                page.views.append(fallback)
                page.update()

        def view_pop(view):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop

        if is_authenticated():
            page.go("/")
        else:
            page.go("/login")

    except Exception as e:
        logger.error(f"Error en la inicialización de la aplicación: {str(e)}")
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=64),
                        ft.Text("Error al iniciar la aplicación", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                        ft.Text(str(e), color=ft.colors.ON_SURFACE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            )
        )
        page.update()


if __name__ == "__main__":
    base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, "assets")
    ft.app(target=main, assets_dir=assets_dir)