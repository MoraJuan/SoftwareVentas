# PageProduct.py
import flet as ft
from sqlalchemy.orm import Session
from services.productService import ProductService
from ui.components.alerts import show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class PageProduct(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_productos", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Productos"
        self.product_service = ProductService(session)
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            0, self.handle_navigation)

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

        self.add_button = ft.ElevatedButton(
            "Agregar Producto",
            on_click=lambda e: self.page.go("/agregar_productos")
        )

        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Productos",
                                    weight=ft.FontWeight.BOLD, size=20),
                            self.add_button,
                            self.product_table
                        ],
                            scroll=ft.ScrollMode.AUTO
                        ),
                        expand=True,
                        padding=20,

                    )
                ]),
                expand=True,
            )]

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
                                        on_click=lambda e, p=product: self.edit_product(
                                            p)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda e, p=product: self.delete_product(
                                            p)
                                    ),
                                ])
                            ),
                        ]
                    )
                )
            self.update()
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los productos: {str(e)}")

    def edit_product(self, product):
        try:
            self.page.client_storage.set("edit_product_id", product.id)
            self.page.go("/editar_producto")
        except Exception as e:
            show_error_message(
                self.page, f"Error al editar el producto: {str(e)}")

    def delete_product(self, product):
        try:
            self.product_service.delete_product(product.id)
            self.load_products()
        except Exception as e:
            show_error_message(
                self.page, f"Error al eliminar el producto: {str(e)}")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")
