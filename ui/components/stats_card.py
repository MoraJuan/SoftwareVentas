import flet as ft

class StatsCard(ft.UserControl):
    def __init__(self, title: str, value: any, icon: str, color: str):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(self.icon, color=self.color),
                    ft.Text(self.title, size=16)
                ]),
                ft.Text(str(self.value), size=24, weight=ft.FontWeight.BOLD)
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            width=200
        )