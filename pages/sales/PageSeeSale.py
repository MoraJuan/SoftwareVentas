import logging
import flet as ft
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index

class SeeSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_ventas", controls=[], padding=0)
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(5, self.handle_navigation)
        
        # Date filters
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

        # Sales table
        self.sales_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Método Pago")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Estado"))
            ],
            rows=[]
        )

        # Layout
        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Historial de Ventas", 
                                  size=20, 
                                  weight=ft.FontWeight.BOLD),
                            ft.Row([
                                self.date_from,
                                self.date_to,
                                self.filter_button
                            ], spacing=10),
                            self.sales_table
                        ], spacing=20),
                        expand=True
                    )
                ]),
                expand=True
            )
        ]
        
        # Load initial sales
        self.load_sales()

    def load_sales(self, e=None):
        try:
            from_date = datetime.strptime(self.date_from.value, "%Y-%m-%d")
            to_date = datetime.strptime(self.date_to.value, "%Y-%m-%d") + timedelta(days=1)
            
            sales = self.sale_service.get_sales_between_dates(from_date, to_date)
            
            self.sales_table.rows.clear()
            
            for sale in sales:
                self.sales_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(sale.id))),
                        ft.DataCell(ft.Text(sale.date.strftime("%Y-%m-%d %H:%M"))),
                        ft.DataCell(ft.Text(sale.customer.name if sale.customer else "N/A")),
                        ft.DataCell(ft.Text(sale.payment_method)),
                        ft.DataCell(ft.Text(f"${sale.total_amount:.2f}")),
                        ft.DataCell(ft.Text(sale.status))
                    ])
                )
            
            self.sales_table.update()
            
        except Exception as e:
            logging.error(f"Error loading sales: {str(e)}")
            show_error_message(self.page, f"Error al cargar las ventas: {str(e)}")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")