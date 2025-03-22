import flet as ft
import logging
import os

from ui.components.alerts import show_error_message

# Constantes para los breakpoints de responsive design
MOBILE_BREAKPOINT = 600
TABLET_BREAKPOINT = 1024
LARGE_DESKTOP_BREAKPOINT = 1200

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
        
        # Inicializar valores por defecto
        self.is_mobile = False
        self.is_tablet = False
        self.is_large_desktop = True  # Default para pantalla completa
        
        # Determinar el tipo de dispositivo basado en el ancho de la pantalla
        # Se actualizará en el método build() cuando la página esté completamente cargada
        self.nav_control = None
        self.logo_path = os.path.join("assets", "icon.png")
        
    def determine_device_type(self):
        """Determina el tipo de dispositivo basado en el ancho de la pantalla"""
        if not hasattr(self.page, 'width') or self.page.width is None:
            # Si no podemos obtener el ancho, asumimos pantalla completa/desktop
            logging.info("No se pudo determinar el ancho de la pantalla, asumiendo pantalla completa")
            self.is_mobile = False
            self.is_tablet = False
            self.is_large_desktop = True
            return
            
        width = self.page.width
        logging.info(f"Ancho de pantalla detectado: {width}px")
        
        self.is_mobile = width < MOBILE_BREAKPOINT
        self.is_tablet = MOBILE_BREAKPOINT <= width < TABLET_BREAKPOINT
        self.is_large_desktop = width >= LARGE_DESKTOP_BREAKPOINT
        
        logging.info(f"Tipo de dispositivo: mobile={self.is_mobile}, tablet={self.is_tablet}, large_desktop={self.is_large_desktop}")

    def build(self):
        try:
            # Determinar el tipo de dispositivo
            self.determine_device_type()
            
            # Obtener altura disponible para pantalla completa
            available_height = self.page.window.height if hasattr(self.page, 'window') and hasattr(self.page.window, 'height') else self.page.height
            if not available_height or available_height <= 0:
                available_height = 800  # Valor por defecto si no podemos determinar la altura
                
            logging.info(f"Altura disponible: {available_height}px")
            
            # Crear los destinos de navegación
            nav_items = [
                ft.NavigationDestination(
                    icon=icon,
                    selected_icon=selected_icon,
                    label=label,
                ) for icon, selected_icon, label in self.destinations
            ]

            # Botón de cierre de sesión
            logout_button = ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
                tooltip="Cerrar Sesión",
                on_click=self.handle_logout,
            )

            # Contenedor del logo
            logo_container = ft.Container(
                content=ft.Row([
                    ft.Image(
                        src=self.logo_path,
                        width=28,
                        height=28,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text("Pallet", 
                            size=20, 
                            weight=ft.FontWeight.BOLD, 
                            color=ft.colors.PRIMARY,
                            opacity=1 if self.is_large_desktop or self.is_mobile else 0)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                margin=ft.margin.only(top=20, bottom=20),
                padding=ft.padding.all(8)
            )

            # Manejar eventos de redimensionamiento
            self.page.on_resize = self.handle_resize

            # Configurar la navegación según el tipo de dispositivo
            if self.is_mobile:
                # Dispositivo móvil: barra de navegación inferior
                self.nav_control = ft.NavigationBar(
                    destinations=nav_items,
                    selected_index=self.selected_index,
                    on_change=self.handle_navigation,
                    bgcolor=ft.colors.SURFACE,
                    elevation=8,
                    height=65,  # Altura fija para la barra de navegación móvil
                    label_behavior=ft.NavigationBarLabelBehavior.ONLY_SHOW_SELECTED,
                    # Asegurar que ocupe todo el ancho disponible
                    width=self.page.width if self.page.width else 400,
                )
                
                # AppBar con logo y botón de cierre de sesión
                self.page.appbar = ft.AppBar(
                    leading=ft.Image(
                        src=self.logo_path,
                        width=24,
                        height=24,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    title=ft.Text("Pallet"),
                    center_title=False,
                    bgcolor=ft.colors.SURFACE,
                    actions=[logout_button],
                    elevation=2,
                    # Asegurar que ocupe todo el ancho disponible
                    toolbar_height=56,
                )
            elif self.is_tablet:
                # Tablet: navegación lateral compacta
                rail_destinations = [
                    ft.NavigationRailDestination(
                        icon=icon,
                        selected_icon=selected_icon,
                        label=label,
                        padding=6,
                    ) for icon, selected_icon, label in self.destinations
                ]
                
                self.nav_control = ft.Container(
                    content=ft.Column([
                        # Logo compacto en tablets
                        ft.Container(
                            content=ft.Image(
                                src=self.logo_path,
                                width=32,
                                height=32,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            margin=ft.margin.only(top=20, bottom=20),
                            alignment=ft.alignment.center,
                        ),
                        # Rail de navegación expandido verticalmente
                        ft.Container(
                            content=ft.NavigationRail(
                                selected_index=self.selected_index,
                                label_type=ft.NavigationRailLabelType.SELECTED,  # Solo mostrar etiqueta seleccionada
                                min_width=60,
                                min_extended_width=160,
                                extended=False,  # No extendido en tablets
                                destinations=rail_destinations,
                                on_change=self.handle_navigation,
                                bgcolor=ft.colors.SURFACE,
                            ),
                            expand=True,
                        ),
                        # Botón de logout en la parte inferior
                        ft.Container(
                            content=logout_button, 
                            margin=ft.margin.only(bottom=15),
                            alignment=ft.alignment.center,
                        )
                    ], 
                    spacing=0,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START),
                    width=65,  # Ancho fijo optimizado para tablets
                    height=available_height,  # Usar la altura disponible
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.OUTLINE)),
                    bgcolor=ft.colors.SURFACE,
                )
            else:
                # Desktop: navegación lateral completa
                rail_destinations = [
                    ft.NavigationRailDestination(
                        icon=icon,
                        selected_icon=selected_icon,
                        label=label,
                        padding=8
                    ) for icon, selected_icon, label in self.destinations
                ]
                
                # Determinar si el rail debe estar extendido
                is_extended = self.is_large_desktop
                
                self.nav_control = ft.Container(
                    content=ft.Column([
                        logo_container,  # Logo completo
                        ft.Container(
                            content=ft.NavigationRail(
                                selected_index=self.selected_index,
                                label_type=ft.NavigationRailLabelType.ALL,  # Mostrar todas las etiquetas
                                min_width=70,
                                min_extended_width=200,
                                extended=is_extended,  # Extendido en desktop grande
                                destinations=rail_destinations,
                                on_change=self.handle_navigation,
                                bgcolor=ft.colors.SURFACE,
                            ),
                            expand=True,
                        ),
                        # Botón de logout con margen
                        ft.Container(
                            content=logout_button, 
                            margin=ft.margin.only(bottom=20),
                            alignment=ft.alignment.center,
                        )
                    ], 
                    spacing=0,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START),
                    width=200 if is_extended else 80,  # Ancho adaptable
                    height=available_height,  # Usar la altura disponible
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.OUTLINE)),
                    bgcolor=ft.colors.SURFACE,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.with_opacity(0.15, ft.colors.SHADOW),
                        offset=ft.Offset(2, 0),
                    ) if is_extended else None,
                )

            return self.nav_control

        except Exception as e:
            logging.error(f"Error construyendo NavigationRail: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
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
            # Guardar el estado actual
            old_is_mobile = self.is_mobile
            old_is_tablet = self.is_tablet
            old_is_large_desktop = getattr(self, 'is_large_desktop', False)
            
            # Obtener altura disponible para pantalla completa
            available_height = self.page.window.height if hasattr(self.page, 'window') and hasattr(self.page.window, 'height') else self.page.height
            if not available_height or available_height <= 0:
                available_height = 800  # Valor por defecto si no podemos determinar la altura
                
            # Determinar nuevo estado
            self.determine_device_type()
            
            # Registrar cambio de tamaño para depuración
            logging.info(f"NavigationRail resize: pantalla {self.page.width}x{available_height}px, " + 
                         f"mobile={self.is_mobile}, tablet={self.is_tablet}, large_desktop={self.is_large_desktop}")
            
            # Actualizar ancho de la barra de navegación móvil si ya existe
            if self.is_mobile and isinstance(self.nav_control, ft.NavigationBar):
                self.nav_control.width = self.page.width if self.page.width else 400
                self.update()
                
            # Actualizar altura del contenedor para tablets y desktop
            elif not self.is_mobile and isinstance(self.nav_control, ft.Container):
                self.nav_control.height = available_height
                
            # Reconstruir completamente si cambia el tipo de dispositivo
            if (old_is_mobile != self.is_mobile or 
                old_is_tablet != self.is_tablet):
                logging.info(f"Cambio de tipo de dispositivo: mobile={self.is_mobile}, tablet={self.is_tablet}")
                self.nav_control = self.build()
                self.update()
                return
                
            # Para desktop, solo ajustar propiedades si cambia entre desktop normal y grande
            if not self.is_mobile and not self.is_tablet:
                is_large_desktop = self.is_large_desktop
                
                # Solo actualizar si cambió entre escritorio normal y grande
                if old_is_large_desktop != is_large_desktop and isinstance(self.nav_control, ft.Container):
                    logging.info(f"Ajustando tamaño de navegación: large_desktop={is_large_desktop}")
                    
                    # Ajustar ancho
                    self.nav_control.width = 200 if is_large_desktop else 80
                    self.nav_control.height = available_height
                    
                    # Ajustar visibilidad del texto del logo
                    if self.nav_control.content and self.nav_control.content.controls:
                        logo_container = self.nav_control.content.controls[0]
                        if isinstance(logo_container, ft.Container) and logo_container.content:
                            if isinstance(logo_container.content, ft.Row) and len(logo_container.content.controls) > 1:
                                logo_text = logo_container.content.controls[1]
                                if isinstance(logo_text, ft.Text):
                                    logo_text.opacity = 1 if is_large_desktop else 0
                    
                    # Ajustar rail
                    if (self.nav_control.content and len(self.nav_control.content.controls) > 1 and 
                        isinstance(self.nav_control.content.controls[1], ft.Container) and 
                        hasattr(self.nav_control.content.controls[1], 'content')):
                        
                        nav_rail = self.nav_control.content.controls[1].content
                        if hasattr(nav_rail, 'extended'):
                            nav_rail.extended = is_large_desktop
                            
                    # Aplicar/quitar sombra según tamaño
                    self.nav_control.shadow = ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.with_opacity(0.15, ft.colors.SHADOW),
                        offset=ft.Offset(2, 0),
                    ) if is_large_desktop else None
                    
                    self.update()
                    
        except Exception as e:
            logging.error(f"Error en handle_resize: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())