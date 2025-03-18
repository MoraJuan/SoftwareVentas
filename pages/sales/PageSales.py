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
                
                # Crear fila con una referencia al ID de la venta en lugar del objeto completo
                sale_id = sale.id
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(sale_id), color=ft.colors.ON_SURFACE)),
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
                                    on_click=self.create_view_sale_callback(sale_id)
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
                
                # Crear fila con una referencia al ID del producto en lugar del objeto completo
                product_id = product.id
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(product_id), color=ft.colors.ON_SURFACE)),
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
                                    on_click=self.create_sell_product_callback(product_id)
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
    
    def create_view_sale_callback(self, sale_id):
        """Crea una función de callback para ver detalles de venta"""
        def handle_click(e):
            sale = self.sale_service.get_sale_by_id(sale_id)
            if sale:
                self.view_sale_details(sale)
            else:
                show_error_message(self.page, f"No se pudo encontrar la venta con ID {sale_id}")
        return handle_click
    
    def create_sell_product_callback(self, product_id):
        """Crea una función de callback para vender producto"""
        def handle_click(e):
            product = self.product_service.get_product_by_id(product_id)
            if product:
                self.sell_product(product)
            else:
                show_error_message(self.page, f"No se pudo encontrar el producto con ID {product_id}")
        return handle_click
        
    def view_sale_details(self, sale):
        """Muestra los detalles de una venta"""
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
                        ft.DataCell(ft.Text(f"${item.unit_price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.quantity * item.unit_price:.2f}", color=ft.colors.ON_SURFACE)),
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
                    ft.Text(f"Cliente: {sale.customer.name if sale.customer else 'Cliente no registrado'}", color=ft.colors.ON_SURFACE),
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
        """Cierra el diálogo actual"""
        try:
            self.page.dialog.open = False
            self.page.update()
        except Exception as e:
            logging.error(f"Error al cerrar diálogo: {str(e)}")
            show_error_message(self.page, f"Error al cerrar diálogo: {str(e)}")
        
    def sell_product(self, product):
        """Inicia una venta con el producto seleccionado"""
        try:
            # Guardar el ID del producto en el almacenamiento del cliente para usarlo en la página de venta
            self.page.client_storage.set("selected_product_id", product.id)
            # Navegar a la página de realizar venta
            self.page.go("/realizar_venta")
        except Exception as e:
            logging.error(f"Error al iniciar venta: {str(e)}")
            show_error_message(self.page, f"Error al iniciar venta: {str(e)}") 