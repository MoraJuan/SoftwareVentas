import flet as ft
from services.productService import ProductService
from services.saleService import SaleService
from services.customerService import CustomerService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index
import logging


class MakeSaleView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(controls=[], padding=0)
        self.page = page
        self.product_service = ProductService(session)
        self.sale_service = SaleService(session)
        self.customer_service = CustomerService(session)
        self.cart = []
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            1, self.handle_navigation)

        self.customer_dropdown = ft.Dropdown(
            label="Cliente",
            width=300,
            options=self.get_customer_options()
        )

        self.payment_method_dropdown = ft.Dropdown(
            label="Método de Pago",
            width=300,
            options=[
                ft.dropdown.Option("efectivo", "Efectivo"),
                ft.dropdown.Option("tarjeta", "Tarjeta"),
                ft.dropdown.Option("transferencia", "Transferencia")
            ]
        )

        self.search_name_input = ft.TextField(
            label="Buscar por Nombre",
            width=300,
            on_change=self.search_products
        )

        self.search_category_input = ft.TextField(
            label="Buscar por Categoría",
            width=300,
            on_change=self.search_products
        )

        self.product_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("ID")),
                ft.DataColumn(label=ft.Text("Producto")),
                ft.DataColumn(label=ft.Text("Precio")),
                ft.DataColumn(label=ft.Text("Cantidad")),
                ft.DataColumn(label=ft.Text("Agregar")),
            ],
            rows=self.get_initial_product_rows()
        )

        self.cart_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("ID")),
                ft.DataColumn(label=ft.Text("Producto")),
                ft.DataColumn(label=ft.Text("Cantidad")),
                ft.DataColumn(label=ft.Text("Precio")),
                ft.DataColumn(label=ft.Text("Eliminar")),
                ft.DataColumn(label=ft.Text("Total"))
            ],
            rows=[]
        )

        self.total_text = ft.Text(
            "Total: $0.00", size=16, weight=ft.FontWeight.BOLD
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
                            self.customer_dropdown,
                            self.payment_method_dropdown,
                            ft.Row([
                                self.search_name_input,
                                self.search_category_input
                            ]),
                            ft.Row([
                                self.product_table,
                                self.cart_table
                            ]),
                            self.total_text,
                            self.finalize_sale_button
                        ], spacing=20)
                    )
                ]),
                expand=True
            )
        ]

    def get_initial_product_rows(self):
        products = self.product_service.get_all_products()
        self.product_quantities = {}
        return self.get_product_rows(products)

    def get_product_rows(self, products):
        self.product_quantities = {}  # Reiniciar cantidades
        return [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(pro.id))),
                ft.DataCell(ft.Text(pro.name)),
                ft.DataCell(ft.Text(f"${pro.price:.2f}")),
                ft.DataCell(ft.TextField(
                    label="Cantidad",
                    width=100,
                    on_change=lambda e, product_id=pro.id: self.update_quantity(
                        product_id, e.control.value)
                )),
                ft.DataCell(ft.ElevatedButton(
                    content=ft.Icon(ft.icons.ADD),
                    on_click=lambda e, product_id=pro.id: self.add_product(
                        product_id)
                )),
            ]) for pro in products
        ]

    def update_quantity(self, product_id, quantity):
        """Actualiza la cantidad en el diccionario al cambiar."""
        try:
            self.product_quantities[product_id] = int(quantity)
            print(self.product_quantities)
        except ValueError:
            # Evita errores con entradas no numéricas
            self.product_quantities[product_id] = 0

    def add_product(self, e):
        try:
            # Validar si los campos no están vacíos antes de intentar convertirlos
            product_id = int(e)

            # Si no existe, inicializar cantidad a 1
            if product_id not in self.product_quantities:
                self.product_quantities[product_id] = 1
            else:
                # Si ya existe, incrementar la cantidad
                self.product_quantities[product_id] += 1

            # Obtener el producto
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                logging.error(f"Producto con ID {product_id} no encontrado.")
                show_error_message(self.page, "Producto no encontrado.")
                return

            # Verificar el stock
            if product.stock < self.product_quantities[product_id]:
                logging.error(
                    f"Stock insuficiente para el producto ID {product_id}.")
                show_error_message(
                    self.page, "Stock insuficiente para el producto seleccionado.")
                return

            # Calcular total y actualizar o agregar al carrito
            for item in self.cart:
                if item["product_id"] == product_id:
                    item["quantity"] = self.product_quantities[product_id]
                    item["total"] = item["price"] * item["quantity"]
                    break
            else:
                total = product.price * self.product_quantities[product_id]
                self.cart.append({
                    "product_id": product_id,
                    "name": product.name,
                    "quantity": self.product_quantities[product_id],
                    "price": product.price,
                    "total": total
                })

            self.update_cart_table()
            show_success_message(self.page, "Producto agregado al carrito.")

        except ValueError:
            show_error_message(
                self.page, "Debe ingresar valores numéricos válidos.")
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
            show_error_message(self.page, f"Error inesperado: {e}")

    def search_products(self, e):
        try:
            name = self.search_name_input.value
            category = self.search_category_input.value

            if name:
                products = self.product_service.get_products_by_name(name)
            elif category:
                products = self.product_service.get_products_by_category(
                    category)
            else:
                products = self.product_service.get_all_products()

            self.product_table.rows = self.get_product_rows(products)
            self.product_table.update()

        except Exception as e:
            show_error_message(
                self.page, f"Error al buscar productos: {str(e)}")

    def get_customer_options(self):
        customers = self.customer_service.get_all_customers()
        return [ft.dropdown.Option(str(customer.id), customer.name) for customer in customers]

    def update_cart_table(self):
        self.cart_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(item["product_id"]))),
                ft.DataCell(ft.Text(item["name"])),
                ft.DataCell(ft.Text(str(item["quantity"]))),
                ft.DataCell(ft.Text(f"${item['price']:.2f}")),
                ft.DataCell(ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="Eliminar",
                    on_click=lambda e, p=item: self.delete_product(
                        p["product_id"])
                )),
                ft.DataCell(ft.Text(f"${item['total']:.2f}"))
            ]) for item in self.cart
        ]
        self.total_text.value = f"Total: ${
            sum(item['total'] for item in self.cart):.2f}"
        self.cart_table.update()
        self.total_text.update()

    def finalize_sale(self, e):
        try:
            if not self.cart:
                show_error_message(self.page, "El carrito está vacío.")
                return

            customer_id = self.customer_dropdown.value
            payment_method = self.payment_method_dropdown.value.lower()

            if not customer_id or not payment_method:
                show_error_message(
                    self.page, "Por favor seleccione un cliente y método de pago.")
                return

            try:
                customer_id = int(customer_id)
            except ValueError:
                show_error_message(self.page, "ID de cliente inválido")
                return

            sale_data = {
                "customer_id": customer_id,
                "employee_id": 1,
                "payment_method": payment_method,
                "items": self.cart,
                "total": float(sum(item["total"] for item in self.cart))
            }

            result = self.sale_service.create_sale(sale_data)
            if result:
                show_success_message(self.page, "Venta finalizada con éxito.")
                self.cart.clear()
                self.update_cart_table()
                self.page.go("/ver_ventas")
            else:
                show_error_message(self.page, "Error al crear la venta")

        except Exception as e:
            logging.error(f"Error en finalize_sale: {str(e)}")
            show_error_message(
                self.page, f"Error al finalizar la venta: {str(e)}")

    def delete_product(self, product_id):
        self.cart = [
            item for item in self.cart if item['product_id'] != product_id]
        self.update_cart_table()
        show_success_message(self.page, "Producto eliminado del carrito.")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")