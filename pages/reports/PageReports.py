import flet as ft
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
import logging

class PageReports(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/ver_reportes",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(3, self.page)  # Índice 3 para Reportes

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Reportes", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                self.build_reports_section()
            ], spacing=0, scroll=ft.ScrollMode.AUTO)

            # Contenedor principal
            self.controls = [
                ft.Container(
                    content=ft.Row([
                        self.navigation_rail,
                        ft.VerticalDivider(width=1, color=ft.colors.OUTLINE_VARIANT),
                        ft.Container(
                            padding=20,
                            content=main_content,
                            expand=True
                        )
                    ]),
                    expand=True
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI: {str(e)}")
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def build_reports_section(self):
        try:
            # Crear tarjetas de reportes
            return ft.ResponsiveRow([
                self.create_report_card(
                    "Ventas",
                    "Reportes detallados de ventas por período",
                    ft.icons.TRENDING_UP,
                    "/ver_reportes/ventas"
                ),
                self.create_report_card(
                    "Gastos",
                    "Gestión y reportes de gastos",
                    ft.icons.MONEY_OFF,
                    "/ver_reportes/gastos"
                ),
                self.create_report_card(
                    "Inventario",
                    "Estado y movimientos del inventario",
                    ft.icons.INVENTORY_2,
                    "/ver_reportes/inventario"
                ),
                self.create_report_card(
                    "Clientes",
                    "Análisis de clientes y compras",
                    ft.icons.PEOPLE,
                    "/ver_reportes/clientes"
                ),
            ])
            
        except Exception as e:
            logging.error(f"Error construyendo sección de reportes: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def create_report_card(self, title, description, icon, route):
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon, size=36, color=ft.colors.PRIMARY),
                            ft.Container(width=10),
                            ft.Column([
                                ft.Text(
                                    title,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.ON_SURFACE
                                ),
                                ft.Text(
                                    description,
                                    size=14,
                                    color=ft.colors.ON_SURFACE_VARIANT
                                ),
                            ], spacing=5, expand=True),
                        ]),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Ver Reporte",
                            icon=ft.icons.ARROW_FORWARD,
                            on_click=lambda _, r=route: self.page.go(r),
                            style=ft.ButtonStyle(
                                color=ft.colors.ON_PRIMARY,
                                bgcolor=ft.colors.PRIMARY
                            )
                        ),
                    ], spacing=10),
                    padding=15
                ),
                elevation=2
            ),
            col={"sm": 12, "md": 6, "lg": 3},
            padding=5
        )