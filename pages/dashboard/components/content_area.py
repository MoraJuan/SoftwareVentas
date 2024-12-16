import flet as ft
from ..components.stats_section import create_stats_section
from ..components.charts_section import create_charts_section
from ..components.activity_section import create_activity_section

def create_content_area(session):
    return ft.Container(
        content=ft.Column([
            create_stats_section(session),
            create_charts_section(),
            create_activity_section()
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=20),
        expand=True,
        padding=20,
        bgcolor=ft.colors.WHITE
    )

