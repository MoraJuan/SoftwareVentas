import flet as ft
from pages.inventory import PageInventory
from pages.reports import PageReports
from services.authService import AuthService
from ui.components import show_error_message, show_success_message, NavigationRail
import logging
from pages.dashboard import PageDashboard


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

        # Guardar el manejador original si existe
        original_on_resize = self.page.on_resize
        if original_on_resize and original_on_resize != self.handle_resize:
            self._original_on_resize = original_on_resize
            # Asignar un nuevo manejador que llame a ambos

            def combined_resize_handler(e):
                self.handle_resize(e)
                self._original_on_resize(e)
            self.page.on_resize = combined_resize_handler
        else:
            # Si no hay manejador previo, asignar el nuestro
            self.page.on_resize = self.handle_resize

    def build_ui(self):
        # Contenedor para el contenido principal
        self.content_container = ft.Container(
            content=self.get_dashboard_view(),
            expand=True,
            # Agregar margen para evitar superposición
            margin=ft.margin.all(0),
            # Ajustar el ancho para evitar conflicto con la barra de navegación
            width=self.page.width - (200 if not self.is_mobile else 0),
        )

        # Diseño según el tamaño de pantalla
        if self.is_mobile:
            self.layout = ft.Column(
                controls=[
                    # Contenido principal
                    self.content_container,
                    # BottomNavigationBar
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
                spacing=0,  # Reducir el espacio entre elementos
                expand=True,
            )
            
        # Asignar el layout a los controles
        self.controls = [self.layout]

    # Métodos para obtener las diferentes vistas
    def get_dashboard_view(self):
        try:
            return PageDashboard(self.page, self.session)
        except Exception as e:
            logging.error(f"Error al cargar la vista de dashboard: {str(e)}")
            return ft.Column(
                controls=[
                    ft.Text("Error al cargar el dashboard", size=24,
                            weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                    ft.Text(f"Detalles: {str(e)}",
                            size=16, color=ft.colors.ERROR),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
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

    def get_suppliers_view(self):
        try:
            from pages.supplier.page_factory import SupplierPageFactory
            return SupplierPageFactory.create_supplier_page(
                self.page,
                self.session,
                lambda: self.handle_navigation_change(0)  # Volver al dashboard
            )
        except Exception as e:
            logging.error(f"Error al cargar la vista de proveedores: {str(e)}")
            return ft.Column(
                controls=[
                    ft.Text("Error al cargar proveedores", size=24,
                            weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                    ft.Text(f"Detalles: {str(e)}",
                            size=16, color=ft.colors.ERROR),
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
                self.update()
                self.page.update()
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
        try:
            new_is_mobile = self.page.width < 600

            if new_is_mobile != self.is_mobile:
                self.is_mobile = new_is_mobile
                self.build_ui()
                self.update()
            else:
                if not self.is_mobile:
                    nav_width = 200 if self.page.width > 1000 else 80
                    content_width = self.page.width - nav_width - 1
                    self.content_container.width = content_width
                else:
                    self.content_container.width = self.page.width
            
                # Asegurar que PageDashboard se actualice correctamente
                if isinstance(self.content_container.content, PageDashboard):
                    self.content_container.content.update()

                self.update()

        except Exception as e:
            logging.error(f"Error en HomeView.handle_resize: {str(e)}")


    def build(self):
        return self.layout
