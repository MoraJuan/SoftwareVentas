import flet as ft
from pages.inventory import PageInventory
from pages.reports import PageReports
from services.authService import AuthService
from ui.components import show_error_message, show_success_message, NavigationRail
import logging


class HomeView(ft.UserControl):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.session = session
        self.auth_service = AuthService(session)
        self.is_mobile = self.page.width < 600  # Breakpoint para móvil
        self.navigation_rail = NavigationRail(
            page=self.page,
            selected_index=0,
            on_change=self.handle_navigation_change
        )
        self.content_container = None
        self.layout = None
        self.build_ui()
        self.page.on_resize = self.handle_resize  # Listener para redimensionamiento

    def build_ui(self):
        # Contenedor para el contenido principal
        self.content_container = ft.Container(
            content=self.get_dashboard_view(),
            expand=True,
            padding=10,
            alignment=ft.alignment.top_left,
        )

        # Diseño según el tamaño de pantalla
        if self.is_mobile:
            self.layout = ft.Column(
                controls=[
                    # Contenido principal
                    ft.Container(self.content_container, expand=True),
                    # BottomNavigationBar (ya manejado por NavigationRail)
                    self.navigation_rail,
                ],
                spacing=0,
                expand=True,
            )
        else:
            self.layout = ft.Row(
                controls=[
                    self.navigation_rail,  # NavigationRail a la izquierda
                    ft.VerticalDivider(width=1),
                    self.content_container,  # Contenido principal
                ],
                expand=True,
            )

    # Métodos para obtener las diferentes vistas
    def get_dashboard_view(self):
        return ft.Column(
            controls=[
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Bienvenido al sistema de ventas", size=16),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,  # Permitir desplazamiento en pantallas pequeñas
        )

    def get_sales_view(self):
        return ft.Column(
            controls=[
                ft.Text("Ventas", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Gestión de ventas", size=16),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

    def get_inventory_view(self):
        try:
            return PageInventory(self.page, self.session)
        except Exception as e:
            logging.error(f"Error al cargar la vista de inventario: {str(e)}")
            return ft.Column(
                controls=[
                    ft.Text("Error al cargar el inventario", size=24,
                            weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                    ft.Text(f"Detalles: {str(e)}",
                            size=16, color=ft.colors.ERROR),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )

    def get_reports_view(self):
        try:
            return PageReports(self.page, self.session)
        except Exception as e:
            logging.error(f"Error al cargar la vista de inventario: {str(e)}")
            return ft.Column(
                controls=[
                    ft.Text("Error al cargar el inventario", size=24,
                            weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                    ft.Text(f"Detalles: {str(e)}",
                            size=16, color=ft.colors.ERROR),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )

        # return ft.Column(
        #     controls=[
        #         ft.Text("Reportes", size=24, weight=ft.FontWeight.BOLD),
        #         ft.Text("Informes y estadísticas", size=16),
        #     ],
        #     spacing=20,
        #     scroll=ft.ScrollMode.AUTO,
        # )

    def get_suppliers_view(self):
        return ft.Column(
            controls=[
                ft.Text("Proveedores", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Gestión de proveedores", size=16),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

    # Manejar el cambio de vista
    def handle_navigation_change(self, index):
        try:
            views = [
                self.get_dashboard_view,
                self.get_sales_view,
                self.get_inventory_view,
                self.get_reports_view,
                self.get_suppliers_view,
            ]
            # Asegurarse de que el índice esté dentro del rango
            if 0 <= index < len(views):
                view = views[index]()
                self.content_container.content = view
                self.page.update()  # Actualizar la página completa
            else:
                self.content_container.content = self.get_dashboard_view()  # Fallback
            self.update()
        except Exception as e:
            logging.error(f"Error al cambiar de vista: {str(e)}")
            show_error_message(
                self.page, f"Error al cambiar de vista: {str(e)}")
            # Mantener la vista actual o mostrar un error
            self.content_container.content = ft.Column(
                controls=[
                    ft.Text("Error al cambiar de vista", size=24,
                            weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                    ft.Text(f"{str(e)}", size=16, color=ft.colors.ERROR),
                ],
                spacing=20
            )
            self.update()

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()  # Reconstruir el diseño
            self.update()

    def build(self):
        return self.layout
