import flet as ft
import logging
from datetime import datetime
from services.productService import ProductService
from services.saleService import SaleService
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from ui.components.alerts import show_error_message, show_success_message

class MakeSaleView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/realizar_venta",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.product_service = ProductService(session)
        self.sale_service = SaleService(session)
        self.cart = []
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(1, self.page)  # Índice 1 para Ventas

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=ft.colors.ON_SURFACE,
                            tooltip="Volver a Ventas",
                            on_click=lambda _: self.page.go("/ver_ventas")
                        ),
                        ft.Text(
                            "Realizar Venta", 
                            size=24, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                    ]),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Crear secciones de la interfaz
            self.search_section = self.build_search_section()
            self.products_section = self.build_products_section()
            self.cart_section = self.build_cart_section()
            self.customer_section = self.build_customer_section()
            self.payment_section = self.build_payment_section()

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Buscar Productos", 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.search_section,
                        self.products_section,
                        ft.Container(height=20),
                        ft.Text(
                            "Carrito de Compra", 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.cart_section,
                        ft.Container(height=20),
                        ft.Row([
                            self.customer_section,
                            self.payment_section
                        ], spacing=20)
                    ], spacing=10),
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
            
            # Verificar si hay un producto seleccionado en el almacenamiento del cliente
            selected_product_id = self.page.client_storage.get("selected_product_id")
            if selected_product_id is not None:
                try:
                    # Obtener el producto seleccionado
                    product = self.product_service.get_product_by_id(selected_product_id)
                    if product and product.stock > 0:
                        # Añadir el producto al carrito
                        self.add_to_cart(product)
                    # Limpiar el producto seleccionado del almacenamiento
                    self.page.client_storage.remove("selected_product_id")
                except Exception as e:
                    logging.error(f"Error al cargar producto seleccionado: {str(e)}")

        except Exception as e:
            logging.error(f"Error construyendo UI: {str(e)}")
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def build_search_section(self):
        # Crear campo de búsqueda
        self.search_input = ft.TextField(
            label="Buscar por nombre o categoría",
            width=400,
            prefix_icon=ft.icons.SEARCH,
            hint_text="Ingrese nombre o categoría del producto",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )
        
        # Botón de búsqueda
        search_button = ft.ElevatedButton(
            "Buscar",
            icon=ft.icons.SEARCH,
            on_click=self.search_products,
            style=ft.ButtonStyle(
                color=ft.colors.ON_PRIMARY,
                bgcolor=ft.colors.PRIMARY
            )
        )
        
        # Contenedor del formulario
        return ft.Container(
            content=ft.Row([
                self.search_input,
                search_button
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10
        )
    
    def build_products_section(self):
        # Crear tabla de productos
        self.products_table = ft.DataTable(
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
        
        return ft.Container(
            content=self.products_table,
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10
        )
    
    def build_cart_section(self):
        # Crear tabla del carrito
        self.cart_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Precio", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Cantidad", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Subtotal", color=ft.colors.ON_SURFACE)),
                ft.DataColumn(ft.Text("Acciones", color=ft.colors.ON_SURFACE)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
        )
        
        # Contenedor del carrito
        return ft.Container(
            content=self.cart_table,
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10
        )
    
    def build_customer_section(self):
        # Crear campos para el cliente
        self.customer_name = ft.TextField(
            label="Nombre del Cliente",
            width=300,
            hint_text="Opcional",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )
        
        self.customer_id = ft.TextField(
            label="Identificación",
            width=300,
            hint_text="Opcional",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )
        
        # Contenedor de información del cliente
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Información del Cliente", 
                    size=16, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                self.customer_name,
                self.customer_id
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10,
            width=350
        )
    
    def build_payment_section(self):
        # Crear sección de totales
        self.total_text = ft.Text(
            "Total: $0.00", 
            size=20, 
            weight=ft.FontWeight.BOLD,
            color=ft.colors.ON_SURFACE
        )

        # Botón para finalizar venta
        self.complete_sale_button = ft.ElevatedButton(
            "Finalizar Venta",
            icon=ft.icons.SHOPPING_CART_CHECKOUT,
            on_click=self.complete_sale,
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.colors.ON_PRIMARY,
                bgcolor=ft.colors.PRIMARY
            )
        )
        
        # Contenedor de pago
        return ft.Container(
                        content=ft.Column([
                ft.Text(
                    "Resumen de Pago", 
                    size=16, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                            self.total_text,
                self.complete_sale_button
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10,
            width=350
        )
    
    def search_products(self, e):
        try:
            search_term = self.search_input.value
            if not search_term:
                show_error_message(self.page, "Ingrese un término de búsqueda")
                return

            # Buscar productos
            products = self.product_service.search_products(search_term)
            
            # Crear filas para la tabla
            rows = []
            for product in products:
                # Verificar si hay stock
                stock_color = ft.colors.ERROR if product.stock <= 0 else ft.colors.ON_SURFACE
                
                # Crear fila con ID del producto para evitar problemas de referencia
                product_id = product.id
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
                                    tooltip="Agregar al carrito",
                                    disabled=product.stock <= 0,
                                    on_click=self.create_add_to_cart_callback(product_id)
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
            logging.error(f"Error al buscar productos: {str(e)}")
            show_error_message(self.page, f"Error al buscar productos: {str(e)}")
    
    def create_add_to_cart_callback(self, product_id):
        """Crea una función de callback para agregar al carrito"""
        def handle_click(e):
            try:
                product = self.product_service.get_product_by_id(product_id)
                if product:
                    self.add_to_cart(product)
                else:
                    show_error_message(self.page, f"No se pudo encontrar el producto con ID {product_id}")
            except Exception as ex:
                logging.error(f"Error en callback de agregar al carrito: {str(ex)}")
                show_error_message(self.page, f"Error al agregar al carrito: {str(ex)}")
        return handle_click
    
    def add_to_cart(self, product):
        try:
            # Verificar si el producto ya está en el carrito
            for item in self.cart:
                if item["product"].id == product.id:
                    # Verificar stock
                    if item["quantity"] >= product.stock:
                        show_error_message(self.page, "No hay suficiente stock")
                        return
                    
                    # Incrementar cantidad
                    item["quantity"] += 1
                    self.update_cart()
                    show_success_message(self.page, f"Se aumentó la cantidad de {product.name}")
                    return
            
            # Agregar nuevo producto al carrito
            self.cart.append({
                "product": product,
                "quantity": 1
            })
            
            # Actualizar carrito
            self.update_cart()
            show_success_message(self.page, f"Se agregó {product.name} al carrito")
            
        except Exception as e:
            logging.error(f"Error al agregar al carrito: {str(e)}")
            show_error_message(self.page, f"Error al agregar al carrito: {str(e)}")
    
    def update_cart(self):
        try:
            # Crear filas para la tabla
            rows = []
            total = 0
            
            for item in self.cart:
                product = item["product"]
                quantity = item["quantity"]
                subtotal = product.price * quantity
                total += subtotal
                
                # Crear fila con ID del producto para evitar problemas de referencia
                product_id = product.id
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(product.name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${product.price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.REMOVE,
                                    icon_color=ft.colors.ON_SURFACE_VARIANT,
                                    tooltip="Disminuir",
                                    on_click=self.create_decrease_callback(product_id)
                                ),
                                ft.Text(str(quantity), color=ft.colors.ON_SURFACE),
                                ft.IconButton(
                                    icon=ft.icons.ADD,
                                    icon_color=ft.colors.ON_SURFACE_VARIANT,
                                    tooltip="Aumentar",
                                    on_click=self.create_increase_callback(product_id)
                                ),
                            ])
                        ),
                        ft.DataCell(ft.Text(f"${subtotal:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.ERROR,
                                    tooltip="Eliminar",
                                    on_click=self.create_remove_callback(product_id)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla y total
            self.cart_table.rows = rows
            self.total_text.value = f"Total: ${total:.2f}"
            
            # Habilitar/deshabilitar botón de finalizar venta
            self.complete_sale_button.disabled = len(self.cart) == 0
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al actualizar carrito: {str(e)}")
            show_error_message(self.page, f"Error al actualizar carrito: {str(e)}")
    
    def create_decrease_callback(self, product_id):
        """Crea una función de callback para disminuir cantidad"""
        def handle_click(e):
            try:
                product = self.product_service.get_product_by_id(product_id)
                if product:
                    self.decrease_quantity(product)
                else:
                    show_error_message(self.page, f"No se pudo encontrar el producto con ID {product_id}")
            except Exception as ex:
                logging.error(f"Error en callback de disminuir cantidad: {str(ex)}")
                show_error_message(self.page, f"Error al disminuir cantidad: {str(ex)}")
        return handle_click
    
    def create_increase_callback(self, product_id):
        """Crea una función de callback para aumentar cantidad"""
        def handle_click(e):
            try:
                product = self.product_service.get_product_by_id(product_id)
                if product:
                    self.increase_quantity(product)
                else:
                    show_error_message(self.page, f"No se pudo encontrar el producto con ID {product_id}")
            except Exception as ex:
                logging.error(f"Error en callback de aumentar cantidad: {str(ex)}")
                show_error_message(self.page, f"Error al aumentar cantidad: {str(ex)}")
        return handle_click
    
    def create_remove_callback(self, product_id):
        """Crea una función de callback para eliminar del carrito"""
        def handle_click(e):
            try:
                product = self.product_service.get_product_by_id(product_id)
                if product:
                    self.remove_from_cart(product)
                else:
                    show_error_message(self.page, f"No se pudo encontrar el producto con ID {product_id}")
            except Exception as ex:
                logging.error(f"Error en callback de eliminar del carrito: {str(ex)}")
                show_error_message(self.page, f"Error al eliminar del carrito: {str(ex)}")
        return handle_click
    
    def decrease_quantity(self, product):
        try:
            for item in self.cart:
                if item["product"].id == product.id:
                    if item["quantity"] > 1:
                        item["quantity"] -= 1
                        show_success_message(self.page, f"Se disminuyó la cantidad de {product.name}")
                    else:
                        self.cart.remove(item)
                        show_success_message(self.page, f"Se eliminó {product.name} del carrito")
                    break

            self.update_cart()

        except Exception as e:
            logging.error(f"Error al disminuir cantidad: {str(e)}")
            show_error_message(self.page, f"Error al disminuir cantidad: {str(e)}")
    
    def increase_quantity(self, product):
        try:
            for item in self.cart:
                if item["product"].id == product.id:
                    # Verificar stock
                    if item["quantity"] >= item["product"].stock:
                        show_error_message(self.page, "No hay suficiente stock")
                        return
                    
                    item["quantity"] += 1
                    show_success_message(self.page, f"Se aumentó la cantidad de {product.name}")
                    break
            
            self.update_cart()
            
        except Exception as e:
            logging.error(f"Error al aumentar cantidad: {str(e)}")
            show_error_message(self.page, f"Error al aumentar cantidad: {str(e)}")
    
    def remove_from_cart(self, product):
        try:
            for item in self.cart:
                if item["product"].id == product.id:
                    self.cart.remove(item)
                    show_success_message(self.page, f"Se eliminó {product.name} del carrito")
                    break
            
            self.update_cart()
            
        except Exception as e:
            logging.error(f"Error al eliminar del carrito: {str(e)}")
            show_error_message(self.page, f"Error al eliminar del carrito: {str(e)}")
    
    def complete_sale(self, e):
        try:
            # Verificar que haya productos en el carrito
            if not self.cart:
                show_error_message(self.page, "No hay productos en el carrito")
                return
            
            # Preparar datos de la venta
            sale_data = {
                "customer_id": self.customer_id.value,
                "items": [],
                "payment_method": "efectivo"  # Valor por defecto
            }
            
            # Agregar items
            for item in self.cart:
                sale_data["items"].append({
                    "product_id": item["product"].id,
                    "quantity": item["quantity"],
                    "price": item["product"].price
                })
            
            # Crear venta
            sale = self.sale_service.create_sale(sale_data)
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, "Venta realizada correctamente")
            
            # Limpiar carrito
            self.cart = []
            self.update_cart()
            
            # Limpiar campos
            self.customer_name.value = ""
            self.customer_id.value = ""
            self.update()
            
            # Redirigir a la página de ventas después de un breve retraso
            self.page.go("/ver_ventas")
            
        except Exception as e:
            logging.error(f"Error al completar venta: {str(e)}")
            show_error_message(self.page, f"Error al completar venta: {str(e)}")
