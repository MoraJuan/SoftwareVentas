import flet as ft
import logging
import pandas as pd
import os
from datetime import datetime, timedelta
from services.productService import ProductService
from services.inventoryHistoryService import InventoryHistoryService
from database.connection import get_db
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from ui.components.alerts import show_error_message, show_success_message

class InventoryHistoryPage(ft.View):
    def __init__(self, page: ft.Page, session=None):
        super().__init__(
            route="/historial_inventario",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.db = session or next(get_db())
        self.product_service = ProductService(self.db)
        self.inventory_history_service = InventoryHistoryService(self.db)
        
        # Variables de estado
        self.history_records = []
        self.filtered_records = []
        self.current_page = 1
        self.items_per_page = 15
        
        # Filtros
        self.date_range_dropdown = ft.Dropdown(
            label="Rango de fechas",
            options=[
                ft.dropdown.Option("today", "Hoy"),
                ft.dropdown.Option("week", "Última semana"),
                ft.dropdown.Option("month", "Último mes"),
                ft.dropdown.Option("all", "Todo")
            ],
            value="week",
            width=200
        )
        
        self.change_type_dropdown = ft.Dropdown(
            label="Tipo de cambio",
            options=[
                ft.dropdown.Option("all", "Todos"),
                ft.dropdown.Option("add", "Entradas"),
                ft.dropdown.Option("remove", "Salidas"),
                ft.dropdown.Option("set", "Ajustes directo")
            ],
            value="all",
            width=200
        )
        
        self.product_dropdown = ft.Dropdown(
            label="Producto",
            options=[
                ft.dropdown.Option("all", "Todos los productos")
            ],
            value="all",
            width=300
        )
        
        # Tablas
        self.history_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Stock Anterior")),
                ft.DataColumn(ft.Text("Nuevo Stock")),
                ft.DataColumn(ft.Text("Cambio")),
                ft.DataColumn(ft.Text("Razón"))
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            column_spacing=10
        )
        
        self.alerts_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Stock Actual")),
                ft.DataColumn(ft.Text("Stock Mínimo")),
                ft.DataColumn(ft.Text("Alerta"))
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            column_spacing=10
        )
        
        # Controles de paginación
        self.btn_first_page = ft.IconButton(
            icon=ft.icons.FIRST_PAGE,
            tooltip="Primera página",
            on_click=self.go_to_first_page,
            disabled=True,
            icon_color=ft.colors.PRIMARY
        )
        
        self.btn_prev_page = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            tooltip="Página anterior",
            on_click=self.go_to_prev_page,
            disabled=True,
            icon_color=ft.colors.PRIMARY
        )
        
        self.page_info_text = ft.Text(
            f"Página {self.current_page} de {self.get_total_pages()}",
            color=ft.colors.ON_SURFACE
        )
        
        self.btn_next_page = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            tooltip="Página siguiente",
            on_click=self.go_to_next_page,
            disabled=True,
            icon_color=ft.colors.PRIMARY
        )
        
        self.btn_last_page = ft.IconButton(
            icon=ft.icons.LAST_PAGE,
            tooltip="Última página",
            on_click=self.go_to_last_page,
            disabled=True,
            icon_color=ft.colors.PRIMARY
        )
        
        self.pagination_row = ft.Row(
            [
                self.btn_first_page,
                self.btn_prev_page,
                self.page_info_text,
                self.btn_next_page,
                self.btn_last_page,
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        self.total_records_text = ft.Text(
            f"Total: 0 registros",
            color=ft.colors.ON_SURFACE_VARIANT,
            size=12
        )
        
        self.build_ui()
    
    def build_ui(self):
        # Crear navegación
        self.navigation_rail = create_navigation_rail(2, self.page)  # 2 para Inventario

        # Crear botón de tema
        self.theme_button = ThemeIconButton(self.page)

        # Título principal con botón de tema
        header = ft.Container(
            content=ft.Row([
                ft.Text(
                    "Historial de Inventario", 
                    size=24, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                ft.Container(expand=True),
                self.theme_button
            ]),
            padding=ft.padding.only(right=20, bottom=20)
        )
        
        # Cargar datos iniciales
        self.load_products_dropdown()
        self.load_history_data()
        self.load_alerts_data()
        
        # Construir la interfaz
        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,
                    ft.VerticalDivider(width=1, color=ft.colors.OUTLINE_VARIANT),
                    ft.Container(
                        padding=20,
                        content=ft.Column([
                            header,
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Alertas de Inventario", size=20, weight=ft.FontWeight.BOLD),
                                    self.alerts_table
                                ]),
                                padding=10,
                                margin=10,
                                border_radius=10,
                                border=ft.border.all(1, ft.colors.OUTLINE)
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Historial de Cambios", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Row([
                                        self.date_range_dropdown,
                                        self.change_type_dropdown,
                                        self.product_dropdown,
                                    ], wrap=True),
                                    ft.Row([
                                        ft.FilledButton(
                                            text="Filtrar",
                                            icon=ft.icons.FILTER_ALT,
                                            on_click=self.filter_history
                                        ),
                                        ft.FilledTonalButton(
                                            text="Exportar a Excel",
                                            icon=ft.icons.DOWNLOAD,
                                            on_click=self.export_to_excel
                                        )
                                    ], spacing=10),
                                    self.history_table,
                                    # Paginación
                                    ft.Column([
                                        self.pagination_row,
                                        self.total_records_text
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                                ]),
                                padding=10,
                                margin=10,
                                border_radius=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                expand=True
                            )
                        ], expand=True, scroll=ft.ScrollMode.AUTO),
                        expand=True
                    )
                ]),
                expand=True
            )
        ]
    
    def load_products_dropdown(self):
        """Carga los productos en el dropdown"""
        try:
            products = self.product_service.get_all_products()
            
            # Agregar opciones al dropdown
            options = [ft.dropdown.Option("all", "Todos los productos")]
            for product in products:
                options.append(ft.dropdown.Option(str(product.id), product.name))
            
            self.product_dropdown.options = options
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al cargar productos en dropdown: {str(e)}")
    
    def load_history_data(self):
        """Carga los datos del historial"""
        try:
            # Cargar todos los registros de historial
            self.history_records = self.inventory_history_service.get_recent_history(500)  # Límite de 500 registros
            
            # Aplicar filtros
            self.filter_history()
            
        except Exception as e:
            logging.error(f"Error al cargar historial: {str(e)}")
            show_error_message(self.page, f"Error al cargar historial: {str(e)}")
    
    def filter_history(self, e=None):
        """Filtra los datos del historial según los filtros seleccionados"""
        try:
            # Determinar rango de fechas
            end_date = datetime.now()
            start_date = None
            
            if self.date_range_dropdown.value == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif self.date_range_dropdown.value == "week":
                start_date = end_date - timedelta(days=7)
            elif self.date_range_dropdown.value == "month":
                start_date = end_date - timedelta(days=30)
            
            # Aplicar filtros al historial
            if start_date and self.date_range_dropdown.value != "all":
                filtered_records = [r for r in self.history_records if r.date >= start_date and r.date <= end_date]
            else:
                filtered_records = self.history_records.copy()
            
            # Filtrar por tipo de cambio
            if self.change_type_dropdown.value != "all":
                filtered_records = [r for r in filtered_records if r.change_type == self.change_type_dropdown.value]
            
            # Filtrar por producto
            if self.product_dropdown.value != "all":
                product_id = int(self.product_dropdown.value)
                filtered_records = [r for r in filtered_records if r.product_id == product_id]
            
            self.filtered_records = filtered_records
            
            # Volver a la primera página
            self.current_page = 1
            
            # Actualizar tabla y controles de paginación
            self.update_history_table()
            self.update_pagination_controls()
            
        except Exception as e:
            logging.error(f"Error al filtrar historial: {str(e)}")
            show_error_message(self.page, f"Error al filtrar historial: {str(e)}")
    
    def update_history_table(self):
        """Actualiza la tabla con los registros de la página actual"""
        try:
            self.history_table.rows.clear()
            
            # Obtener registros de la página actual
            page_records = self.get_current_page_records()
            
            if not page_records:
                # Mostrar mensaje cuando no hay datos
                self.history_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("No hay registros de historial disponibles")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text(""))
                        ]
                    )
                )
            else:
                for record in page_records:
                    # Formatear tipo de cambio
                    change_type_text = "Desconocido"
                    change_type_color = ft.colors.ON_SURFACE
                    
                    if record.change_type == "add":
                        change_type_text = "Entrada"
                        change_type_color = ft.colors.GREEN
                    elif record.change_type == "remove":
                        change_type_text = "Salida"
                        change_type_color = ft.colors.ERROR
                    elif record.change_type == "set":
                        change_type_text = "Ajuste"
                        change_type_color = ft.colors.BLUE
                    
                    # Formatear cambio
                    change_text = f"+{record.change_amount}" if record.change_amount > 0 else str(record.change_amount)
                    change_color = ft.colors.GREEN if record.change_amount > 0 else ft.colors.ERROR if record.change_amount < 0 else ft.colors.ON_SURFACE
                    
                    product_name = record.product.name if record.product else f"Producto #{record.product_id}"
                    
                    self.history_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(record.date.strftime("%d/%m/%Y %H:%M"))),
                                ft.DataCell(ft.Text(product_name)),
                                ft.DataCell(ft.Text(change_type_text, color=change_type_color)),
                                ft.DataCell(ft.Text(str(record.previous_stock))),
                                ft.DataCell(ft.Text(str(record.new_stock))),
                                ft.DataCell(ft.Text(change_text, color=change_color)),
                                ft.DataCell(ft.Text(record.change_reason or "-"))
                            ]
                        )
                    )
            
            # Actualizar contador de registros
            self.total_records_text.value = f"Total: {len(self.filtered_records)} registros"
            
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al actualizar tabla de historial: {str(e)}")
            show_error_message(self.page, f"Error al actualizar tabla: {str(e)}")
    
    def load_alerts_data(self):
        """Carga los datos de alertas de inventario"""
        try:
            # Obtener productos con stock bajo
            low_stock_products = self.inventory_history_service.get_low_stock_products()
            
            # Actualizar tabla
            self.alerts_table.rows.clear()
            
            if not low_stock_products:
                self.alerts_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("No hay alertas de inventario")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text(""))
                        ]
                    )
                )
            else:
                for product in low_stock_products:
                    alert_text = "Stock Bajo" if product.stock > 0 else "Sin Stock"
                    alert_color = ft.colors.ORANGE if product.stock > 0 else ft.colors.ERROR
                    
                    category_name = product.category if product.category else "-"
                    if product.category and product.category.isdigit():
                        try:
                            from services.categoryService import CategoryService
                            category_service = CategoryService(self.db)
                            category = category_service.get_category_by_id(int(product.category))
                            if category:
                                category_name = category.name
                        except:
                            pass
                    
                    self.alerts_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(product.name)),
                                ft.DataCell(ft.Text(category_name)),
                                ft.DataCell(ft.Text(str(product.stock))),
                                ft.DataCell(ft.Text("5")),  # Valor fijo para stock mínimo
                                ft.DataCell(ft.Text(alert_text, color=alert_color))
                            ]
                        )
                    )
            
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al cargar alertas: {str(e)}")
            show_error_message(self.page, f"Error al cargar alertas: {str(e)}")
    
    def get_total_pages(self):
        """Calcula el número total de páginas"""
        if not self.filtered_records:
            return 1
        return max(1, (len(self.filtered_records) + self.items_per_page - 1) // self.items_per_page)
    
    def get_current_page_records(self):
        """Obtiene los registros de la página actual"""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return self.filtered_records[start_index:end_index]
    
    def update_pagination_controls(self):
        """Actualiza los controles de paginación"""
        total_pages = self.get_total_pages()
        
        self.page_info_text.value = f"Página {self.current_page} de {total_pages}"
        
        # Actualizar estado de los botones
        self.btn_first_page.disabled = self.current_page == 1
        self.btn_prev_page.disabled = self.current_page == 1
        self.btn_next_page.disabled = self.current_page == total_pages
        self.btn_last_page.disabled = self.current_page == total_pages
        
        self.page.update()
    
    def go_to_first_page(self, e):
        """Ir a la primera página"""
        self.current_page = 1
        self.update_history_table()
        self.update_pagination_controls()
    
    def go_to_prev_page(self, e):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_history_table()
            self.update_pagination_controls()
    
    def go_to_next_page(self, e):
        """Ir a la página siguiente"""
        if self.current_page < self.get_total_pages():
            self.current_page += 1
            self.update_history_table()
            self.update_pagination_controls()
    
    def go_to_last_page(self, e):
        """Ir a la última página"""
        self.current_page = self.get_total_pages()
        self.update_history_table()
        self.update_pagination_controls()
    
    def export_to_excel(self, e):
        """Exporta los datos del historial a un archivo Excel"""
        try:
            # Crear DataFrame para el historial
            data = []
            
            for record in self.filtered_records:
                product_name = record.product.name if record.product else f"Producto #{record.product_id}"
                
                # Formatear tipo de cambio
                change_type_text = "Desconocido"
                if record.change_type == "add":
                    change_type_text = "Entrada"
                elif record.change_type == "remove":
                    change_type_text = "Salida"
                elif record.change_type == "set":
                    change_type_text = "Ajuste"
                
                data.append({
                    "Fecha": record.date.strftime("%d/%m/%Y %H:%M"),
                    "Producto": product_name,
                    "Tipo de Cambio": change_type_text,
                    "Stock Anterior": record.previous_stock,
                    "Nuevo Stock": record.new_stock,
                    "Cambio": record.change_amount,
                    "Razón": record.change_reason or "-"
                })
            
            if not data:
                show_error_message(self.page, "No hay datos para exportar")
                return
            
            # Crear archivo Excel
            df = pd.DataFrame(data)
            filename = f"historial_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Datos exportados a {filename}")
            
            # Intentar abrir el archivo
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(filename)
                elif os.name == 'posix':  # macOS y Linux
                    import subprocess
                    subprocess.call(('xdg-open', filename))
            except:
                pass
                
        except Exception as e:
            logging.error(f"Error al exportar a Excel: {str(e)}")
            show_error_message(self.page, f"Error al exportar a Excel: {str(e)}")

def main(page: ft.Page):
    page.title = "Historial de Inventario"
    inventory_history_page = InventoryHistoryPage(page)
    page.add(inventory_history_page.build())

if __name__ == "__main__":
    ft.app(target=main) 