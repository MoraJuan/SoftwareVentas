import flet as ft
import logging

from ui.components.alerts import show_error_message

class NavigationRail(ft.UserControl):
    def __init__(self, page: ft.Page, selected_index: int = 0):
        super().__init__()
        self.page = page
        self.selected_index = selected_index
        self.destinations = [
            (ft.icons.DASHBOARD_OUTLINED, ft.icons.DASHBOARD_ROUNDED, "Dashboard", "/"),
            (ft.icons.SHOPPING_CART_OUTLINED, ft.icons.SHOPPING_CART_ROUNDED, "Ventas", "/ver_ventas"),
            (ft.icons.INVENTORY_2_OUTLINED, ft.icons.INVENTORY_2_ROUNDED, "Inventario", "/ver_inventario"),
            (ft.icons.ASSESSMENT_OUTLINED, ft.icons.ASSESSMENT_ROUNDED, "Reportes", "/ver_reportes"),
            (ft.icons.PEOPLE_OUTLINED, ft.icons.PEOPLE_ROUNDED, "Proveedores", "/ver_proveedores"),
        ]

    def build(self):
        try:
            nav_items = []
            for icon, selected_icon, label, _ in self.destinations:
                nav_items.append(
                    ft.NavigationRailDestination(
                        icon=icon,
                        selected_icon=selected_icon,
                        label=label,
                        padding=8
                    )
                )

            # Botón de cerrar sesión
            logout_button = ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
                tooltip="Cerrar Sesión",
                on_click=self.handle_logout
            )

            return ft.NavigationRail(
                selected_index=self.selected_index,
                label_type=ft.NavigationRailLabelType.SELECTED,
                min_width=70,
                min_extended_width=200,
                extended=True,
                group_alignment=-0.85,
                destinations=nav_items,
                on_change=self.handle_navigation,
                bgcolor=ft.colors.SURFACE,
                leading=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    name=ft.icons.STORE_ROUNDED,
                                    size=28,
                                    color=ft.colors.PRIMARY
                                ),
                                ft.Text(
                                    "DiagSoft",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.PRIMARY
                                )
                            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                            margin=ft.margin.only(top=20, bottom=30),
                            padding=ft.padding.all(8)
                        ),
                    ], 
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                trailing=ft.Container(
                    content=logout_button,
                    margin=ft.margin.only(bottom=20)
                )
            )
        except Exception as e:
            logging.error(f"Error construyendo NavigationRail: {str(e)}")
            return ft.Text("Error en la navegación", color=ft.colors.ERROR)

    def handle_navigation(self, e):
        try:
            index = e.control.selected_index
            route = self.destinations[index][3]  # Obtener la ruta del destino seleccionado
            self.page.go(route)
        except Exception as e:
            logging.error(f"Error en navegación: {str(e)}")
            show_error_message(self.page, "Error al navegar")
            
    def handle_logout(self, e):
        try:
            # Eliminar token y datos de sesión
            self.page.client_storage.remove("token")
            self.page.client_storage.remove("username")
            self.page.client_storage.remove("login_time")
            
            # Redirigir a login
            self.page.go("/login")
        except Exception as e:
            logging.error(f"Error al cerrar sesión: {str(e)}")
            show_error_message(self.page, "Error al cerrar sesión")

def create_navigation_rail(selected_index: int, page: ft.Page):
    return NavigationRail(page=page, selected_index=selected_index)

def get_route_for_index(index: int):
    """Obtiene la ruta correspondiente a un índice de navegación"""
    routes = [
        "/",                # Dashboard
        "/ver_ventas",      # Ventas
        "/ver_inventario",  # Inventario
        "/ver_reportes",    # Reportes
        "/ver_proveedores", # Proveedores
    ]
    if 0 <= index < len(routes):
        return routes[index]
    return "/"

class ThemeIconButton(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page

    def build(self):
        return ft.IconButton(
            icon=ft.icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE,
            icon_color=ft.colors.ON_SURFACE,
            tooltip="Cambiar tema",
            on_click=self.handle_theme_change
        )
    
    def handle_theme_change(self, e):
        try:
            self.page.toggle_theme()
            self.update()
        except Exception as e:
            logging.error(f"Error al cambiar tema: {str(e)}")
            show_error_message(self.page, "Error al cambiar el tema")