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
        self.all_products = []  # Lista para almacenar todos los productos
        self.filtered_products = []  # Lista para almacenar productos filtrados
        self.sort_column_index = 2  # Por defecto ordenar por nombre (índice 2)
        self.sort_ascending = True  # Por defecto orden ascendente
        self.current_page = 1  # Página actual
        self.items_per_page = 10  # Productos por página
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

            # Crear campo de búsqueda
            self.search_field = ft.TextField(
                label="Buscar productos",
                prefix_icon=ft.icons.SEARCH,
                expand=True,
                border_radius=20,
                on_change=self.filter_products,
                hint_text="Ingrese el nombre del producto...",
                height=50
            )

            # Crear tabla de inventario
            self.inventory_table = self.build_inventory_table()
            
            # Contenedor para la tabla que se actualizará
            self.table_container = ft.Container(
                content=self.inventory_table,
                expand=True
            )
            
            # Crear botones de paginación directamente
            self.btn_first_page = ft.IconButton(
                icon=ft.icons.FIRST_PAGE,
                tooltip="Primera página",
                on_click=self.go_to_first_page,
                disabled=self.current_page == 1,
                icon_color=ft.colors.PRIMARY
            )
            
            self.btn_prev_page = ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                tooltip="Página anterior",
                on_click=self.go_to_prev_page,
                disabled=self.current_page == 1,
                icon_color=ft.colors.PRIMARY
            )
            
            self.page_info_text = ft.Text(
                f"Página {self.current_page} de {self.get_total_pages()}",
                color=ft.colors.ON_SURFACE
            )
            
            self.page_indicator = ft.Container(
                content=self.page_info_text,
                padding=ft.padding.symmetric(horizontal=10),
                border_radius=8,
                bgcolor=ft.colors.with_opacity(0.05, ft.colors.PRIMARY)
            )
            
            self.btn_next_page = ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                tooltip="Página siguiente",
                on_click=self.go_to_next_page,
                disabled=self.current_page == self.get_total_pages(),
                icon_color=ft.colors.PRIMARY
            )
            
            self.btn_last_page = ft.IconButton(
                icon=ft.icons.LAST_PAGE,
                tooltip="Última página",
                on_click=self.go_to_last_page,
                disabled=self.current_page == self.get_total_pages(),
                icon_color=ft.colors.PRIMARY
            )
            
            self.total_products_text = ft.Text(
                f"Total: {len(self.filtered_products)} productos",
                color=ft.colors.ON_SURFACE_VARIANT,
                size=12
            )
            
            # Crear fila de paginación simplificada
            pagination_row = ft.Row(
                [
                    self.btn_first_page,
                    self.btn_prev_page,
                    self.page_indicator,
                    self.btn_next_page,
                    self.btn_last_page,
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
            
            # Crear contenedor para el contador de productos
            products_counter = ft.Container(
                content=self.total_products_text,
                alignment=ft.alignment.center
            )
            
            # Contenedor de paginación simplificado
            self.pagination_container = ft.Container(
                content=ft.Column([
                    pagination_row,
                    products_counter
                ]),
                margin=ft.margin.only(top=20)
            )
            
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
                        # Agregar campo de búsqueda
                        ft.Container(
                            content=self.search_field,
                            margin=ft.margin.only(bottom=15)
                        ),
                        ft.Text(
                            "Productos en Inventario",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        # Tabla de inventario
                        self.table_container,
                        # Controles de paginación simplificados
                        self.pagination_container
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
            
    def filter_products(self, e):
        """Filtra los productos según el texto de búsqueda"""
        try:
            search_text = self.search_field.value.lower()
            
            if not search_text:
                # Si no hay texto de búsqueda, mostrar todos los productos
                self.filtered_products = self.all_products.copy()
            else:
                # Filtrar productos que contengan el texto de búsqueda en el nombre
                self.filtered_products = [
                    product for product in self.all_products 
                    if search_text in product.name.lower()
                ]
            
            # Aplicar ordenamiento actual a los productos filtrados
            self.sort_products()
            
            # Volver a la primera página cuando se filtra
            self.current_page = 1
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.inventory_table = self.build_inventory_table()
            self.table_container.content = self.inventory_table
            
            # Actualizar la tabla con los productos de la página actual
            self.update_table_with_products(self.get_current_page_products())
                
        except Exception as e:
            logging.error(f"Error al filtrar productos: {str(e)}")
            show_error_message(self.page, f"Error al filtrar productos: {str(e)}")
    
    def sort_products(self):
        """Ordena los productos según la columna seleccionada"""
        try:
            # Definir la función de ordenamiento según el índice de columna
            if self.sort_column_index == 0:  # ID
                key_func = lambda p: p.id
            elif self.sort_column_index == 1:  # Código
                key_func = lambda p: p.code.lower() if p.code else ""
            elif self.sort_column_index == 2:  # Nombre
                key_func = lambda p: p.name.lower() if p.name else ""
            elif self.sort_column_index == 3:  # Categoría
                key_func = lambda p: (p.category or "").lower()
            elif self.sort_column_index == 4:  # Stock
                key_func = lambda p: p.stock or 0
            elif self.sort_column_index == 5:  # Precio
                key_func = lambda p: p.price or 0
            else:
                # Por defecto ordenar por nombre
                key_func = lambda p: p.name.lower() if p.name else ""
            
            # Ordenar la lista de productos
            self.filtered_products.sort(key=key_func, reverse=not self.sort_ascending)
            
        except Exception as e:
            logging.error(f"Error al ordenar productos: {str(e)}")
            show_error_message(self.page, f"Error al ordenar productos: {str(e)}")
    
    def manual_sort(self, column_index):
        """Método alternativo para manejar el ordenamiento al hacer clic en una columna"""
        try:
            # Si se hace clic en la misma columna, invertir el orden
            if column_index == self.sort_column_index:
                self.sort_ascending = not self.sort_ascending
            else:
                # Si se hace clic en una columna diferente, establecer como nueva columna de ordenamiento
                self.sort_column_index = column_index
                self.sort_ascending = True
            
            # Ordenar productos
            self.sort_products()
            
            # Crear una nueva tabla con los iconos de ordenamiento actualizados
            self.inventory_table = self.build_inventory_table()
            
            # Actualizar el contenedor de la tabla
            self.table_container.content = self.inventory_table
            
            # Actualizar la tabla con los productos de la página actual
            self.update_table_with_products(self.get_current_page_products())
            
            # Actualizar la UI
            self.update()
            
        except Exception as e:
            logging.error(f"Error al manejar ordenamiento manual: {str(e)}")
            show_error_message(self.page, f"Error al ordenar tabla: {str(e)}")
            
    def update_table_with_products(self, products):
        """Actualiza la tabla con los productos proporcionados"""
        try:
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
                if self.search_field.value:
                    show_error_message(self.page, f"No se encontraron productos que coincidan con '{self.search_field.value}'")
                else:
                    show_error_message(self.page, "No se encontraron productos en inventario")
            
            # Actualizar controles de paginación
            total_pages = self.get_total_pages()
            self.page_info_text.value = f"Página {self.current_page} de {total_pages}"
            self.total_products_text.value = f"Total: {len(self.filtered_products)} productos"
            
            # Actualizar estado de los botones de paginación
            self.btn_first_page.disabled = self.current_page == 1
            self.btn_prev_page.disabled = self.current_page == 1
            self.btn_next_page.disabled = self.current_page == total_pages
            self.btn_last_page.disabled = self.current_page == total_pages
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al actualizar tabla: {str(e)}")
            show_error_message(self.page, f"Error al actualizar tabla: {str(e)}")

    def build_inventory_table(self):
        try:
            # Crear tabla de inventario con encabezados clicables para ordenamiento
            return ft.DataTable(
                columns=[
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Row([
                                ft.Text("ID", color=ft.colors.ON_SURFACE),
                                ft.Icon(
                                    name=ft.icons.ARROW_UPWARD if self.sort_column_index == 0 and self.sort_ascending else
                                         ft.icons.ARROW_DOWNWARD if self.sort_column_index == 0 and not self.sort_ascending else None,
                                    size=16,
                                    color=ft.colors.PRIMARY if self.sort_column_index == 0 else ft.colors.TRANSPARENT
                                )
                            ], spacing=5),
                            on_click=lambda _: self.manual_sort(0)
                        )
                    ),
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Código", color=ft.colors.ON_SURFACE),
                                ft.Icon(
                                    name=ft.icons.ARROW_UPWARD if self.sort_column_index == 1 and self.sort_ascending else
                                         ft.icons.ARROW_DOWNWARD if self.sort_column_index == 1 and not self.sort_ascending else None,
                                    size=16,
                                    color=ft.colors.PRIMARY if self.sort_column_index == 1 else ft.colors.TRANSPARENT
                                )
                            ], spacing=5),
                            on_click=lambda _: self.manual_sort(1)
                        )
                    ),
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Nombre", color=ft.colors.ON_SURFACE),
                                ft.Icon(
                                    name=ft.icons.ARROW_UPWARD if self.sort_column_index == 2 and self.sort_ascending else
                                         ft.icons.ARROW_DOWNWARD if self.sort_column_index == 2 and not self.sort_ascending else None,
                                    size=16,
                                    color=ft.colors.PRIMARY if self.sort_column_index == 2 else ft.colors.TRANSPARENT
                                )
                            ], spacing=5),
                            on_click=lambda _: self.manual_sort(2)
                        )
                    ),
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Categoría", color=ft.colors.ON_SURFACE),
                                ft.Icon(
                                    name=ft.icons.ARROW_UPWARD if self.sort_column_index == 3 and self.sort_ascending else
                                         ft.icons.ARROW_DOWNWARD if self.sort_column_index == 3 and not self.sort_ascending else None,
                                    size=16,
                                    color=ft.colors.PRIMARY if self.sort_column_index == 3 else ft.colors.TRANSPARENT
                                )
                            ], spacing=5),
                            on_click=lambda _: self.manual_sort(3)
                        )
                    ),
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Stock", color=ft.colors.ON_SURFACE),
                                ft.Icon(
                                    name=ft.icons.ARROW_UPWARD if self.sort_column_index == 4 and self.sort_ascending else
                                         ft.icons.ARROW_DOWNWARD if self.sort_column_index == 4 and not self.sort_ascending else None,
                                    size=16,
                                    color=ft.colors.PRIMARY if self.sort_column_index == 4 else ft.colors.TRANSPARENT
                                )
                            ], spacing=5),
                            on_click=lambda _: self.manual_sort(4)
                        )
                    ),
                    ft.DataColumn(
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Precio", color=ft.colors.ON_SURFACE),
                                ft.Icon(
                                    name=ft.icons.ARROW_UPWARD if self.sort_column_index == 5 and self.sort_ascending else
                                         ft.icons.ARROW_DOWNWARD if self.sort_column_index == 5 and not self.sort_ascending else None,
                                    size=16,
                                    color=ft.colors.PRIMARY if self.sort_column_index == 5 else ft.colors.TRANSPARENT
                                )
                            ], spacing=5),
                            on_click=lambda _: self.manual_sort(5)
                        )
                    ),
                    ft.DataColumn(ft.Text("Estado", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Acciones", color=ft.colors.ON_SURFACE)),
                ],
                rows=[],
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                heading_row_height=50,
                data_row_min_height=50,
                column_spacing=10,
                heading_row_color=ft.colors.with_opacity(0.05, ft.colors.PRIMARY),
                show_checkbox_column=False,
            )
        except Exception as e:
            logging.error(f"Error construyendo tabla de inventario: {str(e)}")
            return ft.Text("Error al cargar la tabla de inventario", color=ft.colors.ERROR)
            
    def load_inventory(self, e=None):
        """Carga los productos en la tabla de inventario"""
        try:
            # Obtener todos los productos
            self.all_products = self.product_service.get_all_products()
            
            # Inicializar productos filtrados con todos los productos
            self.filtered_products = self.all_products.copy()
            
            # Aplicar ordenamiento actual
            self.sort_products()
            
            # Volver a la primera página cuando se cargan nuevos datos
            self.current_page = 1
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.inventory_table = self.build_inventory_table()
            self.table_container.content = self.inventory_table
            
            # Actualizar la tabla con los productos de la página actual
            self.update_table_with_products(self.get_current_page_products())
            
            # Limpiar campo de búsqueda
            if e is not None:  # Solo si se llama desde el botón de actualizar
                self.search_field.value = ""
                self.update()
            
            # Depurar estructura de controles de paginación
            self.debug_pagination_controls()
            
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
        
    def get_total_pages(self):
        """Calcula el número total de páginas"""
        if not self.filtered_products:
            return 1
        return max(1, (len(self.filtered_products) + self.items_per_page - 1) // self.items_per_page)
        
    def go_to_page(self, page_number):
        """Navega a la página especificada"""
        try:
            logging.info(f"Intentando ir a la página {page_number}")
            total_pages = self.get_total_pages()
            logging.info(f"Total de páginas: {total_pages}")
            
            # Validar que la página sea válida
            if page_number < 1:
                page_number = 1
                logging.info("Ajustando a página 1 (mínimo)")
            elif page_number > total_pages:
                page_number = total_pages
                logging.info(f"Ajustando a página {total_pages} (máximo)")
                
            # Actualizar página actual
            self.current_page = page_number
            logging.info(f"Página actual establecida a: {self.current_page}")
            
            # Actualizar texto de información de página
            self.page_info_text.value = f"Página {self.current_page} de {total_pages}"
            self.total_products_text.value = f"Total: {len(self.filtered_products)} productos"
            
            # Actualizar estado de los botones de paginación
            self.btn_first_page.disabled = self.current_page == 1
            self.btn_prev_page.disabled = self.current_page == 1
            self.btn_next_page.disabled = self.current_page == total_pages
            self.btn_last_page.disabled = self.current_page == total_pages
            
            logging.info("Obteniendo productos para la página actual")
            current_page_products = self.get_current_page_products()
            logging.info(f"Productos en la página actual: {len(current_page_products)}")
            
            # Actualizar tabla con los productos de la página actual
            self.update_table_with_products(current_page_products)
            
            # Forzar actualización de la UI
            self.update()
            logging.info(f"Navegación a página {page_number} completada")
            
        except Exception as e:
            logging.error(f"Error al cambiar de página: {str(e)}")
            show_error_message(self.page, f"Error al cambiar de página: {str(e)}")
            
    def get_current_page_products(self):
        """Obtiene los productos de la página actual"""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return self.filtered_products[start_index:end_index]
        
    def go_to_first_page(self, e):
        """Ir a la primera página"""
        logging.info("Botón Primera Página presionado")
        self.go_to_page(1)
        
    def go_to_prev_page(self, e):
        """Ir a la página anterior"""
        logging.info(f"Botón Página Anterior presionado (actual: {self.current_page})")
        self.go_to_page(self.current_page - 1)
        
    def go_to_next_page(self, e):
        """Ir a la página siguiente"""
        logging.info(f"Botón Página Siguiente presionado (actual: {self.current_page})")
        self.go_to_page(self.current_page + 1)
        
    def go_to_last_page(self, e):
        """Ir a la última página"""
        total_pages = self.get_total_pages()
        logging.info(f"Botón Última Página presionado (total: {total_pages})")
        self.go_to_page(total_pages)
        
    def debug_pagination_controls(self):
        """Depura la estructura de los controles de paginación"""
        try:
            logging.info("=== Depuración de controles de paginación ===")
            logging.info(f"Página actual: {self.current_page}")
            logging.info(f"Total de páginas: {self.get_total_pages()}")
            logging.info(f"Total de productos: {len(self.filtered_products)}")
            
            # Verificar botones
            logging.info("Botón Primera Página: " + ("Deshabilitado" if self.btn_first_page.disabled else "Habilitado"))
            logging.info("Botón Página Anterior: " + ("Deshabilitado" if self.btn_prev_page.disabled else "Habilitado"))
            logging.info("Botón Página Siguiente: " + ("Deshabilitado" if self.btn_next_page.disabled else "Habilitado"))
            logging.info("Botón Última Página: " + ("Deshabilitado" if self.btn_last_page.disabled else "Habilitado"))
                
            logging.info("=== Fin de depuración ===")
        except Exception as e:
            logging.error(f"Error al depurar controles de paginación: {str(e)}") 