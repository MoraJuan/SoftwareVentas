import flet as ft
import csv
from io import StringIO
from sqlalchemy.orm import Session
from services.customerService import CustomerService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index
import logging


class PageCustomer(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_compradores", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Clientes"
        self.customer_service = CustomerService(session)
        self.all_customers = []  # Lista para almacenar todos los clientes
        self.filtered_customers = []  # Lista para almacenar clientes filtrados
        self.sort_column_index = 1  # Por defecto ordenar por nombre (índice 1)
        self.sort_ascending = True  # Por defecto orden ascendente
        self.current_page = 1
        self.customers_per_page = 10
        self.build_ui()

    def build_ui(self):
        try:
            # Inicializar controles
            self.navigation_rail = create_navigation_rail(2, self.handle_navigation)
            self.header = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    icon_color=ft.colors.BLUE,
                    tooltip="Volver a Reportes",
                    on_click=lambda _: self.page.go("/ver_reportes")
                ),
                ft.Text(
                    "Clientes",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
            ],
            alignment=ft.MainAxisAlignment.START
            )

            # Campo de búsqueda
            self.search_field = ft.TextField(
                label="Buscar cliente",
                width=300,
                prefix_icon=ft.icons.SEARCH,
                on_change=self.filter_customers,
                hint_text="Ingrese el nombre del cliente...",
                border_radius=20,
                height=50
            )

            # Botón de exportar a CSV
            self.export_button = ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                tooltip="Exportar a CSV",
                on_click=self.export_to_csv
            )

            # Crear tabla de clientes
            self.customer_table = self.build_customer_table()
            
            # Contenedor para la tabla que se actualizará
            self.table_container = ft.Container(
                content=self.customer_table,
                expand=True
            )

            # Crear botones de paginación
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
            
            self.total_customers_text = ft.Text(
                f"Total: {len(self.filtered_customers)} clientes",
                color=ft.colors.ON_SURFACE_VARIANT,
                size=12
            )
            
            # Crear fila de paginación
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
            
            # Crear contenedor para el contador de clientes
            customers_counter = ft.Container(
                content=self.total_customers_text,
                alignment=ft.alignment.center
            )
            
            # Contenedor de paginación
            self.pagination_container = ft.Container(
                content=ft.Column([
                    pagination_row,
                    customers_counter
                ]),
                margin=ft.margin.only(top=20)
            )

            # Botón para agregar cliente
            self.add_button = ft.ElevatedButton(
                "Agregar Cliente",
                icon=ft.icons.PERSON_ADD,
                on_click=lambda e: self.page.go("/agregar_comprador"),
                style=ft.ButtonStyle(
                    color=ft.colors.ON_PRIMARY,
                    bgcolor=ft.colors.PRIMARY
                )
            )

            # Barra de progreso
            self.progress_bar = ft.ProgressBar(visible=False)

            # Cargar datos iniciales
            self.load_customers()

            # Diseño del contenido
            content = ft.Column([
                self.header,
                ft.Row([
                    self.search_field,
                    self.export_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.progress_bar,
                ft.Row([
                    self.add_button,
                    ft.ElevatedButton(
                        "Actualizar Datos",
                        icon=ft.icons.REFRESH,
                        on_click=self.load_customers,
                        style=ft.ButtonStyle(
                            color=ft.colors.ON_SURFACE,
                            bgcolor=ft.colors.SURFACE_VARIANT
                        )
                    )
                ], spacing=10),
                ft.Divider(height=20), 
                self.table_container,
                self.pagination_container
            ], spacing=20)

            # Configuración principal de controles
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

        except Exception as e:
            logging.error(f"Error construyendo UI: {str(e)}")
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def build_customer_table(self):
        """Construye la tabla de clientes con encabezados clicables para ordenamiento"""
        try:
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
                                ft.Text("Email", color=ft.colors.ON_SURFACE),
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
                                ft.Text("Teléfono", color=ft.colors.ON_SURFACE),
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
            logging.error(f"Error construyendo tabla de clientes: {str(e)}")
            return ft.Text("Error al cargar la tabla de clientes", color=ft.colors.ERROR)

    def handle_navigation(self, e):
        """Manejar eventos de navegación"""
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
            self.page.update()
        except Exception as e:
            logging.error(f"Error de navegación: {str(e)}")
            show_error_message(self.page, f"Error de navegación: {str(e)}")

    def filter_customers(self, e):
        """Filtra los clientes según el texto de búsqueda"""
        try:
            search_text = self.search_field.value.lower()
            
            if not search_text:
                # Si no hay texto de búsqueda, mostrar todos los clientes
                self.filtered_customers = self.all_customers.copy()
            else:
                # Filtrar clientes que contengan el texto de búsqueda en el nombre o email
                self.filtered_customers = [
                    customer for customer in self.all_customers 
                    if search_text in customer.name.lower() or 
                       (customer.email and search_text in customer.email.lower())
                ]
            
            # Aplicar ordenamiento actual a los clientes filtrados
            self.sort_customers_by_column()
            
            # Volver a la primera página cuando se filtra
            self.current_page = 1
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.customer_table = self.build_customer_table()
            self.table_container.content = self.customer_table
            
            # Actualizar la tabla con los clientes de la página actual
            self.update_table_with_customers(self.get_current_page_customers())
                
        except Exception as e:
            logging.error(f"Error al filtrar clientes: {str(e)}")
            show_error_message(self.page, f"Error al filtrar clientes: {str(e)}")

    def export_to_csv(self, e):
        """Exportar la lista de clientes a un archivo CSV"""
        try:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Nombre", "Email", "Teléfono", "Dirección"])
            for customer in self.all_customers:
                writer.writerow([customer.id, customer.name, customer.email])
            csv_data = output.getvalue()
            # Codificar datos CSV para URL
            csv_url = f"data:text/csv;charset=utf-8,{csv_data}"
            self.page.launch_url(csv_url)
            show_success_message(self.page, "Clientes exportados exitosamente.")
        except Exception as e:
            logging.error(f"Error al exportar clientes: {str(e)}")
            show_error_message(self.page, f"Error al exportar clientes: {str(e)}")

    def sort_customers_by_column(self):
        """Ordena los clientes según la columna seleccionada"""
        try:
            # Definir la función de ordenamiento según el índice de columna
            if self.sort_column_index == 0:  # ID
                key_func = lambda c: c.id
            elif self.sort_column_index == 1:  # Nombre
                key_func = lambda c: c.name.lower()
            elif self.sort_column_index == 2:  # Email
                key_func = lambda c: (c.email or "").lower()
            else:
                # Por defecto ordenar por nombre
                key_func = lambda c: c.name.lower()
            
            # Ordenar la lista de clientes
            self.filtered_customers.sort(key=key_func, reverse=not self.sort_ascending)
            
        except Exception as e:
            logging.error(f"Error al ordenar clientes: {str(e)}")
            show_error_message(self.page, f"Error al ordenar clientes: {str(e)}")
    
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
            
            # Ordenar clientes
            self.sort_customers_by_column()
            
            # Crear una nueva tabla con los iconos de ordenamiento actualizados
            self.customer_table = self.build_customer_table()
            
            # Actualizar el contenedor de la tabla
            self.table_container.content = self.customer_table
            
            # Actualizar la tabla con los clientes de la página actual
            self.update_table_with_customers(self.get_current_page_customers())
            
            # Actualizar la UI
            self.update()
            
        except Exception as e:
            logging.error(f"Error al manejar ordenamiento manual: {str(e)}")
            show_error_message(self.page, f"Error al ordenar tabla: {str(e)}")

    def go_to_first_page(self, e):
        """Ir a la primera página"""
        self.go_to_page(1)
        
    def go_to_prev_page(self, e):
        """Ir a la página anterior"""
        self.go_to_page(self.current_page - 1)
        
    def go_to_next_page(self, e):
        """Ir a la página siguiente"""
        self.go_to_page(self.current_page + 1)
        
    def go_to_last_page(self, e):
        """Ir a la última página"""
        self.go_to_page(self.get_total_pages())
        
    def go_to_page(self, page_number):
        """Navega a la página especificada"""
        try:
            total_pages = self.get_total_pages()
            
            # Validar que la página sea válida
            if page_number < 1:
                page_number = 1
            elif page_number > total_pages:
                page_number = total_pages
                
            # Actualizar página actual
            self.current_page = page_number
            
            # Actualizar texto de información de página
            self.page_info_text.value = f"Página {self.current_page} de {total_pages}"
            self.total_customers_text.value = f"Total: {len(self.filtered_customers)} clientes"
            
            # Actualizar estado de los botones de paginación
            self.btn_first_page.disabled = self.current_page == 1
            self.btn_prev_page.disabled = self.current_page == 1
            self.btn_next_page.disabled = self.current_page == total_pages
            self.btn_last_page.disabled = self.current_page == total_pages
            
            # Actualizar tabla con los clientes de la página actual
            self.update_table_with_customers(self.get_current_page_customers())
            
            # Forzar actualización de la UI
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cambiar de página: {str(e)}")
            show_error_message(self.page, f"Error al cambiar de página: {str(e)}")

    def get_total_pages(self):
        """Calcula el número total de páginas"""
        if not self.filtered_customers:
            return 1
        return max(1, (len(self.filtered_customers) + self.customers_per_page - 1) // self.customers_per_page)
        
    def get_current_page_customers(self):
        """Obtiene los clientes de la página actual"""
        start_index = (self.current_page - 1) * self.customers_per_page
        end_index = start_index + self.customers_per_page
        return self.filtered_customers[start_index:end_index]

    def update_table_with_customers(self, customers):
        """Actualiza la tabla con los clientes proporcionados"""
        try:
            # Crear filas para la tabla
            rows = []
            for customer in customers:
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(customer.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(customer.name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(customer.email or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Ver Detalles",
                                    on_click=lambda e, c=customer: self.view_customer(c)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Editar",
                                    on_click=lambda e, c=customer: self.edit_customer(c)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.ERROR,
                                    tooltip="Eliminar",
                                    on_click=lambda e, c=customer: self.delete_customer(c)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.customer_table.rows = rows
            
            # Mostrar mensaje si no hay resultados
            if not rows:
                if self.search_field.value:
                    show_error_message(self.page, f"No se encontraron clientes que coincidan con '{self.search_field.value}'")
                else:
                    show_error_message(self.page, "No se encontraron clientes")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al actualizar tabla: {str(e)}")
            show_error_message(self.page, f"Error al actualizar tabla: {str(e)}")

    def view_customer(self, customer):
        """Ver información detallada de un cliente"""
        try:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles del Cliente: {customer.name}"),
                content=ft.Column([
                    ft.Text(f"ID: {customer.id}"),
                    ft.Text(f"Nombre: {customer.name}"),
                    ft.Text(f"Email: {customer.email or 'No disponible'}"),
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
            logging.error(f"Error al ver detalles del cliente: {str(e)}")
            show_error_message(self.page, f"Error al ver detalles del cliente: {str(e)}")

    def edit_customer(self, customer):
        """Navega a la página de edición de cliente"""
        try:
            self.page.client_storage.set("edit_customer_id", customer.id)
            self.page.go("/editar_comprador")
        except Exception as e:
            logging.error(f"Error al editar cliente: {str(e)}")
            show_error_message(self.page, f"Error al editar cliente: {str(e)}")

    def delete_customer(self, customer):
        """Elimina un cliente"""
        try:
            # Confirmar eliminación
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"¿Eliminar cliente {customer.name}?"),
                content=ft.Text("Esta acción no se puede deshacer."),
                actions=[
                    ft.TextButton("Cancelar", on_click=self.close_dialog),
                    ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_customer(customer)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logging.error(f"Error al eliminar cliente: {str(e)}")
            show_error_message(self.page, f"Error al eliminar cliente: {str(e)}")

    def confirm_delete_customer(self, customer):
        """Confirma la eliminación de un cliente"""
        try:
            # Eliminar cliente
            self.customer_service.delete_customer(customer.id)
            
            # Cerrar diálogo
            self.close_dialog()
            
            # Recargar clientes
            self.load_customers()
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Cliente {customer.name} eliminado correctamente")
        except Exception as e:
            logging.error(f"Error al eliminar cliente: {str(e)}")
            show_error_message(self.page, f"Error al eliminar cliente: {str(e)}")

    def close_dialog(self, e=None):
        """Cierra el diálogo actual"""
        self.page.dialog.open = False
        self.page.update()

    def load_customers(self, e=None):
        """Carga los clientes en la tabla"""
        try:
            # Obtener todos los clientes
            self.all_customers = self.customer_service.get_all_customers()
            
            # Inicializar clientes filtrados con todos los clientes
            self.filtered_customers = self.all_customers.copy()
            
            # Aplicar ordenamiento actual
            self.sort_customers_by_column()
            
            # Volver a la primera página cuando se cargan nuevos datos
            self.current_page = 1
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.customer_table = self.build_customer_table()
            self.table_container.content = self.customer_table
            
            # Actualizar la tabla con los clientes de la página actual
            self.update_table_with_customers(self.get_current_page_customers())
            
            # Limpiar campo de búsqueda
            if e is not None:  # Solo si se llama desde el botón de actualizar
                self.search_field.value = ""
                self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar clientes: {str(e)}")
            show_error_message(self.page, f"Error al cargar clientes: {str(e)}")