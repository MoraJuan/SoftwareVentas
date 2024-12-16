import flet as ft
from sqlalchemy.orm import Session
from services.productService import ProductService
from ui.components.alerts import show_success_message, show_error_message

class PageProduct(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_productos", controls=[], padding=20)
        self.page = page
        self.session = session
        self.page.title = "Lista de Productos"
        self.product_service = ProductService(session)
        self.build_ui()

    def build_ui(self):
        # Tabla de productos
        self.product_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # Campos de entrada
        self.name_input = ft.TextField(
            label="Nombre del Producto",
            width=300,
        )
        self.price_input = ft.TextField(
            label="Precio",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.stock_input = ft.TextField(
            label="Stock",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        # Botones
        self.add_button = ft.ElevatedButton(
            text="Agregar Producto",
            icon=ft.icons.ADD,
            on_click=self.add_product
        )
        self.home_button = ft.IconButton(
            icon=ft.icons.HOME,
            tooltip="Volver al Dashboard",
            on_click=lambda e: self.page.go("/dashboard")
        )

        # Layout de la vista
        self.controls = [
            ft.Column([
                ft.Row([
                    ft.Text("Productos", weight=ft.FontWeight.BOLD, size=20),
                    self.home_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    self.name_input,
                    self.price_input,
                    self.stock_input,
                    self.add_button
                ], spacing=10),
                self.product_table
            ], spacing=20)
        ]

        self.load_products()

    def load_products(self):
        try:
            products = self.product_service.get_all_products()
            self.product_table.rows.clear()
            for product in products:
                self.product_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(product.id))),
                            ft.DataCell(ft.Text(product.name)),
                            ft.DataCell(ft.Text(f"${product.price:.2f}")),
                            ft.DataCell(ft.Text(str(product.stock))),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda e, p=product: self.edit_product(p)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda e, p=product: self.delete_product(p)
                                    ),
                                ])
                            ),
                        ]
                    )
                )
            self.update()
        except Exception as e:
            show_error_message(self.page, f"Error al cargar los productos: {str(e)}")

    def add_product(self, e):
        try:
            name = self.name_input.value
            price = float(self.price_input.value)
            stock = int(self.stock_input.value)

            if not name:
                show_error_message(self.page, "El nombre del producto es obligatorio.")
                return

            new_product = {
                "name": name,
                "price": price,
                "stock": stock
            }
            self.product_service.create_product(new_product)
            show_success_message(self.page, "Producto agregado exitosamente.")
            self.name_input.value = ""
            self.price_input.value = ""
            self.stock_input.value = ""
            self.load_products()
        except ValueError:
            show_error_message(self.page, "Por favor ingrese valores numéricos válidos para precio y stock.")
        except Exception as e:
            show_error_message(self.page, f"Error al agregar el producto: {str(e)}")

    def edit_product(self, product):
        try:
            self.page.client_storage.set("edit_product_id", product.id)
            self.page.go("/editar_producto")
        except Exception as e:
            show_error_message(self.page, f"Error al editar el producto: {str(e)}")

    def delete_product(self, product):
        try:
            self.product_service.delete_product(product.id)
            show_success_message(self.page, "Producto eliminado exitosamente.")
            self.load_products()
        except Exception as e:
            show_error_message(self.page, f"Error al eliminar el producto: {str(e)}")
            
    def clear_products(self, e=None):
        try:
            if self.product_service.delete_all_products():
                self.load_products()
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Productos eliminados correctamente"))
                )
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Error al eliminar productos"))
                )
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"))
            )

    def clear_inputs(self):
        self.name_input.value = ""
        self.price_input.value = ""
        self.stock_input.value = ""
        self.page.update()