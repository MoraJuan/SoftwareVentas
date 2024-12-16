import flet as ft

def create_error_boundary(error, retry_callback):
    return ft.Container(
        content=ft.Column([
            ft.Text("Error loading dashboard content", 
                   size=20, 
                   color=ft.colors.RED),
            ft.Text(str(error), color=ft.colors.RED),
            ft.ElevatedButton("Retry", 
                            on_click=lambda _: retry_callback())
        ]),
        padding=20
    )