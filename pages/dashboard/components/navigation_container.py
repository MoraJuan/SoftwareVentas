import flet as ft
from ..utils.navigation import create_navigation_rail

def create_navigation_container(page: ft.Page, on_navigation, on_logout):
    navigation_rail = create_navigation_rail(0, on_navigation)
    
    logout_button = ft.IconButton(
        icon=ft.icons.LOGOUT,
        tooltip="Cerrar sesión",
        on_click=on_logout
    )

    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=navigation_rail,
                expand=True
            ),
            logout_button
        ]),
        width=200,
        expand=True
    )