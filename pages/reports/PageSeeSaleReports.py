import logging
import flet as ft
import datetime
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class SeeSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_reportes/ventas", controls=[], padding=0)
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)

        #!Calendario
        self.date_from = datetime.now().strftime('2024-01-01')
        self.date_to1 = datetime.now().strftime('%Y-%m-%d')

        #!Table Sales
        self.all_sales = 0
        self.current_page = 1
        self.sale_per_page = 10
        self.sort_column = False

        self.build_ui()

    def build_ui(self):
        try:
            self.navigation_rail = create_navigation_rail(
                2, self.handle_navigation)

            self.customer = None

            # Header con el botón "Volver a Reportes"
            self.header = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        icon_color=ft.colors.BLUE,
                        tooltip="Volver a Reportes",
                        on_click=lambda _: self.page.go("/ver_reportes")
                    ),
                    ft.Text(
                        "Reporte de Ventas",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                ],
                alignment=ft.MainAxisAlignment.START
            )

            # Tabla de ventas
            self.sales_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Fecha")),
                    ft.DataColumn(ft.Text("Cliente")),
                    ft.DataColumn(ft.Text("Productos")),
                    ft.DataColumn(ft.Text("Total")),
                    ft.DataColumn(ft.Text("Estado"))
                ],
                rows=[]
            )

            # Botones para seleccionar fechas
            self.boton_from = ft.ElevatedButton(
                self.date_from,
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: self.page.open(
                    ft.DatePicker(
                        first_date=datetime(year=2024, month=1, day=1),
                        last_date=datetime(
                            year=datetime.now().year, month=datetime.now().month, day=datetime.now().day),
                        on_change=self.handle_change_from,
                        on_dismiss=self.handle_dismissal,
                    )
                ),
            )

            self.boton_to = ft.ElevatedButton(
                self.date_to1,
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: self.page.open(
                    ft.DatePicker(
                        first_date=datetime(year=2024, month=1, day=1),
                        last_date=datetime(
                            year=datetime.now().year, month=datetime.now().month, day=datetime.now().day),
                        on_change=self.handle_change_to,
                        on_dismiss=self.handle_dismissal,
                    )
                ),
            )

            self.search_field = ft.TextField(
                label="Buscar cliente",
                width=300,
                prefix_icon=ft.icons.SEARCH,
                on_change=self.handle_customer
            )

            # Botón para filtrar ventas
            self.filter_button = ft.ElevatedButton(
                "Filtrar ventas",
                on_click=self.update_table
            )

            # Paginacion
            self.prev_button = ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                tooltip="Página anterior",
                on_click=self.prev_page
            )
            self.next_button = ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                tooltip="Página siguiente",
                on_click=self.next_page
            )
            self.page_info = ft.Text(f"Páginas: {self.current_page}")

            # Layout principal
            self.controls = [
                ft.Container(
                    content=ft.Row([
                        self.navigation_rail,
                        ft.Container(
                            padding=20,
                            content=ft.Column([
                                self.header,
                                ft.Row([
                                    self.boton_from,
                                    self.boton_to,
                                    self.search_field,
                                    self.filter_button
                                ], spacing=10),
                                self.sales_table,
                                ft.Row([
                                    self.prev_button,
                                    self.page_info,
                                    self.next_button
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ], spacing=20),
                            expand=True
                        )
                    ]),
                    expand=True
                )
            ]

            self.page.add(self)
            self.update_table()

        except Exception as e:
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()

    def next_page(self, e):
        total_pages = (len(self.all_sales) +
                       self.sale_per_page - 1) // self.sale_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_table()

        def sort_sales(self,e):
            column = e.column_index
            if self.sort_column == column:
              self.sort_reverse = not self.sort_reverse
            else:
                self.sort_column = column
                self.sort_reverse = False

# def sort_suppliers(self, e):
#         """Ordenar proveedores según la columna clicada"""
#         column = e.column_index
#         if self.sort_column == column:
#             self.sort_reverse = not self.sort_reverse
#         else:
#             self.sort_column = column
#             self.sort_reverse = False

#         if column == 0:  # ID
#             self.all_suppliers.sort(
#                 key=lambda s: s.id, reverse=self.sort_reverse)
#         elif column == 1:  # Nombre
#             self.all_suppliers.sort(
#                 key=lambda s: s.name.lower(), reverse=self.sort_reverse)
#         elif column == 2:  # Email
#             self.all_suppliers.sort(
#                 key=lambda s: s.email.lower(), reverse=self.sort_reverse)
#         elif column == 3:  # Teléfono
#             self.all_suppliers.sort(
#                 key=lambda s: s.phone, reverse=self.sort_reverse)
#         elif column == 4:  # Dirección
#             self.all_suppliers.sort(
#                 key=lambda s: s.address.lower(), reverse=self.sort_reverse)

    def update_table(self, e=None):
        # Obtengo la lista de ventas
        self.all_sales = self.filter_sales()

        # Obtengo los datos para la paginación
        start = (self.current_page - 1) * self.sale_per_page
        end = start + self.sale_per_page
        sales = self.all_sales[start:end]

        # Cargo la lista
        self.sales_table.rows.clear()
        for sale in sales:
            self.add_sale_to_table(sale)

        # Actualizo la página
        self.sales_table.update()
        self.page_info.value = f"Páginas: {self.current_page}"
        self.page_info.update()

    def filter_sales(self):
        try:
            # Convertir las fechas seleccionadas a objetos datetime
            from_date = datetime.strptime(self.date_from, "%Y-%m-%d")
            to_date = datetime.strptime(
                self.date_to1, "%Y-%m-%d") + timedelta(days=1)

            # Obtener ventas filtradas por rango de fechas
            sales = self.sale_service.get_sales_filtered(
                from_date, to_date, self.customer)

            return sales

        except Exception as e:
            show_error_message(self.page, f"Error al filtrar ventas: {str(e)}")
            return []

    def add_sale_to_table(self, sale):
        self.sales_table.rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(sale.id))),
                ft.DataCell(
                    ft.Text(sale.date.strftime("%Y-%m-%d %H:%M"))),
                ft.DataCell(
                    ft.Text(sale.customer.name if sale.customer else "N/A")),
                ft.DataCell(
                    ft.Text(", ".join([item.product.name for item in sale.items]))),
                ft.DataCell(ft.Text(f"${sale.total_amount:.2f}")),
                ft.DataCell(ft.Text(sale.status))
            ])
        )

    def handle_change_from(self, e):
        # Actualizar fecha "Desde" con el valor seleccionado
        self.date_from = e.control.value.strftime('%Y-%m-%d')
        self.boton_from.text = self.date_from  # Actualizar texto del botón
        self.page.update()

    def handle_change_to(self, e):
        # Actualizar fecha "Hasta" con el valor seleccionado
        self.date_to1 = e.control.value.strftime('%Y-%m-%d')
        self.boton_to.text = self.date_to1  # Actualizar texto del botón
        self.page.update()

    def handle_customer(self, e):
        self.customer = e.control.value

    def handle_dismissal(self, e):
        print("DatePicker dismissed")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")
