import flet as ft
from pages.inventory import PageInventory
from pages.reports import PageReports
from pages.sales import PageSales
from services.authService import AuthService
from ui.components import show_error_message, show_success_message, NavigationRail
from ui.components.navigation import MOBILE_BREAKPOINT, TABLET_BREAKPOINT, LARGE_DESKTOP_BREAKPOINT
import logging


class HomeView(ft.UserControl):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.session = session
        self.auth_service = AuthService(session)
        
        # Inicializar valores por defecto para pantalla completa
        self.is_mobile = False
        self.is_tablet = False
        self.is_large_desktop = True  # Default para pantalla completa
        
        # La detección real se hará en build_ui() cuando la página esté cargada
        self.navigation_rail = NavigationRail(
            page=self.page,
            selected_index=0,
            on_change=self.handle_navigation_change
        )
        self.content_container = None
        self.layout = None
        self.build_ui()
        self.page.on_resize = self.handle_resize  # Listener para redimensionamiento

    def determine_device_type(self):
        """Determina el tipo de dispositivo basado en el ancho de la pantalla"""
        if not hasattr(self.page, 'width') or self.page.width is None:
            # Si no podemos obtener el ancho, asumimos pantalla completa/desktop
            logging.info("HomeView: No se pudo determinar el ancho de la pantalla, asumiendo pantalla completa")
            self.is_mobile = False
            self.is_tablet = False
            self.is_large_desktop = True
            return
            
        width = self.page.width
        logging.info(f"HomeView: Ancho de pantalla detectado: {width}px")
        
        self.is_mobile = width < MOBILE_BREAKPOINT
        self.is_tablet = MOBILE_BREAKPOINT <= width < TABLET_BREAKPOINT
        self.is_large_desktop = width >= LARGE_DESKTOP_BREAKPOINT
        
        logging.info(f"HomeView: Tipo de dispositivo: mobile={self.is_mobile}, tablet={self.is_tablet}, large_desktop={self.is_large_desktop}")

    def build_ui(self):
        # Actualizar tipo de dispositivo
        self.determine_device_type()
        
        # Obtener dimensiones reales de la ventana para pantalla completa
        available_width = self.page.window.width if hasattr(self.page, 'window') and hasattr(self.page.window, 'width') else self.page.width
        available_height = self.page.window.height if hasattr(self.page, 'window') and hasattr(self.page.window, 'height') else self.page.height
        
        # Valores por defecto si no se pueden determinar
        if not available_width or available_width <= 0:
            available_width = 1200
        if not available_height or available_height <= 0:
            available_height = 800
            
        logging.info(f"HomeView: Tamaño disponible: {available_width}x{available_height}px")
            
        # Contenedor para el contenido principal con padding adaptativo según el dispositivo
        padding_value = 8 if self.is_mobile else 12 if self.is_tablet else 20
        
        self.content_container = ft.Container(
            content=self.get_dashboard_view(),
            expand=True,
            padding=padding_value,
            alignment=ft.alignment.top_left,
        )

        # Diseño según el tamaño de pantalla
        if self.is_mobile:
            self.layout = ft.Column(
                controls=[
                    # Contenido principal
                    ft.Container(
                        content=self.content_container,
                        expand=True,
                        # Espacio para que no se superponga con la barra de navegación
                        margin=ft.margin.only(bottom=5),
                    ),
                    # NavigationBar (ya manejado por NavigationRail)
                    # Asegurar que el navegador ocupe todo el ancho disponible
                    ft.Container(
                        content=self.navigation_rail,
                        width=available_width,
                    ),
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
                    # Contenido principal con expand para ocupar el espacio disponible
                    self.content_container,
                ],
                spacing=0,  # Espaciado cero para maximizar espacio
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
                # Asegurar que ocupe todo el ancho y alto disponible
                width=available_width,
                height=available_height,
            )

    # Métodos para obtener las diferentes vistas
    def get_dashboard_view(self):
        # Tamaños ajustados según el tipo de dispositivo
        header_size = 18 if self.is_mobile else 20 if self.is_tablet else 24
        text_size = 14 if self.is_mobile else 15 if self.is_tablet else 16
        
        return ft.Column(
            controls=[
                ft.Text("Dashboard", size=header_size, weight=ft.FontWeight.BOLD),
                ft.Text("Bienvenido al sistema de ventas", size=text_size),
            ],
            spacing=16 if self.is_mobile else 20,
            scroll=ft.ScrollMode.AUTO,  # Permitir desplazamiento en pantallas pequeñas
        )

    def get_sales_view(self):
        try:
            return PageSales(self.page, self.session)
        except Exception as e:
            logging.error(f"Error al cargar la vista de ventas: {str(e)}")
            return ft.Column(
                controls=[
                    ft.Text("Error al cargar la vista de ventas", size=24,
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
        return ft.Column(
            controls=[
                ft.Text("Proveedores", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Gestión de proveedores", size=16),
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
                
                # Si estamos en la vista de ventas (índice 1), asegurar que se carguen los datos
                if index == 1:
                    logging.info("Navegando a la vista de ventas, cargando datos...")
                    
                    # Verificar si la vista de ventas tiene el método load_sales
                    if hasattr(view, 'load_sales') and callable(view.load_sales):
                        logging.info("Ejecutando load_sales en la vista de ventas...")
                        # Actualizar componentes antes de cargar ventas
                        self.content_container.update()
                        self.update()
                        
                        # Cargar las ventas
                        view.load_sales()
                        
                        # Forzar actualización después de cargar
                        view.update()
                        self.content_container.update()
                        self.update()
                        self.page.update()
                        
                    # Alternativamente, si solo tiene silent_refresh_data
                    elif hasattr(view, 'silent_refresh_data') and callable(view.silent_refresh_data):
                        logging.info("Ejecutando silent_refresh_data en la vista de ventas...")
                        # Actualizar componentes antes de cargar ventas
                        self.content_container.update()
                        self.update()
                        
                        # Cargar las ventas silenciosamente
                        view.silent_refresh_data()
                        
                        # Forzar actualización después de cargar
                        view.update()
                        self.content_container.update()
                        self.update()
                        self.page.update()
                    
                    # Alternativamente, si solo tiene refresh_data
                    elif hasattr(view, 'refresh_data') and callable(view.refresh_data):
                        logging.info("Ejecutando refresh_data en la vista de ventas...")
                        # Actualizar componentes antes de cargar ventas
                        self.content_container.update()
                        self.update()
                        
                        # Cargar las ventas
                        view.refresh_data()
                        
                        # Forzar actualización después de cargar
                        view.update()
                        self.content_container.update()
                        self.update()
                        self.page.update()
                    else:
                        logging.warning("La vista de ventas no tiene métodos para cargar datos automáticamente")
                
                # Actualizar la página completa
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

    def build(self):
        return self.layout
