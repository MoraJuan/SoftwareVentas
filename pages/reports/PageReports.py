import flet as ft
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index

class PageReports(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_reportes", controls=[], padding=0)
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.navigation_rail = create_navigation_rail(2, self.handle_navigation)
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(2, self.handle_navigation)

        report_cards = ft.ResponsiveRow([
            self.create_report_card(
                "Ventas",
                "Total de ventas por fecha, producto, cliente y vendedor",
                ft.icons.POINT_OF_SALE,
                "/ver_reportes/ventas"
            ),
            self.create_report_card(
                "Proveedores",
                "Listado de proveedores",
                ft.icons.LOCAL_SHIPPING,
                "/ver_proveedores"
            ),
            self.create_report_card(
                "Pagos",
                "Detalles de pagos recibidos",
                ft.icons.PAYMENTS,
                "/ver_reportes/pagos"
            ),
            self.create_report_card(
                "Inventario",
                "Estado del inventario y productos",
                ft.icons.INVENTORY,
                "/ver_productos"
            ),
            self.create_report_card(
                "Clientes",
                "Información de clientes y compras",
                ft.icons.PEOPLE,
                "/ver_compradores"
            ),
            self.create_report_card(
                "Exportar",
                "Exportar reportes a PDF o Excel",
                ft.icons.DOWNLOAD,
                "/ver_reportes/exportar"
            ),
        ])

        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Reportes", 
                                size=24, 
                                weight=ft.FontWeight.BOLD),
                            report_cards
                        ], spacing=20),
                        expand=True
                    )
                ]),
                expand=True
            )
        ]

    def create_report_card(self, title, description, icon, route):
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            padding=10,
            content=ft.GestureDetector(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(icon, size=40, color=ft.colors.BLUE),
                            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(description, 
                                size=14, 
                                color=ft.colors.GREY_700,
                                text_align=ft.TextAlign.CENTER),
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10),
                        padding=20,
                    )
                ),
                on_tap=lambda e: self.page.go(route)
            )
        )

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")