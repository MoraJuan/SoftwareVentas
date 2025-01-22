import flet as ft

from ui.components.alerts import show_error_message


def create_navigation_rail(selected_index: int, on_change):
    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=72,
        min_extended_width=200,
        extended=True,
        group_alignment=-1.0,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.DASHBOARD,
                selected_icon=ft.icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SHOPPING_CART,
                selected_icon=ft.icons.SHOPPING_CART,
                label="Realizar Venta"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.ASSESSMENT,
                selected_icon=ft.icons.ASSESSMENT,
                label="Reports"
            )
        ],
        on_change=on_change
    )

def get_route_for_index(index: int) -> str:
    routes = {
        0: "/dashboard",
        1: "/realizar_venta",
        2: "/ver_reportes"
    }
    return routes.get(index, "/dashboard")

def handle_navigation(e):
    try:
        route = get_route_for_index(e.control.selected_index)
        e.page.go(route)
    except Exception as e:
        show_error_message(e.page, f"Error de navegación: {str(e)}")