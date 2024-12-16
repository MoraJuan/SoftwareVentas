import flet as ft
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message, show_success_message

class SeeSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        self.page = page
        self.session = session
        self.page.title = "Historial de Ventas"
        self.sale_service = SaleService(session)
        self.build_ui()

    def build_ui(self):
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
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # Resumen
        self.total_sales = ft.Text("Total de ventas: $0.00", size=20)

        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Historial de Ventas", 
                               size=20, 
                               weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.HOME,
                            tooltip="Volver al inicio",
                            on_click=lambda _: self.page.go("/")
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        self.date_from,
                        self.date_to,
                        self.filter_button
                    ]),
                    self.sales_table,
                    self.total_sales
                ]),
                padding=20
            )
        )
        self.load_sales()

    def load_sales(self, e=None):
        try:
            # Convertir fechas
            start_date = datetime.strptime(self.date_from.value, "%Y-%m-%d")
            end_date = datetime.strptime(self.date_to.value, "%Y-%m-%d") + timedelta(days=1)

            # Obtener ventas
            sales = self.sale_service.get_sales_by_date_range(start_date, end_date)
            total_amount = self.sale_service.get_total_sales_amount(start_date, end_date)

            # Actualizar tabla
            self.sales_table.rows.clear()
            for sale in sales:
                self.sales_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(sale.id))),
                            ft.DataCell(ft.Text(sale.date.strftime("%Y-%m-%d %H:%M"))),
                            ft.DataCell(ft.Text(sale.customer.name if sale.customer else "N/A")),
                            ft.DataCell(ft.Text(f"${sale.total_amount:.2f}")),
                            ft.DataCell(ft.Text(sale.status)),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        ft.icons.CANCEL,
                                        tooltip="Cancelar venta",
                                        on_click=lambda x, s=sale: self.cancel_sale(s.id)
                                    ) if sale.status == 'completed' else None
                                ])
                            ),
                        ]
                    )
                )

            # Actualizar total
            self.total_sales.value = f"Total de ventas: ${total_amount:.2f}"
            self.page.update()

        except ValueError:
            show_error_message(self.page, "Formato de fecha inválido")
        except Exception as e:
            show_error_message(self.page, f"Error al cargar las ventas: {str(e)}")

    def cancel_sale(self, sale_id: int):
        try:
            if self.sale_service.cancel_sale(sale_id):
                show_success_message(self.page, "Venta cancelada exitosamente")
                self.load_sales()
            else:
                show_error_message(self.page, "No se pudo cancelar la venta")
        except Exception as e:
            show_error_message(self.page, f"Error al cancelar la venta: {str(e)}")