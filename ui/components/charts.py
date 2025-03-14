import flet as ft
from typing import List, Dict

class LineChart(ft.UserControl):
    def __init__(self, title: str, data: List[Dict]):
        super().__init__()
        self.title = title
        self.data = data

    def build(self):
        # Por ahora, mostraremos un placeholder
        return ft.Container(
            content=ft.Column([
                ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ft.Text("Gráfico de líneas aquí", color=ft.colors.ON_SURFACE_VARIANT)
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10
        )

class PieChart(ft.UserControl):
    def __init__(self, title: str, data: List[Dict]):
        super().__init__()
        self.title = title
        self.data = data

    def build(self):
        # Por ahora, mostraremos un placeholder
        return ft.Container(
            content=ft.Column([
                ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ft.Text("Gráfico circular aquí", color=ft.colors.ON_SURFACE_VARIANT)
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10
        )