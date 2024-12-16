# filepath: /c:/Users/juanc/OneDrive/Escritorio/SoftwareJuanma/project/pages/PageSeeSale.py

import flet as ft
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class SeeSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_ventas", controls=[], padding=20)
        self.page = page
        self.session = session
        self.page.title = "Historial de Ventas"
        self.sale_service = SaleService(session)
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            0, self.handle_navigation)
        # Filtros de fecha
        self.date_from = ft.TextField(
            label="Desde",
            width=200,
            value=datetime.now().strftime("%Y-%m-%d"),
            keyboard_type=ft.KeyboardType.DATETIME
        )
        self.date_to = ft.TextField(
            label="Hasta",
            width=200,
            value=datetime.now().strftime("%Y-%m-%d"),
            keyboard_type=ft.KeyboardType.DATETIME
        )

        self.filter_button = ft.ElevatedButton(
            "Filtrar",
            on_click=self.load_sales
        )

        # Tabla de ventas
        self.sales_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Total")),
            ],
            rows=[]
        )

        # Layout de la vista
        self.controls = [
            ft.Row([
                self.navigation_rail,
                ft.Column([
                    ft.Text("Historial de Ventas", size=20,
                                weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.date_from,
                        self.date_to,
                        self.filter_button
                    ], spacing=10),
                    self.sales_table
                ], spacing=20)
            ])
        ]

        # Cargar las ventas inicialmente
        self.load_sales()

    def load_sales(self, e=None):
        try:
            from_date = datetime.strptime(self.date_from.value, "%Y-%m-%d")
            to_date = datetime.strptime(
                self.date_to.value, "%Y-%m-%d") + timedelta(days=1)
            sales = self.sale_service.get_sales_between_dates(
                from_date, to_date)
            self.sales_table.rows.clear()
            for sale in sales:
                self.sales_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(sale.id))),
                            ft.DataCell(
                                ft.Text(sale.date.strftime("%Y-%m-%d"))),
                            ft.DataCell(ft.Text(sale.customer_name)),
                            ft.DataCell(ft.Text(f"${sale.total:.2f}")),
                        ]
                    )
                )
            self.update()
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar las ventas: {str(e)}")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")
