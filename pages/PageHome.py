import flet as ft

class PageHome:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Gestión de Negocios"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.scroll = "adaptive"
        self.page.padding = 20
        self.build_ui()

    def build_ui(self):
        #! Crear botones del menú
        self.botones_menu = ft.Column(
            [
                ft.ElevatedButton("Realizar Venta", on_click=lambda e: self.page.go("/realizar_venta")),
                ft.ElevatedButton("Ver Productos", on_click=lambda e: self.page.go("/ver_productos")),
                ft.ElevatedButton("Ver Proveedores", on_click=lambda e: self.page.go("/ver_proveedores")),
                ft.ElevatedButton("Ver Compradores", on_click=lambda e: self.page.go("/ver_compradores")),
                ft.ElevatedButton("Ver Ventas", on_click=lambda e: self.page.go("/ver_ventas")),
            ],
            alignment="center",
            spacing=20,
        )

        #! Vista de la pestaña principal
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Column([ft.Text("Inicio")]),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self.botones_menu,
                                width=300,
                                alignment=ft.alignment.center,
                                padding=20,
                            ),
                        ],
                        alignment="center",
                    ),
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=40,
                ),
                alignment=ft.alignment.center,
            )
        )