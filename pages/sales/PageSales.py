import flet as ft
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from services.saleService import SaleService
from services.productService import ProductService
from datetime import datetime, timedelta
import logging

class PageSales(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/ver_ventas",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.product_service = ProductService(session)
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(1, self.page)

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Gestión de Ventas", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Crear tabla de ventas
            self.sales_table = self.build_sales_table()
            
            # Crear tabla de productos
            self.products_table = self.build_products_table()
            
            # Cargar datos iniciales
            self.load_recent_sales()
            self.load_products()

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton(
                                "Nueva Venta",
                                icon=ft.icons.ADD_SHOPPING_CART,
                                on_click=lambda _: self.page.go("/realizar_venta"),
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_PRIMARY,
                                    bgcolor=ft.colors.PRIMARY
                                )
                            ),
                            ft.ElevatedButton(
                                "Actualizar Datos",
                                icon=ft.icons.REFRESH,
                                on_click=self.refresh_data,
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_SURFACE,
                                    bgcolor=ft.colors.SURFACE_VARIANT
                                )
                            )
                        ], spacing=10),
                        ft.Container(height=20),
                        ft.Text(
                            "Ventas Recientes",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.sales_table,
                        ft.Container(height=30),
                        ft.Text(
                            "Productos Disponibles",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.products_table
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

    def build_sales_table(self):
        try:
            # Crear tabla de ventas
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Fecha", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Cliente", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Total", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Estado", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Acciones", color=ft.colors.ON_SURFACE)),
                ],
                rows=[],
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                sort_column_index=0,
                sort_ascending=False,
            )
        except Exception as e:
            logging.error(f"Error construyendo tabla de ventas: {str(e)}")
            return ft.Text("Error al cargar la tabla de ventas", color=ft.colors.ERROR)
            
    def build_products_table(self):
        try:
            # Crear tabla de productos
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Nombre", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Categoría", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Precio", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Stock", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Acciones", color=ft.colors.ON_SURFACE)),
                ],
                rows=[],
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            )
        except Exception as e:
            logging.error(f"Error construyendo tabla de productos: {str(e)}")
            return ft.Text("Error al cargar la tabla de productos", color=ft.colors.ERROR)
            
    def load_recent_sales(self):
        try:
            # Obtener ventas de los últimos 30 días
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Obtener ventas recientes
            sales = self.sale_service.get_sales_between_dates(start_date, end_date)
            
            # Crear filas para la tabla
            rows = []
            for sale in sales:
                # Formatear fecha
                date_str = sale.date.strftime("%d/%m/%Y %H:%M") if sale.date else "N/A"
                
                # Obtener nombre del cliente
                customer_name = sale.customer.name if sale.customer else "Desconocido"
                
                # Formatear estado
                status_color = ft.colors.GREEN if sale.status == 'completed' else ft.colors.ERROR
                status_text = "Completada" if sale.status == 'completed' else "Cancelada"
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(sale.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(date_str, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(customer_name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${sale.total_amount:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(status_text, color=status_color)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Ver detalles",
                                    on_click=lambda _, s=sale: self.view_sale_details(s)
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
                show_error_message(self.page, "No se encontraron ventas recientes")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar ventas recientes: {str(e)}")
            show_error_message(self.page, f"Error al cargar ventas recientes: {str(e)}")
            
    def load_products(self):
        try:
            # Obtener todos los productos
            products = self.product_service.get_all_products()
            
            # Crear filas para la tabla
            rows = []
            for product in products:
                # Verificar si hay stock
                stock_color = ft.colors.ERROR if product.stock <= 0 else ft.colors.ON_SURFACE
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(product.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(product.name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(product.category or "Sin categoría", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${product.price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(str(product.stock), color=stock_color)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.ADD_SHOPPING_CART,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Vender",
                                    disabled=product.stock <= 0,
                                    on_click=lambda _, p=product: self.sell_product(p)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.products_table.rows = rows
            
            # Mostrar mensaje si no hay resultados
            if not rows:
                show_error_message(self.page, "No se encontraron productos")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar productos: {str(e)}")
            show_error_message(self.page, f"Error al cargar productos: {str(e)}")
            
    def refresh_data(self, e=None):
        """Actualiza los datos de las tablas"""
        self.load_recent_sales()
        self.load_products()
        show_success_message(self.page, "Datos actualizados correctamente")
        
    def view_sale_details(self, sale):
        """Muestra los detalles de una venta"""
        # Aquí podrías implementar la lógica para mostrar los detalles de la venta
        # Por ejemplo, abrir un diálogo o navegar a una página de detalles
        show_success_message(self.page, f"Ver detalles de la venta {sale.id}")
        
    def sell_product(self, product):
        """Inicia una venta con el producto seleccionado"""
        # Navegar a la página de realizar venta
        self.page.go("/realizar_venta") 