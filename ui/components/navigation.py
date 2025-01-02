import flet as ft

from ui.components.alerts import show_error_message


def create_navigation_rail(selected_index: int, on_change):
    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        extended=False,
        expand=False,
        height=500, 
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
                icon=ft.icons.INVENTORY,
                selected_icon=ft.icons.INVENTORY,
                label="Ver Productos"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PEOPLE,
                selected_icon=ft.icons.PEOPLE,
                label="Ver Compradores"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.LOCAL_SHIPPING,
                selected_icon=ft.icons.LOCAL_SHIPPING,
                label="Ver Proveedores"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.RECEIPT_LONG,
                selected_icon=ft.icons.RECEIPT_LONG,
                label="Ver Ventas"
            ),
            logout_button()
        ],
        on_change=on_change
    )


def logout_button():
    return ft.IconButton(
        icon=ft.icons.LOGOUT,
        tooltip="Cerrar sesión",
        on_click=handle_logout,
        # label="Cerrar sesión"
    )


def handle_logout(e):
    try:
        ft.Page.client_storage.remove("token")
        ft.Page.client_storage.remove("user_role")
        ft.Page.go("/login")
    except Exception as e:
        show_error_message(ft.Page, f"Logout error: {str(e)}")


def get_route_for_index(index: int) -> str:
    routes = {
        0: "/dashboard",
        1: "/realizar_venta",
        2: "/ver_productos",
        3: "/ver_compradores",
        4: "/ver_proveedores",
        5: "/ver_ventas"
    }
    return routes.get(index, "/dashboard")
