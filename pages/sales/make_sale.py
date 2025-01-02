import flet as ft
from services.productService import ProductService
from services.saleService import SaleService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class MakeSaleView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(controls=[], padding=0)
        self.page = page
        self.product_service = ProductService(session)
        self.sale_service = SaleService(session)
        self.cart = []
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            0, self.handle_navigation)

        self.product_dropdown = ft.Dropdown(
            label="Producto",
            width=300,
            options=self.get_product_options()
        )

        self.quantity_input = ft.TextField(
            label="Cantidad",
            width=300
        )

        self.search_name_input = ft.TextField(
            label="Buscar por Nombre",
            width=300
        )

        self.search_category_input = ft.TextField(
            label="Buscar por Categoría",
            width=300
        )

        self.min_price_input = ft.TextField(
            label="Precio Mínimo",
            width=140
        )

        self.max_price_input = ft.TextField(
            label="Precio Máximo",
            width=140
        )

        self.search_button = ft.ElevatedButton(
            "Buscar",
            on_click=self.search_products
        )

        self.cart_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("ID")),
                ft.DataColumn(label=ft.Text("Producto")),
                ft.DataColumn(label=ft.Text("Cantidad")),
                ft.DataColumn(label=ft.Text("Precio")),
                ft.DataColumn(label=ft.Text("Total"))
            ],
            rows=[]
        )

        self.total_text = ft.Text(
            "Total: $0.00", size=16, weight=ft.FontWeight.BOLD)

        self.add_product_button = ft.ElevatedButton(
            "Agregar Producto",
            on_click=self.add_product
        )

        self.finalize_sale_button = ft.ElevatedButton(
            "Finalizar Venta",
            on_click=self.finalize_sale
        )

        # Layout of the view
        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Realizar Venta", size=20,
                                    weight=ft.FontWeight.BOLD),
                            ft.Row([
                                self.search_name_input,
                                self.search_category_input,
                                self.min_price_input,
                                self.max_price_input,
                                self.search_button
                            ], spacing=10),
                            self.product_dropdown,
                            self.quantity_input,
                            self.add_product_button,
                            self.cart_table,
                            self.total_text,
                            ft.Row([
                                self.finalize_sale_button
                            ], spacing=10)
                        ], spacing=20)
                    )],
                    scroll=ft.ScrollMode.AUTO
                ),
                expand=True
            )]

    def get_product_options(self):
        products = self.product_service.get_all_products()
        return [ft.dropdown.Option(key=product.id, text=product.name) for product in products]

    def search_products(self, e):
        try:
            name = self.search_name_input.value
            category = self.search_category_input.value
            min_price = self.min_price_input.value
            max_price = self.max_price_input.value

            if name:
                products = self.product_service.get_products_by_name(name)
            elif category:
                products = self.product_service.get_products_by_category(
                    category)
            elif min_price and max_price:
                products = self.product_service.get_products_by_price_range(
                    float(min_price), float(max_price))
            else:
                products = self.product_service.get_all_products()

            self.product_dropdown.options = [ft.dropdown.Option(
                key=product.id, text=product.name) for product in products]
            self.product_dropdown.update()

        except Exception as e:
            show_error_message(
                self.page, f"Error al buscar productos: {str(e)}")

    def add_product(self, e):
        try:
            # Obtener datos del producto desde el dropdown y el campo de entrada
            product_id = self.get_product_id()
            quantity = self.get_quantity()

            # Validar datos
            if not product_id or not quantity:
                show_error_message(
                    self.page, "Debe ingresar un producto y una cantidad válida")
                return

            # Obtener información del producto desde la base de datos
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                show_error_message(self.page, "Producto no encontrado")
                return

            # Calcular el total del producto
            total = product.price * quantity

            # Agregar producto al carrito
            self.cart.append({
                "product_id": product_id,
                "name": product.name,
                "quantity": quantity,
                "price": product.price,
                "total": total
            })

            # Actualizar la tabla del carrito
            self.update_cart_table()

            # Mostrar mensaje de éxito
            show_success_message(self.page, "Producto agregado al carrito")

        except Exception as e:
            show_error_message(
                self.page, f"Error al agregar producto: {str(e)}")

    def finalize_sale(self, e):
        try:
            if not self.cart:
                show_error_message(self.page, "El carrito está vacío")
                return

            # Crear la venta en la base de datos
            sale_data = {
                "items": self.cart,
                "total": sum(item["total"] for item in self.cart)
            }
            self.sale_service.create_sale(sale_data)

            # Limpiar el carrito
            self.cart.clear()
            self.update_cart_table()

            # Mostrar mensaje de éxito
            show_success_message(self.page, "Venta finalizada con éxito")

        except Exception as e:
            show_error_message(
                self.page, f"Error al finalizar la venta: {str(e)}")

    def update_cart_table(self):
        self.cart_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(item["product_id"]))),
                ft.DataCell(ft.Text(item["name"])),
                ft.DataCell(ft.Text(str(item["quantity"]))),
                ft.DataCell(ft.Text(f"${item['price']:.2f}")),
                ft.DataCell(ft.Text(f"${item['total']:.2f}"))
            ]) for item in self.cart
        ]
        self.total_text.value = f"Total: ${
            sum(item['total'] for item in self.cart):.2f}"
        self.cart_table.update()  # Actualiza la tabla
        self.total_text.update()  # Actualiza el texto del total
        self.page.update()  # Actualiza la página

    def get_product_id(self):
        # Obtener el ID del producto desde el dropdown
        return int(self.product_dropdown.value)

    def get_quantity(self):
        # Obtener la cantidad desde el campo de entrada
        return int(self.quantity_input.value)

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")
