import flet as ft

def create_appbar(page: ft.Page, title: str):
    """Crea una barra de aplicación con título y botón de tema"""
    
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()
    
    return ft.AppBar(
        title=ft.Text(title),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.IconButton(
                icon=ft.icons.BRIGHTNESS_2_OUTLINED,
                tooltip="Cambiar tema",
                on_click=toggle_theme
            ),
            ft.IconButton(
                icon=ft.icons.PERSON,
                tooltip="Perfil",
                on_click=lambda _: page.go("/perfil")
            )
        ]
    )

def create_sidebar(page: ft.Page):
    """Crea una barra lateral con navegación"""
    return ft.NavigationRail(
        selected_index=2,  # Índice para inventario
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.DASHBOARD,
                selected_icon=ft.icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.POINT_OF_SALE,
                selected_icon=ft.icons.POINT_OF_SALE,
                label="Ventas",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.INVENTORY,
                selected_icon=ft.icons.INVENTORY,
                label="Inventario",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PEOPLE,
                selected_icon=ft.icons.PEOPLE,
                label="Clientes",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.BUSINESS,
                selected_icon=ft.icons.BUSINESS,
                label="Proveedores",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.BAR_CHART,
                selected_icon=ft.icons.BAR_CHART,
                label="Reportes",
            ),
        ],
        on_change=lambda e: handle_navigation(e, page),
    )

def handle_navigation(e, page: ft.Page):
    """Maneja la navegación entre secciones"""
    index = e.control.selected_index
    
    if index == 0:
        page.go("/")  # Dashboard
    elif index == 1:
        page.go("/ver_ventas")  # Ventas
    elif index == 2:
        page.go("/ver_inventario")  # Inventario
    elif index == 3:
        page.go("/ver_compradores")  # Clientes
    elif index == 4:
        page.go("/ver_proveedores")  # Proveedores
    elif index == 5:
        page.go("/ver_reportes")  # Reportes 