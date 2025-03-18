import flet as ft

def create_appbar(page: ft.Page, title: str):
    pass

def create_sidebar(page: ft.Page):
    pass

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