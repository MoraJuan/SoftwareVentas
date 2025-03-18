import flet as ft
from datetime import datetime, timedelta
from services.productService import ProductService
from services.inventoryHistoryService import InventoryHistoryService
from database.connection import get_db
from utils.ui_components import create_appbar, create_sidebar

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
            width=200,
            on_change=self.filter_history
        )
        
        self.change_type_dropdown = ft.Dropdown(
            label="Tipo de cambio",
            options=[
                ft.dropdown.Option("all", "Todos"),
                ft.dropdown.Option("entrada", "Entradas"),
                ft.dropdown.Option("salida", "Salidas"),
                ft.dropdown.Option("ajuste", "Ajustes"),
                ft.dropdown.Option("creación", "Creaciones")
            ],
            value="all",
            width=200,
            on_change=self.filter_history
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
            rows=[]
        )
        
        self.alerts_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Stock Actual")),
                ft.DataColumn(ft.Text("Stock Mínimo")),
                ft.DataColumn(ft.Text("Alerta"))
            ],
            rows=[]
        )
        
        self.build_ui()
    
    def build_ui(self):
        # Cargar datos iniciales
        self.load_history_data()
        self.load_alerts_data()
        
        # Construir la interfaz
        self.controls = [
            ft.Column([
                create_appbar(self.page, "Historial de Inventario"),
                ft.Row([
                    create_sidebar(self.page),
                    ft.Column([
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
                                    ft.FilledButton(
                                        text="Actualizar",
                                        on_click=lambda _: self.filter_history(None)
                                    )
                                ]),
                                self.history_table
                            ]),
                            padding=10,
                            margin=10,
                            border_radius=10,
                            border=ft.border.all(1, ft.colors.OUTLINE)
                        )
                    ], expand=True, scroll=ft.ScrollMode.AUTO)
                ], expand=True)
            ])
        ]
    
    def load_history_data(self):
        """Carga los datos del historial según los filtros seleccionados"""
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
            
            # Obtener historial
            history_records = []
            try:
                if start_date and self.date_range_dropdown.value != "all":
                    history_records = self.inventory_history_service.get_history_by_date_range(start_date, end_date)
                else:
                    history_records = self.inventory_history_service.get_recent_history(100)
                
                # Filtrar por tipo de cambio si es necesario
                if self.change_type_dropdown.value != "all":
                    history_records = [r for r in history_records if r.change_type == self.change_type_dropdown.value]
            except Exception as e:
                # Error al obtener historial
                history_records = []
            
            # Actualizar tabla
            self.history_table.rows.clear()
            
            if not history_records:
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
                for record in history_records:
                    product_name = record.product.name if record.product else f"Producto #{record.product_id}"
                    
                    self.history_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(record.date.strftime("%d/%m/%Y %H:%M"))),
                                ft.DataCell(ft.Text(product_name)),
                                ft.DataCell(ft.Text(record.change_type)),
                                ft.DataCell(ft.Text(str(record.previous_stock))),
                                ft.DataCell(ft.Text(str(record.new_stock))),
                                ft.DataCell(ft.Text(str(record.change_amount))),
                                ft.DataCell(ft.Text(record.change_reason or "-"))
                            ]
                        )
                    )
            
            self.page.update()
        except Exception as e:
            # Mostrar mensaje de error
            self.history_table.rows.clear()
            self.history_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"Error al cargar historial: {str(e)}")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text(""))
                    ]
                )
            )
            self.page.update()
    
    def load_alerts_data(self):
        """Carga los datos de alertas de inventario"""
        try:
            # Obtener alertas
            alerts = self.product_service.get_inventory_alerts()
            
            # Actualizar tabla
            self.alerts_table.rows.clear()
            
            # Productos con stock bajo
            if not alerts["low_stock"]:
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
                for product in alerts["low_stock"]:
                    self.alerts_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(product.name)),
                                ft.DataCell(ft.Text(product.category or "-")),
                                ft.DataCell(ft.Text(str(product.stock))),
                                ft.DataCell(ft.Text("5")),  # Valor fijo para stock mínimo
                                ft.DataCell(ft.Text("Stock Bajo", color=ft.colors.RED))
                            ]
                        )
                    )
            
            self.page.update()
        except Exception as e:
            # Mostrar mensaje de error
            self.alerts_table.rows.clear()
            self.alerts_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"Error al cargar alertas: {str(e)}")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text(""))
                    ]
                )
            )
            self.page.update()
    
    def filter_history(self, e):
        """Filtra el historial según los criterios seleccionados"""
        self.load_history_data()

def main(page: ft.Page):
    page.title = "Historial de Inventario"
    inventory_history_page = InventoryHistoryPage(page)
    page.add(inventory_history_page.build())

if __name__ == "__main__":
    ft.app(target=main) 