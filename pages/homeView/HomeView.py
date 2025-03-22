import flet as ft
from pages.inventory import PageInventory
from pages.reports import PageReports
from services.authService import AuthService
from ui.components import show_error_message, show_success_message, NavigationRail
import logging
from pages.dashboard import PageDashboard
from pages.sales import PageSales


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
        # Calcular dimensiones disponibles
        available_width = self.page.width if hasattr(self.page, 'width') else 1200
        available_height = self.page.height if hasattr(self.page, 'height') else 800
        
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
                # Asegurar que ocupe todo el alto disponible
                height=available_height,
                width=available_width,
            )
        else:
            # Para tablets y desktop
            self.layout = ft.Row(
                controls=[
                    self.navigation_rail,  # NavigationRail a la izquierda
                    ft.VerticalDivider(width=1),
                    self.content_container,  # Contenido principal
                ],
                spacing=0,  # Reducir el espacio entre elementos
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
                # Asegurar que ocupe todo el ancho y alto disponible
                width=available_width,
                height=available_height,
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
        try:
            return PageSales(self.page, self.session)
        except Exception as e:
            logging.error(f"Error al cargar la vista de ventas: {str(e)}")
            return ft.Column(
                controls=[
                    ft.Text("Error al cargar las ventas", size=24,
                            weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                    ft.Text(f"Detalles: {str(e)}",
                            size=16, color=ft.colors.ERROR),
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

    def handle_resize(self, e):
        # Guardar el estado actual
        old_is_mobile = self.is_mobile
        old_is_tablet = self.is_tablet
        old_is_large_desktop = getattr(self, 'is_large_desktop', False)
        
        # Actualizar el tipo de dispositivo
        self.determine_device_type()
        
        # Obtener dimensiones reales de la ventana
        available_width = self.page.window.width if hasattr(self.page, 'window') and hasattr(self.page.window, 'width') else self.page.width
        available_height = self.page.window.height if hasattr(self.page, 'window') and hasattr(self.page.window, 'height') else self.page.height
        
        # Usar valores por defecto si no se pueden determinar
        if not available_width or available_width <= 0:
            available_width = 1200
        if not available_height or available_height <= 0:
            available_height = 800
            
        logging.info(f"HomeView resize: Tamaño disponible: {available_width}x{available_height}px")
        
        # Actualizar el tamaño del contenedor de navegación en móvil si existe
        if self.is_mobile and self.layout and isinstance(self.layout, ft.Column) and len(self.layout.controls) > 1:
            nav_container = self.layout.controls[1]
            if isinstance(nav_container, ft.Container):
                nav_container.width = available_width
                
        # Actualizar el tamaño del layout en todos los casos
        if self.layout:
            self.layout.width = available_width
            self.layout.height = available_height
        
        # Reconstruir completamente si cambia el tipo de dispositivo
        if (old_is_mobile != self.is_mobile or 
            old_is_tablet != self.is_tablet):
            logging.info(f"HomeView: Cambio de tipo de dispositivo - mobile={self.is_mobile}, tablet={self.is_tablet}")
            self.build_ui()  # Reconstruir el diseño
            self.update()
            return
        
        # Ajustes finos sin reconstruir toda la UI
        if hasattr(self, 'content_container') and self.content_container is not None:
            # Ajustar padding según el tamaño
            padding_value = 8 if self.is_mobile else 12 if self.is_tablet else 20
            if self.content_container.padding != padding_value:
                self.content_container.padding = padding_value
            
            # Forzar actualización
            self.update()

    # Manejar el cambio de vista
    def handle_navigation_change(self, index):
        try:
            logging.info(f"Cambiando a la vista con índice: {index}")
            views = [
                self.get_dashboard_view,
                self.get_sales_view,
                self.get_inventory_view,
                self.get_reports_view,
                self.get_suppliers_view,
            ]
            # Asegurarse de que el índice esté dentro del rango
            if 0 <= index < len(views):
                # Crear la vista solicitada
                view = views[index]()
                self.content_container.content = view
                self.update()
                self.page.update()
            else:
                self.content_container.content = self.get_dashboard_view()  # Fallback
                self.update()
        except Exception as e:
            logging.error(f"Error al cambiar de vista: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
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
