import flet as ft
import csv
from io import StringIO
from datetime import datetime
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class SeeSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_ventas", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Ventas"
        self.sale_service = SaleService(session)
        self.all_sales = []
        self.current_page = 1
        self.sales_per_page = 10
        self.sort_column = None
        self.sort_reverse = False
        self.build_ui()

    def build_ui(self):
        try:
           # Inicializar controles
            self.date_picker_from_label = datetime.now().strftime("%Y-%m-%d")
            self.date_picker_to_label = datetime.now().strftime("%Y-%m-%d")

            self.navigation_rail = create_navigation_rail(
                5, self.handle_navigation)

            # Filtros de búsqueda
            self.date_picker_from = ft.ElevatedButton(
                self.date_picker_from_label,
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=self.open_date_picker_from
            )

            self.date_picker_to = ft.ElevatedButton(
                self.date_picker_to_label,
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=self.open_date_picker_to
            )

            self.payment_method_field = ft.Dropdown(
                label="Forma de pago",
                options=[
                    ft.dropdown.Option("Efectivo"),
                    ft.dropdown.Option("Tarjeta de Crédito"),
                    ft.dropdown.Option("Tarjeta de Débito"),
                    ft.dropdown.Option("Transferencia"),
                ],
                on_change=self.filter_sales
            )
            self.buyer_field = ft.TextField(
                label="Buscar por comprador",
                width=300,
                prefix_icon=ft.icons.SEARCH,
                on_change=self.filter_sales
            )

            # Botón de exportar a CSV
            self.export_button = ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                tooltip="Exportar a CSV",
                on_click=self.export_to_csv
            )

            # Controles de paginación
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

            # Barra de progreso
            self.progress_bar = ft.ProgressBar(visible=False)

            # Tabla de ventas
            self.sales_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Fecha"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Cliente"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Forma de Pago"),
                                  on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Total"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Estado")),
                ],
                rows=[]
            )

            # Diseño del contenido
            content = ft.Column([
                ft.Text("Ventas", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.date_picker_from,
                    self.date_picker_to,
                    self.payment_method_field,
                    self.buyer_field,
                    self.export_button,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.progress_bar,
                ft.Divider(height=20),
                self.sales_table,
                ft.Row([
                    self.prev_button,
                    self.page_info,
                    self.next_button
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=20)

            # Configuración principal de controles sin scroll
            self.controls = [
                ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        content=content,
                        expand=True,
                        padding=20
                    )
                ], expand=True)
            ]

            # Cargar ventas al iniciar la página
            self.load_sales()

        except Exception as e:
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def open_date_picker_from(self, e):
        """Abrir el DatePicker para 'Desde'"""
        date_picker = ft.DatePicker(
            first_date=datetime(2023, 10, 1),
            last_date=datetime.now(),
            on_change=self.handle_date_picker_from_change
        )
        self.page.open(date_picker)

    def open_date_picker_to(self, e):
        """Abrir el DatePicker para 'Hasta'"""
        date_picker = ft.DatePicker(
            first_date=datetime(2023, 10, 1),
            last_date=datetime.now(),
            on_change=self.handle_date_picker_to_change
        )
        self.page.open(date_picker)

    def handle_date_picker_from_change(self, e):
        """Cuando el valor del DatePicker 'Desde' cambie"""
        selected_date = e.control.value
        self.date_picker_from_label = f"{
            selected_date.strftime('%Y-%m-%d')}"
        self.page.update()

    def handle_date_picker_to_change(self, e):
        """Cuando el valor del DatePicker 'Hasta' cambie"""
        selected_date = e.control.value
        self.date_picker_to_label = f"{
            selected_date.strftime('%Y-%m-%d')}"
        self.page.update()

    def handle_navigation(self, e):
        """Manejar eventos de navegación"""
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
            self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")

    def filter_sales(self, e):
        """Filtrar ventas según los criterios seleccionados"""
        try:
            filtered = [
                sale for sale in self.all_sales
                if (self.date_picker_from.value <= sale.date <= self.date_picker_to.value) and
                   (self.payment_method_field.value in sale.payment_method) and
                   (self.buyer_field.value.lower() in sale.buyer.lower())
            ]
            self.update_table(filtered)
            self.update()
        except Exception as e:
            show_error_message(self.page, f"Error al filtrar ventas: {str(e)}")

    def export_to_csv(self, e):
        """Exportar la lista de ventas a un archivo CSV"""
        try:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Fecha", "Cliente",
                            "Forma de Pago", "Total", "Estado"])
            for sale in self.all_sales:
                writer.writerow([sale.id, sale.date, sale.buyer,
                                sale.payment_method, sale.total, sale.status])
            csv_data = output.getvalue()
            # Codificar datos CSV para URL
            csv_url = f"data:text/csv;charset=utf-8,{csv_data}"
            self.page.launch_url(csv_url)
            show_success_message(self.page, "Ventas exportadas exitosamente.")
        except Exception as e:
            show_error_message(
                self.page, f"Error al exportar ventas: {str(e)}")

    def sort_sales(self, e):
        """Ordenar ventas según la columna clicada"""
        column = e.column_index
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        if column == 0:  # ID
            self.all_sales.sort(key=lambda s: s.id, reverse=self.sort_reverse)
        elif column == 1:  # Fecha
            self.all_sales.sort(key=lambda s: s.date,
                                reverse=self.sort_reverse)
        elif column == 2:  # Cliente
            self.all_sales.sort(key=lambda s: s.buyer.lower(),
                                reverse=self.sort_reverse)
        elif column == 3:  # Forma de Pago
            self.all_sales.sort(
                key=lambda s: s.payment_method.lower(), reverse=self.sort_reverse)

        self.update_table(self.get_paginated_sales())

    def prev_page(self, e):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()

    def next_page(self, e):
        """Ir a la página siguiente"""
        total_pages = (len(self.all_sales) +
                       self.sales_per_page - 1) // self.sales_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_pagination()

    def update_pagination(self):
        """Actualizar la tabla basada en la página actual"""
        paginated = self.get_paginated_sales()
        self.update_table(paginated)
        total_pages = (len(self.all_sales) +
                       self.sales_per_page - 1) // self.sales_per_page
        self.page_info.value = f"Páginas: {self.current_page} de {total_pages}"
        self.page_info.update()

    def get_paginated_sales(self):
        """Obtener ventas para la página actual"""
        start = (self.current_page - 1) * self.sales_per_page
        end = start + self.sales_per_page
        return self.all_sales[start:end]

    def update_table(self, sales):
        """Actualizar la tabla de ventas con la lista proporcionada"""
        self.sales_table.rows.clear()
        for sale in sales:
            self.add_sale_to_table(sale)
        self.sales_table.update()

    def add_sale_to_table(self, sale):
        """Método auxiliar para agregar una venta a la tabla"""
        self.sales_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(sale.id))),
                    ft.DataCell(ft.Text(sale.date.strftime("%Y-%m-%d"))),
                    ft.DataCell(ft.Text(sale.customer_id)),
                    ft.DataCell(ft.Text(sale.payment_method)),
                    ft.DataCell(ft.Text(str(sale.total_amount))),
                    ft.DataCell(ft.Text(sale.status)),
                ]
            )
        )

    def load_sales(self):
        """Cargar ventas con indicación de progreso"""
        try:
            # self.progress_bar.visible = True
            # self.update()
            self.all_sales = self.sale_service.get_all_sales()

            self.current_page = 1
            self.update_pagination()
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar las ventas: {str(e)}")
        finally:
            # self.progress_bar.visible = False
            self.update()

