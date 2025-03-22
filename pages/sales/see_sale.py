import flet as ft
import logging
import os
import pandas as pd
import subprocess
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from services.saleService import SaleService
from services.productService import ProductService
from ui.components.alerts import show_error_message, show_success_message

from io import StringIO
import csv


class ViewSalesView(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(
            route="/ver_reportes/ventas",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.product_service = ProductService(session)

        # Configuración de la tabla de ventas
        self.all_sales = []
        self.current_page = 1
        self.sales_per_page = 10
        self.sort_column = 0
        self.sort_reverse = False

        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            #self.navigation_rail = create_navigation_rail(3, self.page)  # Índice 3 para Reportes

            # Crear botón de tema
            #self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=ft.colors.ON_SURFACE,
                            tooltip="Volver a Reportes",
                            on_click=lambda _: self.page.go("/ver_reportes")
                        ),
                        ft.Text(
                            "Reporte de Ventas", 
                            size=24, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                    ]),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Exportar a CSV",
                        icon=ft.icons.DOWNLOAD,
                        on_click=self.export_to_csv,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREEN
                        )
                    ),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Filtros de búsqueda
            self.search_form = self.build_search_form()
            
            # Tabla de ventas
            self.sales_table = self.build_sales_table()
            
            # Cargar datos iniciales
            self.load_sales()
            
            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Filtros de Búsqueda", 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.search_form,
                        ft.Container(height=20),
                        ft.Text(
                            "Historial de Ventas", 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.sales_table,
                    ]),
                    padding=20
                )
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

    def build_search_form(self):
        # Crear campos de filtro
        self.date_from = ft.TextField(
            label="Desde",
            width=200,
            hint_text="YYYY-MM-DD",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )
        
        self.date_to = ft.TextField(
            label="Hasta",
            width=200,
            hint_text="YYYY-MM-DD",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )
        
        self.customer_name = ft.TextField(
            label="Cliente",
            width=200,
            hint_text="Nombre del cliente",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )
        
        # Botones de filtro
        search_button = ft.ElevatedButton(
            "Buscar",
            icon=ft.icons.SEARCH,
            on_click=self.filter_sales,
            style=ft.ButtonStyle(
                color=ft.colors.ON_PRIMARY,
                bgcolor=ft.colors.PRIMARY
            )
        )
        
        reset_button = ft.OutlinedButton(
            "Limpiar Filtros",
            icon=ft.icons.CLEAR,
            on_click=self.reset_filters
        )
        
        # Botón de exportar a CSV
        export_button = ft.ElevatedButton(
            "Exportar a CSV",
            icon=ft.icons.DOWNLOAD,
            on_click=self.export_to_csv,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.GREEN
            )
        )
        
        # Botones de período rápido
        today_button = ft.TextButton(
            "Hoy",
            on_click=lambda _: self.set_period("today")
        )
        
        week_button = ft.TextButton(
            "Esta Semana",
            on_click=lambda _: self.set_period("week")
        )
        
        month_button = ft.TextButton(
            "Este Mes",
            on_click=lambda _: self.set_period("month")
        )
        
        # Contenedor del formulario
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.date_from,
                    self.date_to,
                    self.customer_name
                ], wrap=True, spacing=10),
                ft.Row([
                    search_button,
                    reset_button,
                    export_button,
                    ft.Container(width=20),
                    ft.Text("Períodos rápidos:", color=ft.colors.ON_SURFACE),
                    today_button,
                    week_button,
                    month_button
                ], wrap=True, spacing=10)
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10
        )
    
    def build_sales_table(self):
        # Crear tabla de ventas
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Fecha", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Cliente", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Total", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Detalles", color=ft.colors.ON_SURFACE)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            sort_column_index=0,
            sort_ascending=False,
        )
    
    def load_sales(self):
        try:
            # Obtener ventas
            sales = self.sale_service.get_all_sales()
            
            # Crear filas para la tabla
            rows = []
            for sale in sales:
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(sale.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(sale.date.strftime("%Y-%m-%d %H:%M"), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(sale.customer_name or "Cliente no registrado", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${sale.total_amount:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Ver detalles",
                                    on_click=lambda _, s=sale: self.show_sale_details(s)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.sales_table.rows = rows
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar ventas: {str(e)}")
            show_error_message(self.page, f"Error al cargar ventas: {str(e)}")
    
    def filter_sales(self, e):
        try:
            # Obtener valores de filtro
            date_from = self.date_from.value
            date_to = self.date_to.value
            customer_name = self.customer_name.value
            
            # Filtrar ventas
            sales = self.sale_service.filter_sales(date_from, date_to, customer_name)
            
            # Crear filas para la tabla
            rows = []
            for sale in sales:
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(sale.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(sale.date.strftime("%Y-%m-%d %H:%M"), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(sale.customer_name or "Cliente no registrado", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${sale.total_amount:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Ver detalles",
                                    on_click=lambda _, s=sale: self.show_sale_details(s)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.sales_table.rows = rows
            
            # Mostrar mensaje si no hay resultados
            if not rows:
                show_error_message(self.page, "No se encontraron ventas con los filtros aplicados")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al filtrar ventas: {str(e)}")
            show_error_message(self.page, f"Error al filtrar ventas: {str(e)}")
    
    def reset_filters(self, e):
        try:
            # Limpiar campos
            self.date_from.value = ""
            self.date_to.value = ""
            self.customer_name.value = ""
            
            # Recargar todas las ventas
            self.load_sales()
            
            # Actualizar UI
            self.update()
            
        except Exception as e:
            logging.error(f"Error al resetear filtros: {str(e)}")
            show_error_message(self.page, f"Error al resetear filtros: {str(e)}")
    
    def set_period(self, period):
        try:
            today = datetime.now().date()
            
            if period == "today":
                # Hoy
                self.date_from.value = today.strftime("%Y-%m-%d")
                self.date_to.value = today.strftime("%Y-%m-%d")
            elif period == "week":
                # Esta semana (lunes a domingo)
                start_of_week = today - timedelta(days=today.weekday())
                self.date_from.value = start_of_week.strftime("%Y-%m-%d")
                self.date_to.value = today.strftime("%Y-%m-%d")
            elif period == "month":
                # Este mes
                start_of_month = today.replace(day=1)
                self.date_from.value = start_of_month.strftime("%Y-%m-%d")
                self.date_to.value = today.strftime("%Y-%m-%d")
            
            # Actualizar UI
            self.update()
            
        except Exception as e:
            logging.error(f"Error al establecer período: {str(e)}")
            show_error_message(self.page, f"Error al establecer período: {str(e)}")
    
    def show_sale_details(self, sale):
        try:
            # Obtener detalles de la venta
            sale_items = self.sale_service.get_sale_items(sale.id)
            
            # Crear filas para la tabla de detalles
            items_rows = []
            for item in sale_items:
                # Obtener producto
                product = self.product_service.get_product_by_id(item.product_id)
                product_name = product.name if product else "Producto no encontrado"
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(product_name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(str(item.quantity), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.subtotal:.2f}", color=ft.colors.ON_SURFACE)),
                    ]
                )
                items_rows.append(row)
            
            # Crear tabla de detalles
            details_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Cantidad", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Precio", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Subtotal", color=ft.colors.ON_SURFACE)),
                ],
                rows=items_rows,
                border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            )
            
            # Crear diálogo de detalles
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles de Venta #{sale.id}", color=ft.colors.ON_SURFACE),
                content=ft.Column([
                    ft.Text(f"Fecha: {sale.date.strftime('%Y-%m-%d %H:%M')}", color=ft.colors.ON_SURFACE),
                    ft.Text(f"Cliente: {sale.customer_name or 'Cliente no registrado'}", color=ft.colors.ON_SURFACE),
                    ft.Container(height=10),
                    ft.Text("Productos:", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    details_table,
                    ft.Container(height=10),
                    ft.Text(f"Total: ${sale.total_amount:.2f}", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ], scroll=ft.ScrollMode.AUTO, height=400),
                actions=[
                    ft.TextButton("Cerrar", on_click=self.close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.colors.SURFACE
            )
            
            # Mostrar diálogo
            self.page.dialog.open = True
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al mostrar detalles de venta: {str(e)}")
            show_error_message(self.page, f"Error al mostrar detalles de venta: {str(e)}")
    
    def close_dialog(self, e):
        try:
            # Cerrar diálogo
            self.page.dialog.open = False
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al cerrar diálogo: {str(e)}")
            show_error_message(self.page, f"Error al cerrar diálogo: {str(e)}")
    
    def export_to_csv(self, e):
        """Exportar la lista de ventas a un archivo CSV"""
        try:
            # Obtener ventas actuales (filtradas o todas)
            sales = []
            if self.date_from.value or self.date_to.value or self.customer_name.value:
                # Si hay filtros aplicados, usar las ventas filtradas
                sales = self.sale_service.filter_sales(
                    self.date_from.value, 
                    self.date_to.value, 
                    self.customer_name.value
                )
            else:
                # Si no hay filtros, usar todas las ventas
                sales = self.sale_service.get_all_sales()
            
            # Crear archivo CSV
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Fecha", "Cliente", "Total", "Método de Pago", "Estado"])
            
            for sale in sales:
                writer.writerow([
                    sale.id,
                    sale.date.strftime("%Y-%m-%d %H:%M"),
                    sale.customer_name or "Cliente no registrado",
                    f"{sale.total_amount:.2f}",
                    sale.payment_method if hasattr(sale, 'payment_method') else "N/A",
                    sale.status if hasattr(sale, 'status') else "N/A"
                ])
            
            csv_data = output.getvalue()
            # Codificar datos CSV para URL
            csv_url = f"data:text/csv;charset=utf-8,{csv_data}"
            self.page.launch_url(csv_url)
            show_success_message(self.page, "Ventas exportadas exitosamente.")
        except Exception as e:
            logging.error(f"Error al exportar ventas: {str(e)}")
            show_error_message(self.page, f"Error al exportar ventas: {str(e)}") 