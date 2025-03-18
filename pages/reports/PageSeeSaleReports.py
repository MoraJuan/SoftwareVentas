import logging
import flet as ft
import datetime
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index
from io import StringIO
import csv
import pandas as pd
import os
import subprocess


class SeeSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_reportes/ventas", controls=[], padding=0)
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)

        #Calendar
        self.date_from = datetime.now().replace(day=1).strftime('%Y-%m-%d')  # Primer día del mes actual
        self.date_to1 = datetime.now().strftime('%Y-%m-%d')  # Día actual

        #Table Sales
        self.all_sales = []
        self.current_page = 1
        self.sale_per_page = 10
        self.sort_column = None
        self.sort_reverse = False
        self.total_pages = 1

        self.build_ui()

    def build_ui(self):
        try:
            self.navigation_rail = create_navigation_rail(
                3, self.handle_navigation)

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
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Exportar a Excel",
                        icon=ft.icons.DOWNLOAD,
                        on_click=self.export_to_excel,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREEN
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.START
            )

            # Tabla de ventas
            self.sales_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Fecha"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Cliente"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Productos"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Total"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Forma de pago"), on_sort=self.sort_sales),
                    ft.DataColumn(ft.Text("Estado"), on_sort=self.sort_sales)
                ],
                rows=[]
            )

            # Botones para seleccionar fechas
            self.boton_from = ft.ElevatedButton(
                self.date_from,
                icon=ft.icons.CALENDAR_MONTH,
                on_click=lambda e: self.page.open(
                    ft.DatePicker(
                        first_date=datetime(year=2024, month=1, day=1),
                        last_date=datetime.now(),
                        on_change=self.handle_change_from,
                        on_dismiss=self.handle_dismissal,
                    )
                ),
            )

            self.boton_to = ft.ElevatedButton(
                self.date_to1,
                icon=ft.icons.CALENDAR_MONTH,
                on_click=lambda e: self.page.open(
                    ft.DatePicker(
                        first_date=datetime(year=2024, month=1, day=1),
                        last_date=datetime.now(),
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
                icon=ft.icons.FILTER_ALT,
                on_click=self.get_sales
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
            self.page_info = ft.Text(f"Página {self.current_page} de {self.total_pages}")

            # Información de totales
            self.total_sales_info = ft.Text("Total: 0 ventas")
            self.total_amount_info = ft.Text("Monto total: $0.00")

            content = ft.Column([
                    self.header,
                    ft.Row([
                        ft.Column([
                            ft.Text("Desde:"),
                            self.boton_from,
                        ]),
                        ft.Column([
                            ft.Text("Hasta:"),
                            self.boton_to,
                        ]),
                        ft.Column([
                            ft.Text("Cliente:"),
                            self.search_field,
                        ]),
                        ft.Column([
                            ft.Text(" "),  # Espaciador
                            self.filter_button,
                        ]),
                    ], spacing=20, alignment=ft.MainAxisAlignment.START),
                    ft.Divider(height=20),
                    # Información de totales
                    ft.Row([
                        self.total_sales_info,
                        ft.Container(width=20),
                        self.total_amount_info,
                    ]),
                    self.sales_table,
                    ft.Row([
                        self.prev_button,
                        self.page_info,
                        self.next_button
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=20)

            # Layout principal
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

            self.page.add(self)
            self.get_sales()

        except Exception as e:
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()

    def next_page(self, e):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_table()

    def sort_sales(self, e):
        column = e.column_index
        
        # Si es la misma columna, invertir el orden
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Ordenar según la columna
        if column == 0:
            self.all_sales.sort(key=lambda s: s.id, reverse=self.sort_reverse)
        elif column == 1:
            self.all_sales.sort(key=lambda s: s.date, reverse=self.sort_reverse)
        elif column == 2:
            # Manejar caso de cliente None
            self.all_sales.sort(key=lambda s: s.customer.name if s.customer else "", reverse=self.sort_reverse)
        elif column == 3:
            # No hay un buen criterio para ordenar por productos, usamos ID
            self.all_sales.sort(key=lambda s: s.id, reverse=self.sort_reverse)
        elif column == 4:
            self.all_sales.sort(key=lambda s: s.total_amount, reverse=self.sort_reverse)
        elif column == 5:
            self.all_sales.sort(key=lambda s: s.payment_method, reverse=self.sort_reverse)
        elif column == 6:
            self.all_sales.sort(key=lambda s: s.status, reverse=self.sort_reverse)

        # Reiniciar a página 1 después de ordenar
        self.current_page = 1
        self.update_table()

    def get_sales(self, e=None):
        try:
            # Obtener las ventas filtradas
            self.all_sales = self.filter_sales()
            
            # Actualizar el conteo y monto total
            self.update_totals()
            
            # Calcular total de páginas
            self.total_pages = max(1, (len(self.all_sales) + self.sale_per_page - 1) // self.sale_per_page)
            
            # Asegurar que current_page sea válida
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            
            # Actualizar la tabla con las ventas paginadas
            self.update_table()
        except Exception as e:
            show_error_message(self.page, f"Error al obtener ventas: {str(e)}")

    def update_table(self):
        """Actualiza la tabla con las ventas de la página actual"""
        try:
            # Limpiar filas existentes
            self.sales_table.rows.clear()
            
            # Calcular índices para paginación
            start = (self.current_page - 1) * self.sale_per_page
            end = min(start + self.sale_per_page, len(self.all_sales))
            
            # Obtener ventas para la página actual
            current_sales = self.all_sales[start:end]
            
            # Añadir ventas a la tabla
            for sale in current_sales:
                self.add_sale_to_table(sale)
            
            # Actualizar información de paginación
            self.page_info.value = f"Página {self.current_page} de {self.total_pages}"
            
            # Actualizar botones de paginación
            self.prev_button.disabled = self.current_page <= 1
            self.next_button.disabled = self.current_page >= self.total_pages
            
            # Actualizar UI
            self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error al actualizar tabla: {str(e)}")

    def update_totals(self):
        """Actualiza la información de totales"""
        try:
            total_sales = len(self.all_sales)
            total_amount = sum(sale.total_amount for sale in self.all_sales)
            
            self.total_sales_info.value = f"Total: {total_sales} ventas"
            self.total_amount_info.value = f"Monto total: ${total_amount:.2f}"
            
            self.page.update()
        except Exception as e:
            logging.error(f"Error al actualizar totales: {str(e)}")

    def filter_sales(self):
        try:
            # Convertir las fechas seleccionadas a objetos datetime
            from_date = datetime.strptime(self.date_from, "%Y-%m-%d")
            # Añadir un día a la fecha final para incluir todo el día
            to_date = datetime.strptime(self.date_to1, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

            # Obtener ventas filtradas por rango de fechas y cliente
            customer_name = self.search_field.value if self.search_field.value else None
            sales = self.sale_service.get_sales_filtered(from_date, to_date, customer_name)

            return sales
        except Exception as e:
            show_error_message(self.page, f"Error al filtrar ventas: {str(e)}")
            return []

    def add_sale_to_table(self, sale):
        """Añade una venta a la tabla de ventas"""
        try:
            # Crear fila para la venta
            self.sales_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(sale.id))),
                        ft.DataCell(ft.Text(sale.date.strftime("%Y-%m-%d %H:%M"))),
                        ft.DataCell(ft.Text(sale.customer.name if sale.customer else "Cliente no registrado")),
                        ft.DataCell(ft.Text(", ".join([item.product.name if item.product else "Producto eliminado" for item in sale.items]))),
                        ft.DataCell(ft.Text(f"${sale.total_amount:.2f}")),
                        ft.DataCell(ft.Text(f"{sale.payment_method}")),
                        ft.DataCell(ft.Text(sale.status))
                    ],
                    on_select=lambda e, sale_id=sale.id: self.view_sale_details(sale_id)
                )
            )
        except Exception as e:
            logging.error(f"Error al añadir venta a la tabla: {str(e)}")

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
        pass

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
            self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")

    def view_sale_details(self, sale_id):
        """Muestra los detalles de una venta"""
        try:
            # Obtener venta por ID
            sale = self.sale_service.get_sale_by_id(sale_id)
            if not sale:
                show_error_message(self.page, f"Venta con ID {sale_id} no encontrada")
                return
                
            # Crear contenido del diálogo
            items_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto")),
                    ft.DataColumn(ft.Text("Cantidad")),
                    ft.DataColumn(ft.Text("Precio Unitario")),
                    ft.DataColumn(ft.Text("Subtotal"))
                ],
                rows=[]
            )
            
            # Añadir detalles de items
            for item in sale.items:
                items_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item.product.name if item.product else "Producto eliminado")),
                        ft.DataCell(ft.Text(str(item.quantity))),
                        ft.DataCell(ft.Text(f"${item.unit_price:.2f}")),
                        ft.DataCell(ft.Text(f"${item.subtotal:.2f}"))
                    ])
                )
                
            # Mostrar diálogo
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles de Venta #{sale.id}"),
                content=ft.Column([
                    ft.Text(f"Fecha: {sale.date.strftime('%Y-%m-%d %H:%M')}"),
                    ft.Text(f"Cliente: {sale.customer.name if sale.customer else 'Cliente no registrado'}"),
                    ft.Text(f"Estado: {sale.status}"),
                    ft.Text(f"Método de pago: {sale.payment_method}"),
                    ft.Divider(),
                    ft.Text("Productos:", weight=ft.FontWeight.BOLD),
                    items_table,
                    ft.Divider(),
                    ft.Text(f"Total: ${sale.total_amount:.2f}", weight=ft.FontWeight.BOLD)
                ], scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.TextButton("Cerrar", on_click=self.close_dialog)
                ]
            )
            self.page.dialog.open = True
            self.page.update()
                
        except Exception as e:
            show_error_message(self.page, f"Error al mostrar detalles de venta: {str(e)}")

    def close_dialog(self, e):
        """Cierra el diálogo actual"""
        self.page.dialog.open = False
        self.page.update()

    def export_to_excel(self, e):
        """Exportar la lista de ventas a un archivo Excel"""
        try:
            # Obtener ventas filtradas
            sales = self.filter_sales()
            
            # Crear DataFrame con pandas
            data = []
            for sale in sales:
                data.append({
                    "ID": sale.id,
                    "Fecha": sale.date.strftime("%Y-%m-%d %H:%M"),
                    "Cliente": sale.customer.name if sale.customer else "Cliente no registrado",
                    "Productos": ", ".join([item.product.name for item in sale.items]),
                    "Total": f"{sale.total_amount:.2f}",
                    "Método de Pago": sale.payment_method,
                    "Estado": sale.status
                })
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Crear archivo Excel temporal
            temp_file = "temp_ventas.xlsx"
            df.to_excel(temp_file, index=False)
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Ventas exportadas exitosamente a {temp_file}")
            
            # Abrir el archivo con la aplicación predeterminada
            if os.name == 'nt':  # Windows
                os.startfile(temp_file)
            elif os.name == 'posix':  # macOS y Linux
                subprocess.call(('xdg-open', temp_file))
                
        except Exception as e:
            logging.error(f"Error al exportar ventas: {str(e)}")
            show_error_message(self.page, f"Error al exportar ventas: {str(e)}")
