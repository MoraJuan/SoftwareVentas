import flet as ft
import csv
from io import StringIO
from sqlalchemy.orm import Session
from services.productService import ProductService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index

class PageProduct(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_productos", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Productos"
        self.product_service = ProductService(session)
        self.all_products = []
        self.current_page = 1
        self.products_per_page = 10
        self.sort_column = None
        self.sort_reverse = False
        self.build_ui()

    def build_ui(self):
        try:
            # Inicializar controles
            self.navigation_rail = create_navigation_rail(2, self.handle_navigation)

            # Campo de búsqueda
            self.search_field = ft.TextField(
                label="Buscar producto",
                width=300,
                prefix_icon=ft.icons.SEARCH,
                on_change=self.filter_products
            )

            # Botón de exportar a CSV
            self.export_button = ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                tooltip="Exportar a CSV",
                on_click=self.export_to_csv
            )

            # Controles de paginación
            self.prev_button = ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                tooltip="Página anterior",
                on_click=self.prev_page
            )
            self.next_button = ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                tooltip="Página siguiente",
                on_click=self.next_page
            )
            self.page_info = ft.Text(f"Páginas: {self.current_page}")

            # Barra de progreso
            self.progress_bar = ft.ProgressBar(visible=False)

            # Tabla de productos
            self.product_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID"), on_sort=self.sort_products),
                    ft.DataColumn(ft.Text("Nombre"), on_sort=self.sort_products),
                    ft.DataColumn(ft.Text("Precio"), on_sort=self.sort_products),
                    ft.DataColumn(ft.Text("Stock"), on_sort=self.sort_products),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=[]
            )

            # Botón para agregar producto
            self.add_button = ft.ElevatedButton(
                "Agregar Producto",
                on_click=lambda e: self.page.go("/agregar_productos")
            )

            self.load_products()

            # Diseño del contenido
            content = ft.Column([
                ft.Text("Productos", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.search_field,
                    self.export_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.progress_bar,
                self.add_button,
                ft.Divider(height=20),
                self.product_table,
                ft.Row([
                    self.prev_button,
                    self.page_info,
                    self.next_button
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=20)

            # Configuración principal de controles sin scroll
            self.controls = [
                ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        content=content,
                        expand=True,
                        padding=20
                    )
                ], expand=True)
            ]

            # Cargar productos al iniciar la página
            self.load_products()

        except Exception as e:
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def handle_navigation(self, e):
        """Manejar eventos de navegación"""
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
            self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")

    def filter_products(self, e):
        """Filtrar productos según el texto de búsqueda"""
        search_term = self.search_field.value.lower()
        filtered = [
            product for product in self.all_products
            if search_term in product.name.lower()
        ]
        self.update_table(filtered)
        self.update()

    def export_to_csv(self, e):
        """Exportar la lista de productos a un archivo CSV"""
        try:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Nombre", "Precio", "Stock"])
            for product in self.all_products:
                writer.writerow([product.id, product.name, product.price, product.stock])
            csv_data = output.getvalue()
            # Codificar datos CSV para URL
            csv_url = f"data:text/csv;charset=utf-8,{csv_data}"
            self.page.launch_url(csv_url)
            show_success_message(self.page, "Productos exportados exitosamente.")
        except Exception as e:
            show_error_message(self.page, f"Error al exportar productos: {str(e)}")

    def sort_products(self, e):
        """Ordenar productos según la columna clicada"""
        column = e.column_index
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        if column == 0:  # ID
            self.all_products.sort(key=lambda p: p.id, reverse=self.sort_reverse)
        elif column == 1:  # Nombre
            self.all_products.sort(key=lambda p: p.name.lower(), reverse=self.sort_reverse)
        elif column == 2:  # Precio
            self.all_products.sort(key=lambda p: p.price, reverse=self.sort_reverse)
        elif column == 3:  # Stock
            self.all_products.sort(key=lambda p: p.stock, reverse=self.sort_reverse)

        self.update_table(self.get_paginated_products())

    def prev_page(self, e):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()

    def next_page(self, e):
        """Ir a la página siguiente"""
        total_pages = (len(self.all_products) + self.products_per_page - 1) // self.products_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_pagination()

    def update_pagination(self):
        """Actualizar la tabla basada en la página actual"""
        paginated = self.get_paginated_products()
        self.update_table(paginated)
        total_pages = (len(self.all_products) + self.products_per_page - 1) // self.products_per_page
        self.page_info.value = f"Páginas: {self.current_page} de {total_pages}"
        self.page_info.update()

    def get_paginated_products(self):
        """Obtener productos para la página actual"""
        start = (self.current_page - 1) * self.products_per_page
        end = start + self.products_per_page
        return self.all_products[start:end]

    def update_table(self, products):
        """Actualizar la tabla de productos con la lista proporcionada"""
        self.product_table.rows.clear()
        for product in products:
            self.add_product_to_table(product)
        self.product_table.update()

    def add_product_to_table(self, product):
        """Método auxiliar para agregar un producto a la tabla"""
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

    def edit_product(self, product):
        """Navegar a la página de edición de producto"""
        try:
            self.page.client_storage.set("edit_product_id", product.id)
            self.page.go("/editar_producto")
        except Exception as e:
            show_error_message(self.page, f"Error al editar el producto: {str(e)}")

    def delete_product(self, product):
        """Mostrar diálogo de confirmación antes de eliminar"""
        try:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Eliminación"),
                content=ft.Text(f"¿Está seguro que desea eliminar el producto {product.name}?"),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: self.close_dialog()
                    ),
                    ft.TextButton(
                        "Eliminar",
                        on_click=lambda e: self.confirm_delete_product(product)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error al mostrar diálogo de confirmación: {str(e)}")

    def confirm_delete_product(self, product):
        """Eliminar el producto después de la confirmación"""
        try:
            self.product_service.delete_product(product.id)
            show_success_message(self.page, "Producto eliminado exitosamente.")
            self.load_products()
            self.close_dialog()
        except Exception as e:
            show_error_message(self.page, f"Error al eliminar el producto: {str(e)}")

    def close_dialog(self):
        """Cerrar el diálogo actualmente abierto"""
        self.page.dialog.open = False
        self.page.update()

    def load_products(self):
        """Cargar productos desde la base de datos"""
        try:
            self.all_products = self.product_service.get_all_products()
            self.update_pagination()
        except Exception as e:
            show_error_message(self.page, f"Error al cargar productos: {str(e)}")
