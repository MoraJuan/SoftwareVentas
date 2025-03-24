import flet as ft
import logging
import os

from ui.components.alerts import show_error_message

# Constantes para los breakpoints de responsive design
MOBILE_BREAKPOINT = 600
TABLET_BREAKPOINT = 1024
LARGE_DESKTOP_BREAKPOINT = 1200
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
        logging.info(f"NavigationRail - Ancho de pantalla detectado: {width}px")
        
        self.is_mobile = width < MOBILE_BREAKPOINT
        self.is_tablet = MOBILE_BREAKPOINT <= width < TABLET_BREAKPOINT
        self.is_large_desktop = width >= LARGE_DESKTOP_BREAKPOINT
        
        logging.info(f"NavigationRail - Tipo de dispositivo: mobile={self.is_mobile}, tablet={self.is_tablet}, large_desktop={self.is_large_desktop}")

    def build(self):
        try:
            # Determinar el tipo de dispositivo
            self.determine_device_type()
            
            # Obtener altura y ancho disponibles
            available_height = self.page.window.height if hasattr(self.page, 'window') and hasattr(self.page.window, 'height') else self.page.height
            available_width = self.page.window.width if hasattr(self.page, 'window') and hasattr(self.page.window, 'width') else self.page.width
            
            if not available_height or available_height <= 0:
                available_height = 800  # Valor por defecto si no podemos determinar la altura
            if not available_width or available_width <= 0:
                available_width = 1200  # Valor por defecto si no podemos determinar el ancho
                
            logging.info(f"NavigationRail - Dimensiones disponibles: {available_width}x{available_height}px")
            
            # Crear los destinos de navegación
            nav_items = [
                ft.NavigationDestination(
                    icon=icon,
                    selected_icon=selected_icon,
                    label=label,
                ) for icon, selected_icon, label in self.destinations
            ]

            # Botón de cambio de tema
            theme_toggle_button = ft.IconButton(
                icon=ft.icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
                tooltip="Cambiar Tema",
                on_click=self.handle_theme_toggle,
                icon_size=24,  # Tamaño explícito del icono
            )

            # Botón de cierre de sesión
            logout_button = ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
                tooltip="Cerrar Sesión",
                on_click=self.handle_logout,
                icon_size=24,  # Tamaño explícito del icono
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
                    width=available_width,
                )
                
                # AppBar con logo y botones de cierre de sesión y cambio de tema
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
                    actions=[
                        # Contenedor con padding para el botón de tema
                        ft.Container(
                            content=theme_toggle_button,
                            padding=ft.padding.all(8),
                            margin=ft.margin.only(right=16),
                            height=48,
                            width=48,
                        ),
                        # Contenedor con padding para el botón de logout
                        ft.Container(
                            content=logout_button,
                            padding=ft.padding.all(8),
                            margin=ft.margin.only(right=16),
                            height=48,
                            width=48,
                        ),
                    ],
                    elevation=2,
                    # Asegurar que ocupe todo el ancho disponible
                    toolbar_height=64,
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
                        # Botones de tema y logout en la parte inferior
                        ft.Container(
                            content=ft.Column([
                                # Contenedor con padding para el botón de tema
                                ft.Container(
                                    content=theme_toggle_button,
                                    padding=ft.padding.all(8),
                                    width=60,
                                    height=60,
                                    border_radius=ft.border_radius.all(30),
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                                ),
                                # Contenedor con padding para el botón de logout
                                ft.Container(
                                    content=logout_button,
                                    padding=ft.padding.all(8),
                                    width=60,
                                    height=60,
                                    border_radius=ft.border_radius.all(30),
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                                )
                            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                            margin=ft.margin.only(bottom=20, top=10),
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
                
                # Preparar los contenedores de botones con padding adecuado
                theme_btn_container = ft.Container(
                    content=theme_toggle_button,
                    padding=ft.padding.all(8),
                    width=60,
                    height=60,
                    border_radius=ft.border_radius.all(30),
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                )
                
                logout_btn_container = ft.Container(
                    content=logout_button,
                    padding=ft.padding.all(8),
                    width=60,
                    height=60,
                    border_radius=ft.border_radius.all(30),
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                )
                
                # Botones en fila o columna según el tamaño
                footer_content = ft.Row(
                    [theme_btn_container, logout_btn_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                ) if is_extended else ft.Column(
                    [theme_btn_container, logout_btn_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                )
                
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
                        # Botones de tema y logout con margen
                        ft.Container(
                            content=footer_content,
                            margin=ft.margin.only(bottom=25, top=15),
                            padding=ft.padding.all(10),
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

            # Asegurarse de que el manejador de resize esté configurado
            if not hasattr(self.page, '_original_on_resize'):
                self.page._original_on_resize = self.page.on_resize
            
            # Establecer nuestro manejador de redimensionamiento
            self.page.on_resize = self.handle_resize

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

    def handle_theme_toggle(self, e):
        try:
            # Verificar si la función toggle_theme existe en la página
            if hasattr(self.page, 'toggle_theme') and callable(self.page.toggle_theme):
                # Llamar a la función toggle_theme de la página
                self.page.toggle_theme()
                # Actualizar el icono del botón según el nuevo tema
                self.update()
            else:
                logging.error("La función toggle_theme no está disponible en la página")
                show_error_message(self.page, "No se pudo cambiar el tema. La función no está disponible.")
        except Exception as e:
            logging.error(f"Error al cambiar el tema: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al cambiar el tema: {str(e)}")

    def handle_resize(self, e):
        try:
            # Obtener dimensiones reales de la ventana
            available_width = self.page.window.width if hasattr(self.page, 'window') and hasattr(self.page.window, 'width') else self.page.width
            available_height = self.page.window.height if hasattr(self.page, 'window') and hasattr(self.page.window, 'height') else self.page.height
            
            # Usar valores por defecto si no se pueden determinar
            if not available_width or available_width <= 0:
                available_width = 1200
            if not available_height or available_height <= 0:
                available_height = 800
                
            # Guardar el estado actual de los tipos de dispositivo
            old_is_mobile = self.is_mobile
            old_is_tablet = self.is_tablet
            old_is_large_desktop = getattr(self, 'is_large_desktop', False)
            
            # Redeterminar el tipo de dispositivo
            self.determine_device_type()
            
            logging.info(f"NavigationRail resize: pantalla {available_width}x{available_height}px, " + 
                        f"mobile={self.is_mobile}, tablet={self.is_tablet}, large_desktop={self.is_large_desktop}")
            
            # Actualizar ancho de la barra de navegación móvil si ya existe
            if self.is_mobile and isinstance(self.nav_control, ft.NavigationBar):
                self.nav_control.width = available_width
                # Actualizar AppBar con los botones
                if hasattr(self.page, 'appbar') and self.page.appbar:
                    # Verificar si necesitamos actualizar los iconos
                    if len(self.page.appbar.actions) >= 2:
                        # Crear nuevo botón con los iconos actualizados
                        theme_icon = ft.icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE
                        
                        # Actualizar el primer botón (tema)
                        if isinstance(self.page.appbar.actions[0], ft.Container) and self.page.appbar.actions[0].content:
                            # Actualizar el icono del botón existente
                            new_theme_button = ft.IconButton(
                                icon=theme_icon,
                                icon_color=ft.colors.ON_SURFACE_VARIANT,
                                tooltip="Cambiar Tema",
                                on_click=self.handle_theme_toggle,
                                icon_size=24,
                            )
                            self.page.appbar.actions[0].content = new_theme_button
                        else:
                            # Crear un nuevo contenedor con el botón
                            self.page.appbar.actions[0] = ft.Container(
                                content=ft.IconButton(
                                    icon=theme_icon,
                                    icon_color=ft.colors.ON_SURFACE_VARIANT,
                                    tooltip="Cambiar Tema",
                                    on_click=self.handle_theme_toggle,
                                    icon_size=24,
                                ),
                                padding=ft.padding.all(4),
                                margin=ft.margin.only(right=8),
                            )
                self.update()
                
            # Reconstruir completamente si cambia el tipo de dispositivo
            if old_is_mobile != self.is_mobile or old_is_tablet != self.is_tablet:
                logging.info(f"NavigationRail: Cambio de tipo de dispositivo - mobile={self.is_mobile}, tablet={self.is_tablet}")
                # Reconstruir completamente el control
                nav_control = self.build()
                self.controls = [nav_control]
                self.update()
                return
                
            # Para dispositivos no móviles, ajustar el alto de la barra lateral
            if not self.is_mobile and isinstance(self.nav_control, ft.Container):
                self.nav_control.height = available_height
                
                # Para desktop, ajustar según el tamaño (grande o normal)
                if not self.is_tablet:
                    is_large_desktop = self.is_large_desktop
                    
                    # Solo actualizar si cambió entre escritorio normal y grande
                    if old_is_large_desktop != is_large_desktop:
                        logging.info(f"NavigationRail: Ajustando tamaño de navegación desktop - large_desktop={is_large_desktop}")
                        
                        # Ajustar ancho
                        self.nav_control.width = 200 if is_large_desktop else 80
                        
                        # Ajustar visibilidad del texto del logo
                        if self.nav_control.content and isinstance(self.nav_control.content, ft.Column) and len(self.nav_control.content.controls) > 0:
                            logo_container = self.nav_control.content.controls[0]
                            if isinstance(logo_container, ft.Container) and logo_container.content:
                                if isinstance(logo_container.content, ft.Row) and len(logo_container.content.controls) > 1:
                                    logo_text = logo_container.content.controls[1]
                                    if isinstance(logo_text, ft.Text):
                                        logo_text.opacity = 1 if is_large_desktop else 0
                        
                        # Ajustar rail
                        if (self.nav_control.content and isinstance(self.nav_control.content, ft.Column) and 
                            len(self.nav_control.content.controls) > 1 and 
                            isinstance(self.nav_control.content.controls[1], ft.Container) and 
                            self.nav_control.content.controls[1].content):
                            
                            nav_rail = self.nav_control.content.controls[1].content
                            if isinstance(nav_rail, ft.NavigationRail):
                                nav_rail.extended = is_large_desktop
                                
                        # Reconfigurar los botones de tema y logout
                        if self.nav_control.content and isinstance(self.nav_control.content, ft.Column) and len(self.nav_control.content.controls) > 2:
                            footer_container = self.nav_control.content.controls[2]
                            if isinstance(footer_container, ft.Container) and footer_container.content:
                                # Crear nuevos botones
                                theme_icon = ft.icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE
                                
                                theme_btn_container = ft.Container(
                                    content=ft.IconButton(
                                        icon=theme_icon,
                                        icon_color=ft.colors.ON_SURFACE_VARIANT,
                                        tooltip="Cambiar Tema",
                                        on_click=self.handle_theme_toggle,
                                        icon_size=24,
                                    ),
                                    padding=ft.padding.all(8),
                                    width=60,
                                    height=60,
                                    border_radius=ft.border_radius.all(30),
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                                )
                                
                                logout_btn_container = ft.Container(
                                    content=ft.IconButton(
                                        icon=ft.icons.LOGOUT,
                                        icon_color=ft.colors.ON_SURFACE_VARIANT,
                                        tooltip="Cerrar Sesión",
                                        on_click=self.handle_logout,
                                        icon_size=24,
                                    ),
                                    padding=ft.padding.all(8),
                                    width=60,
                                    height=60,
                                    border_radius=ft.border_radius.all(30),
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                                )
                                
                                if is_large_desktop:
                                    footer_container.content = ft.Row(
                                        [theme_btn_container, logout_btn_container],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=15
                                    )
                                else:
                                    footer_container.content = ft.Column(
                                        [theme_btn_container, logout_btn_container],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=15
                                    )
                        
                        # Aplicar/quitar sombra según tamaño
                        if is_large_desktop:
                            self.nav_control.shadow = ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=ft.colors.with_opacity(0.15, ft.colors.SHADOW),
                                offset=ft.Offset(2, 0),
                            )
                        else:
                            self.nav_control.shadow = None
                    
                self.update()
                
            # Llamar al manejador original si existe
            if hasattr(self.page, '_original_on_resize') and self.page._original_on_resize:
                self.page._original_on_resize(e)
                    
        except Exception as e:
            logging.error(f"Error en NavigationRail.handle_resize: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())