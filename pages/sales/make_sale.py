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

        self.product_dropdown = ft.Dropdown(
            label="Producto",
            width=300,
            options=self.get_product_options()
        )

        self.quantity_input = ft.TextField(
            label="Cantidad",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.add_product_button = ft.ElevatedButton(
            "Agregar Producto",
            on_click=self.add_product
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
                            ft.Text("Realizar Venta", size=20, weight=ft.FontWeight.BOLD),
                            self.customer_dropdown,
                            self.payment_method_dropdown,
                            ft.Row([
                                self.product_dropdown,
                                self.quantity_input,
                                self.add_product_button
                            ], spacing=10),
                            self.cart_table,
                            self.total_text,
                            self.finalize_sale_button
                        ], spacing=20)
                    )
                ]),
                expand=True
            )
        ]

    def get_customer_options(self):
        customers = self.customer_service.get_all_customers()
        return [ft.dropdown.Option(str(customer.id), customer.name) for customer in customers]

    def get_product_options(self):
        products = self.product_service.get_all_products()
        return [ft.dropdown.Option(str(product.id), product.name) for product in products]

    def add_product(self, e):
        try:
            product_id = int(self.product_dropdown.value)
            quantity = int(self.quantity_input.value)

            if not product_id or not quantity:
                show_error_message(
                    self.page, "Debe seleccionar un producto y una cantidad válida."
                )
                return

            product = self.product_service.get_product_by_id(product_id)
            if not product:
                logging.error(f"Producto con ID {product_id} no encontrado.")
                show_error_message(self.page, "Producto no encontrado.")
                return

            if product.stock < quantity:
                logging.error(f"Stock insuficiente para el producto ID {product_id}.")
                show_error_message(self.page, "Stock insuficiente para el producto seleccionado.")
                return

            total = product.price * quantity

            self.cart.append({
                "product_id": product_id,
                "name": product.name,
                "quantity": quantity,
                "price": product.price,
                "total": total
            })

            self.update_cart_table()
            show_success_message(self.page, "Producto agregado al carrito.")

        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
            show_error_message(
                self.page, "Por favor ingrese valores numéricos válidos para el ID del producto y la cantidad."
            )
        except Exception as e:
            logging.error(f"Exception: {e}")
            show_error_message(
                self.page, f"Error al agregar producto: {str(e)}"
            )

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
        self.total_text.value = f"Total: ${sum(item['total'] for item in self.cart):.2f}"
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
                show_error_message(self.page, "Por favor seleccione un cliente y método de pago.")
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
            show_error_message(self.page, f"Error al finalizar la venta: {str(e)}")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")