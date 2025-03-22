import flet as ft
from services.productService import ProductService
from ui.components.data_table import DataTable
from ui.components.alerts import show_error_message, show_success_message
import logging
from pages.categories import PageCategory
from pages.inventory.PageProductForm import PageProductForm

class PageInventory(ft.UserControl):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.session = session
        self.product_service = ProductService(session)
        self.is_mobile = self.page.width < 600
        self.all_products = []
        self.table = None
        self.table_container = None
        self.search_field = None
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            # Cargar datos iniciales
            self.load_inventory()

            # Campo de búsqueda
            self.search_field = ft.TextField(
                label="Buscar productos",
                prefix_icon=ft.icons.SEARCH,
                width=min(self.page.width * 0.8, 500) if self.is_mobile else 500,
                border_radius=20,
                on_change=self.filter_products,
                hint_text="Ingrese el nombre del producto...",
                height=50
            )

            # Botones de acción
            inventory_actions = ft.Row([
                ft.FilledButton(
                    text="Agregar/Editar",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self.add_product()
                ),
                ft.FilledTonalButton(
                    text="Categorías",
                    icon=ft.icons.CATEGORY,
                    on_click=lambda _: self.show_categories()
                ),
                ft.FilledTonalButton(
                    text="Historial",
                    icon=ft.icons.HISTORY,
                    on_click=lambda _: self.page.go("/historial_inventario")
                )
            ], wrap=True, spacing=10)

            # Tabla de inventario con paginación y ordenamiento
            table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            product_data = self.get_product_data()
            self.table = DataTable(
                columns=["ID", "Código", "Nombre", "Categoría", "Subcategoría", "Stock", "Precio", "Estado", "Acciones"],
                data=product_data,
                items_per_page=10,
                on_select=self.edit_product,
                on_delete=self.delete_product
            )
            # Usar Column para scroll y Container para estilo
            self.table_container = ft.Column(
                [self.table],
                width=table_width,
                scroll=ft.ScrollMode.AUTO if self.is_mobile else None,
                expand=True,
                spacing=0
            )
            self.table_wrapper = ft.Container(
                content=self.table_container,
                padding=10,  # Padding aplicado al Container, no al Column
                border_radius=5,
                bgcolor=ft.colors.SURFACE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK)
                )
            )

            # UI principal usando Container con padding en lugar de pasarlo a Column
            content_column = ft.Column(
                [
                    ft.Text(
                        "Inventario",
                        size=20 if self.is_mobile else 24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Text(
                        "Gestión de inventario",
                        size=14 if self.is_mobile else 16,
                        color=ft.colors.ON_SURFACE_VARIANT
                    ),
                    ft.Container(height=10),
                    inventory_actions,
                    ft.Row([
                        self.search_field,
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            on_click=self.load_inventory,
                            icon_color=ft.colors.PRIMARY
                        )
                    ]),
                    ft.Container(height=10),
                    self.table_wrapper,
                    ft.Text(f"Total: {len(self.all_products)} productos", size=12, text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
            
            # Envolvemos el Column en un Container para aplicar el padding
            self.controls = [
                ft.Container(
                    content=content_column,
                    padding=10 if self.is_mobile else 20
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de inventario: {str(e)}")
            self.controls = [ft.Text(f"Error al cargar el inventario: {str(e)}", color=ft.colors.ERROR)]

    def load_inventory(self, e=None):
        try:
            logging.info("Iniciando carga de inventario")
            self.all_products = self.product_service.get_all_products()
            logging.info(f"Productos cargados: {len(self.all_products)}")
            if self.table:
                self.table.set_data(self.get_product_data())
                logging.info("Datos establecidos en la tabla")
            self.update()
        except Exception as e:
            logging.error(f"Error al cargar inventario: {str(e)}")
            show_error_message(self.page, f"Error al cargar inventario: {str(e)}")

    def filter_products(self, e):
        search_text = self.search_field.value.lower()
        filtered = [
            p for p in self.all_products
            if search_text in p.name.lower()
        ] if search_text else self.all_products.copy()
        self.table.set_data([
            {
                "ID": str(p.id),
                "Código": p.code or "N/A",
                "Nombre": p.name,
                "Categoría": p.category.name if p.category else "Sin categoría",
                "Subcategoría": p.subcategory.name if p.subcategory else "Sin subcategoría",
                "Stock": str(p.stock),
                "Precio": f"${p.price:.2f}",
                "Estado": "Disponible" if p.stock > 0 else "Agotado",
                "product": p
            } for p in filtered
        ])

    def get_product_data(self):
        return [
            {
                "ID": str(p.id),
                "Código": p.code or "N/A",
                "Nombre": p.name,
                "Categoría": p.category.name if p.category else "Sin categoría",
                "Subcategoría": p.subcategory.name if p.subcategory else "Sin subcategoría",
                "Stock": str(p.stock),
                "Precio": f"${p.price:.2f}",
                "Estado": "Disponible" if p.stock > 0 else "Agotado",
                "product": p
            } for p in self.all_products
        ]

    def edit_product(self, row_data):
        product = row_data["product"]
        self.page.client_storage.set("edit_product_id", product.id)
        self.page.go("/editar_producto")

    def delete_product(self, row_data):
        product = row_data["product"]
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"¿Eliminar producto {product.name}?"),
            content=ft.Text("Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_product(product))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def confirm_delete_product(self, product):
        self.product_service.delete_product(product.id)
        self.close_dialog()
        self.load_inventory()
        show_success_message(self.page, f"Producto {product.name} eliminado correctamente")

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.update()
        elif self.table_container:
            new_table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            self.table_container.width = new_table_width
            self.table_container.scroll = ft.ScrollMode.AUTO if self.is_mobile else None
            self.search_field.width = min(self.page.width * 0.8, 500) if self.is_mobile else 500
            self.update()

    def build(self):
        return ft.Column(self.controls, expand=True)

    def show_categories(self):
        self.controls.clear()
        self.controls.append(PageCategory(self.page, self.session))
        self.update()
    
    def add_product(self):
        self.controls.clear()
        self.controls.append(PageProductForm(self.page, self.session))
        self.update()