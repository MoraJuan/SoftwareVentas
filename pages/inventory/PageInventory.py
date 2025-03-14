import flet as ft
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from services.productService import ProductService
import logging

class PageInventory(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/ver_inventario",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.product_service = ProductService(session)
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(2, self.page)

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Gestión de Inventario", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Crear tabla de inventario
            self.inventory_table = self.build_inventory_table()
            
            # Cargar datos iniciales
            self.load_inventory()

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton(
                                "Nuevo Producto",
                                icon=ft.icons.ADD_BOX,
                                on_click=lambda _: self.page.go("/agregar_producto"),
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_PRIMARY,
                                    bgcolor=ft.colors.PRIMARY
                                )
                            ),
                            ft.OutlinedButton(
                                "Ajustar Stock",
                                icon=ft.icons.INVENTORY,
                                on_click=lambda _: self.page.go("/ajustar_stock"),
                            ),
                            ft.ElevatedButton(
                                "Actualizar Datos",
                                icon=ft.icons.REFRESH,
                                on_click=self.load_inventory,
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_SURFACE,
                                    bgcolor=ft.colors.SURFACE_VARIANT
                                )
                            )
                        ], spacing=10),
                        ft.Container(height=20),
                        ft.Text(
                            "Productos en Inventario",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.inventory_table
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

    def build_inventory_table(self):
        try:
            # Crear tabla de inventario
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Código", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Nombre", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Categoría", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Stock", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Precio", color=ft.colors.ON_SURFACE)),
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
            logging.error(f"Error construyendo tabla de inventario: {str(e)}")
            return ft.Text("Error al cargar la tabla de inventario", color=ft.colors.ERROR)
            
    def load_inventory(self, e=None):
        """Carga los productos en la tabla de inventario"""
        try:
            # Obtener todos los productos
            products = self.product_service.get_all_products()
            
            # Crear filas para la tabla
            rows = []
            for product in products:
                # Formatear stock
                stock_color = ft.colors.ERROR if product.stock <= 0 else ft.colors.ON_SURFACE
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(product.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(getattr(product, 'code', 'N/A'), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(product.name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(product.category or "Sin categoría", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(str(product.stock), color=stock_color)),
                        ft.DataCell(ft.Text(f"${product.price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text("Disponible", color=ft.colors.GREEN)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Editar",
                                    on_click=lambda _, p=product: self.edit_product(p)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.ERROR,
                                    tooltip="Eliminar",
                                    on_click=lambda _, p=product: self.delete_product(p)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.inventory_table.rows = rows
            
            # Mostrar mensaje si no hay resultados
            if not rows:
                show_error_message(self.page, "No se encontraron productos en inventario")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar inventario: {str(e)}")
            show_error_message(self.page, f"Error al cargar inventario: {str(e)}")
            
    def edit_product(self, product):
        """Navega a la página de edición de producto"""
        try:
            self.page.client_storage.set("edit_product_id", product.id)
            self.page.go("/editar_producto")
        except Exception as e:
            logging.error(f"Error al editar producto: {str(e)}")
            show_error_message(self.page, f"Error al editar producto: {str(e)}")
            
    def delete_product(self, product):
        """Elimina un producto"""
        try:
            # Confirmar eliminación
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"¿Eliminar producto {product.name}?"),
                content=ft.Text("Esta acción no se puede deshacer."),
                actions=[
                    ft.TextButton("Cancelar", on_click=self.close_dialog),
                    ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_product(product)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logging.error(f"Error al eliminar producto: {str(e)}")
            show_error_message(self.page, f"Error al eliminar producto: {str(e)}")
            
    def confirm_delete_product(self, product):
        """Confirma la eliminación de un producto"""
        try:
            # Eliminar producto
            self.product_service.delete_product(product.id)
            
            # Cerrar diálogo
            self.close_dialog()
            
            # Recargar productos
            self.load_inventory()
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Producto {product.name} eliminado correctamente")
        except Exception as e:
            logging.error(f"Error al eliminar producto: {str(e)}")
            show_error_message(self.page, f"Error al eliminar producto: {str(e)}")
            
    def close_dialog(self, e=None):
        """Cierra el diálogo actual"""
        self.page.dialog.open = False
        self.page.update() 