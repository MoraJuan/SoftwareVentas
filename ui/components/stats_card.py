import flet as ft

class StatsCard(ft.UserControl):
    def __init__(self, title: str, value: any, icon: str, color: str):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color

    def build(self):
        # Formatear el valor si es un número
        formatted_value = self.value
        if isinstance(self.value, (int, float)):
            if self.title.lower().find("venta") >= 0:
                formatted_value = f"${self.value:.2f}"
            else:
                formatted_value = str(self.value)
        
        return ft.Container(
            content=ft.Row([
                # Icono en un círculo con el color de fondo
                ft.Container(
                    content=ft.Icon(
                        self.icon, 
                        color=ft.colors.WHITE,
                        size=20
                    ),
                    width=42,
                    height=42,
                    border_radius=21,
                    bgcolor=self.color,
                    alignment=ft.alignment.center
                ),
                # Columna con título y valor
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            formatted_value, 
                            size=20, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.GREY_900
                        ),
                        ft.Text(
                            self.title, 
                            size=13,
                            color=ft.colors.GREY_700
                        )
                    ], 
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START
                    ),
                    expand=True,
                    margin=ft.margin.only(left=12)
                )
            ]),
            padding=ft.padding.all(15),
            border_radius=8,
            width=220,
            height=80,
            bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK)
        )