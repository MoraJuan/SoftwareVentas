import flet as ft
import logging

from ui.components.alerts import show_error_message

class NavigationRail(ft.UserControl):
    def __init__(self, page: ft.Page, selected_index: int = 0, on_change=None):
        super().__init__()
        self.page = page
        self.selected_index = selected_index
        self.on_change = on_change  # Callback para manejar el cambio de vista
        self.destinations = [
            (ft.icons.DASHBOARD_OUTLINED, ft.icons.DASHBOARD_ROUNDED, "Dashboard"),
            (ft.icons.SHOPPING_CART_OUTLINED, ft.icons.SHOPPING_CART_ROUNDED, "Ventas"),
            (ft.icons.INVENTORY_2_OUTLINED, ft.icons.INVENTORY_2_ROUNDED, "Inventario"),
            (ft.icons.ASSESSMENT_OUTLINED, ft.icons.ASSESSMENT_ROUNDED, "Reportes"),
        ]
        self.is_mobile = self.page.width < 600
        self.nav_control = None

    def build(self):
        try:
            nav_items = [
                ft.NavigationDestination(
                    icon=icon,
                    selected_icon=selected_icon,
                    label=label,
                ) for icon, selected_icon, label in self.destinations
            ]

            logout_button = ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
                tooltip="Cerrar Sesión",
                on_click=self.handle_logout
            )

            logo_container = ft.Container(
                content=ft.Row([
                    ft.Icon(name=ft.icons.STORE_ROUNDED, size=28, color=ft.colors.PRIMARY),
                    ft.Text("DiagSoft", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                margin=ft.margin.only(top=20, bottom=30),
                padding=ft.padding.all(8)
            )

            # No asignar manejador de resize desde aquí para evitar conflictos con HomeView

            if self.is_mobile:
                self.nav_control = ft.NavigationBar(
                    destinations=nav_items,
                    selected_index=self.selected_index,
                    on_change=self.handle_navigation,
                    bgcolor=ft.colors.SURFACE,
                    elevation=8,
                )
            else:
                rail_destinations = [
                    ft.NavigationRailDestination(
                        icon=icon,
                        selected_icon=selected_icon,
                        label=label,
                        padding=8
                    ) for icon, selected_icon, label in self.destinations
                ]
                
                self.nav_control = ft.Container(
                    content=ft.Column([
                        logo_container,
                        ft.Container(
                            content=ft.NavigationRail(
                                selected_index=self.selected_index,
                                label_type=ft.NavigationRailLabelType.ALL if self.page.width > 800 else ft.NavigationRailLabelType.SELECTED,
                                min_width=70,
                                min_extended_width=200,
                                extended=self.page.width > 1000,
                                destinations=rail_destinations,
                                on_change=self.handle_navigation,
                                bgcolor=ft.colors.SURFACE,
                            ),
                            expand=True,
                        ),
                        ft.Container(content=logout_button, margin=ft.margin.only(bottom=20))
                    ], 
                    spacing=0,
                    expand=True),
                    width=200 if self.page.width > 1000 else 80,
                    height=self.page.height if self.page.height else 800,
                    # bgcolor=ft.colors.SURFACE_VARIANT,
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.OUTLINE)),
                )

            return self.nav_control

        except Exception as e:
            logging.error(f"Error construyendo NavigationRail: {str(e)}")
            return ft.Text("Error en la navegación", color=ft.colors.ERROR)

    def handle_navigation(self, e):
        try:
            index = e.control.selected_index
            if self.on_change and callable(self.on_change):  # Verificar que on_change sea callable
                self.on_change(index)
            else:
                logging.warning("on_change no es callable o no está definido")
            self.selected_index = index
            self.update()
        except Exception as e:
            logging.error(f"Error en navegación: {str(e)}")
            show_error_message(self.page, "Error al navegar")

    def handle_logout(self, e):
        try:
            self.page.client_storage.remove("token")
            self.page.client_storage.remove("username")
            self.page.client_storage.remove("login_time")
            self.page.go("/login")
        except Exception as e:
            logging.error(f"Error al cerrar sesión: {str(e)}")
            show_error_message(self.page, "Error al cerrar sesión")

    def handle_resize(self, e):
        try:
            new_is_mobile = self.page.width < 600
            if new_is_mobile != self.is_mobile:
                self.is_mobile = new_is_mobile
                self.nav_control = self.build()
                self.update()
            elif not self.is_mobile and isinstance(self.nav_control, ft.Container):
                self.nav_control.width = 200 if self.page.width > 1000 else 80
                self.nav_control.height = self.page.height if self.page.height else 800
                nav_rail = self.nav_control.content.controls[1].content
                nav_rail.extended = self.page.width > 1000
                nav_rail.label_type = (
                    ft.NavigationRailLabelType.ALL if self.page.width > 800 else ft.NavigationRailLabelType.SELECTED
                )
                self.update()
        except Exception as e:
            logging.error(f"Error en handle_resize: {str(e)}")