import flet as ft
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from services.supplierService import SupplierService
import logging

class PageSuppliers(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/ver_proveedores",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.supplier_service = SupplierService(session)
        self.all_suppliers = []  # Lista para almacenar todos los proveedores
        self.filtered_suppliers = []  # Lista para almacenar proveedores filtrados
        self.sort_column_index = 1  # Por defecto ordenar por nombre (índice 1)
        self.sort_ascending = True  # Por defecto orden ascendente
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(4, self.page)

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Gestión de Proveedores", 
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
                label="Buscar proveedores",
                prefix_icon=ft.icons.SEARCH,
                expand=True,
                border_radius=20,
                on_change=self.filter_suppliers,
                hint_text="Ingrese el nombre del proveedor...",
                height=50
            )

            # Crear tabla de proveedores
            self.suppliers_table = self.build_suppliers_table()
            
            # Contenedor para la tabla que se actualizará
            self.table_container = ft.Container(
                content=self.suppliers_table,
                expand=True
            )
            
            # Cargar datos iniciales
            self.load_suppliers()

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton(
                                "Nuevo Proveedor",
                                icon=ft.icons.PERSON_ADD,
                                on_click=lambda _: self.page.go("/agregar_proveedor"),
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_PRIMARY,
                                    bgcolor=ft.colors.PRIMARY
                                )
                            ),
                            ft.ElevatedButton(
                                "Actualizar Datos",
                                icon=ft.icons.REFRESH,
                                on_click=self.load_suppliers,
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
                            "Lista de Proveedores",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.table_container
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

    def build_suppliers_table(self):
        try:
            # Crear tabla de proveedores con encabezados clicables para ordenamiento
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
                                ft.Text("Nombre", color=ft.colors.ON_SURFACE),
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
                                ft.Text("Teléfono", color=ft.colors.ON_SURFACE),
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
                                ft.Text("Email", color=ft.colors.ON_SURFACE),
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
                                ft.Text("Dirección", color=ft.colors.ON_SURFACE),
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
            logging.error(f"Error construyendo tabla de proveedores: {str(e)}")
            return ft.Text("Error al cargar la tabla de proveedores", color=ft.colors.ERROR)
            
    def filter_suppliers(self, e):
        """Filtra los proveedores según el texto de búsqueda"""
        try:
            search_text = self.search_field.value.lower()
            
            if not search_text:
                # Si no hay texto de búsqueda, mostrar todos los proveedores
                self.filtered_suppliers = self.all_suppliers.copy()
            else:
                # Filtrar proveedores que contengan el texto de búsqueda en el nombre o email
                self.filtered_suppliers = [
                    supplier for supplier in self.all_suppliers 
                    if search_text in supplier.name.lower() or 
                       (supplier.email and search_text in supplier.email.lower())
                ]
            
            # Aplicar ordenamiento actual a los proveedores filtrados
            self.sort_suppliers()
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.suppliers_table = self.build_suppliers_table()
            self.table_container.content = self.suppliers_table
            
            # Actualizar la tabla con los proveedores filtrados
            self.update_table_with_suppliers(self.filtered_suppliers)
                
        except Exception as e:
            logging.error(f"Error al filtrar proveedores: {str(e)}")
            show_error_message(self.page, f"Error al filtrar proveedores: {str(e)}")
    
    def sort_suppliers(self):
        """Ordena los proveedores según la columna seleccionada"""
        try:
            # Definir la función de ordenamiento según el índice de columna
            if self.sort_column_index == 0:  # ID
                key_func = lambda s: s.id
            elif self.sort_column_index == 1:  # Nombre
                key_func = lambda s: s.name.lower()
            elif self.sort_column_index == 2:  # Teléfono
                key_func = lambda s: (s.phone or "").lower()
            elif self.sort_column_index == 3:  # Email
                key_func = lambda s: (s.email or "").lower()
            elif self.sort_column_index == 4:  # Dirección
                key_func = lambda s: (s.address or "").lower()
            else:
                # Por defecto ordenar por nombre
                key_func = lambda s: s.name.lower()
            
            # Ordenar la lista de proveedores
            self.filtered_suppliers.sort(key=key_func, reverse=not self.sort_ascending)
            
        except Exception as e:
            logging.error(f"Error al ordenar proveedores: {str(e)}")
            show_error_message(self.page, f"Error al ordenar proveedores: {str(e)}")
    
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
            
            # Ordenar proveedores
            self.sort_suppliers()
            
            # Crear una nueva tabla con los iconos de ordenamiento actualizados
            self.suppliers_table = self.build_suppliers_table()
            
            # Actualizar el contenedor de la tabla
            self.table_container.content = self.suppliers_table
            
            # Actualizar la tabla con los proveedores filtrados
            self.update_table_with_suppliers(self.filtered_suppliers)
            
            # Actualizar la UI
            self.update()
            
        except Exception as e:
            logging.error(f"Error al manejar ordenamiento manual: {str(e)}")
            show_error_message(self.page, f"Error al ordenar tabla: {str(e)}")
            
    def update_table_with_suppliers(self, suppliers):
        """Actualiza la tabla con los proveedores proporcionados"""
        try:
            # Crear filas para la tabla
            rows = []
            for supplier in suppliers:
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(supplier.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.phone or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.email or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.address or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Ver Detalles",
                                    on_click=lambda e, s=supplier: self.view_supplier(s)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Editar",
                                    on_click=lambda e, s=supplier: self.edit_supplier(s)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.ERROR,
                                    tooltip="Eliminar",
                                    on_click=lambda e, s=supplier: self.delete_supplier(s)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.suppliers_table.rows = rows
            
            # Mostrar mensaje si no hay resultados
            if not rows:
                if self.search_field.value:
                    show_error_message(self.page, f"No se encontraron proveedores que coincidan con '{self.search_field.value}'")
                else:
                    show_error_message(self.page, "No se encontraron proveedores")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al actualizar tabla: {str(e)}")
            show_error_message(self.page, f"Error al actualizar tabla: {str(e)}")
            
    def load_suppliers(self, e=None):
        """Carga los proveedores en la tabla"""
        try:
            # Obtener todos los proveedores
            self.all_suppliers = self.supplier_service.get_all_suppliers()
            
            # Inicializar proveedores filtrados con todos los proveedores
            self.filtered_suppliers = self.all_suppliers.copy()
            
            # Aplicar ordenamiento actual
            self.sort_suppliers()
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.suppliers_table = self.build_suppliers_table()
            self.table_container.content = self.suppliers_table
            
            # Actualizar la tabla con los proveedores
            self.update_table_with_suppliers(self.filtered_suppliers)
            
            # Limpiar campo de búsqueda
            if e is not None:  # Solo si se llama desde el botón de actualizar
                self.search_field.value = ""
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar proveedores: {str(e)}")
            show_error_message(self.page, f"Error al cargar proveedores: {str(e)}")
            
    def view_supplier(self, supplier):
        """Ver información detallada de un proveedor"""
        try:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles del Proveedor: {supplier.name}"),
                content=ft.Column([
                    ft.Text(f"ID: {supplier.id}"),
                    ft.Text(f"Nombre: {supplier.name}"),
                    ft.Text(f"Email: {supplier.email or 'No disponible'}"),
                    ft.Text(f"Teléfono: {supplier.phone or 'No disponible'}"),
                    ft.Text(f"Dirección: {supplier.address or 'No disponible'}"),
                    ft.Text(f"Descripción: {supplier.description or 'No disponible'}"),
                ]),
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda e: self.close_dialog()
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logging.error(f"Error al ver detalles del proveedor: {str(e)}")
            show_error_message(self.page, f"Error al ver detalles del proveedor: {str(e)}")
            
    def edit_supplier(self, supplier):
        """Navega a la página de edición de proveedor"""
        try:
            self.page.client_storage.set("edit_supplier_id", supplier.id)
            self.page.go("/editar_proveedor")
        except Exception as e:
            logging.error(f"Error al editar proveedor: {str(e)}")
            show_error_message(self.page, f"Error al editar proveedor: {str(e)}")
        
    def delete_supplier(self, supplier):
        """Elimina un proveedor"""
        try:
            # Confirmar eliminación
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"¿Eliminar proveedor {supplier.name}?"),
                content=ft.Text("Esta acción no se puede deshacer."),
                actions=[
                    ft.TextButton("Cancelar", on_click=self.close_dialog),
                    ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_supplier(supplier)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logging.error(f"Error al eliminar proveedor: {str(e)}")
            show_error_message(self.page, f"Error al eliminar proveedor: {str(e)}")
            
    def confirm_delete_supplier(self, supplier):
        """Confirma la eliminación de un proveedor"""
        try:
            # Eliminar proveedor
            self.supplier_service.delete_supplier(supplier.id)
            
            # Cerrar diálogo
            self.close_dialog()
            
            # Recargar proveedores
            self.load_suppliers()
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Proveedor {supplier.name} eliminado correctamente")
        except Exception as e:
            logging.error(f"Error al eliminar proveedor: {str(e)}")
            show_error_message(self.page, f"Error al eliminar proveedor: {str(e)}")
            
    def close_dialog(self, e=None):
        """Cierra el diálogo actual"""
        self.page.dialog.open = False
        self.page.update() 