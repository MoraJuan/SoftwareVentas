import flet as ft
import csv
from io import StringIO
from sqlalchemy.orm import Session
from services.customerService import CustomerService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class PageCustomer(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_compradores", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Compradores"
        self.customer_service = CustomerService(session)
        self.all_customers = []
        self.current_page = 1
        self.customers_per_page = 10
        self.sort_column = None
        self.sort_reverse = False
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
                on_change=self.filter_customers
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

            # Tabla de clientes
            self.customer_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID"), on_sort=self.sort_customers),
                    ft.DataColumn(ft.Text("Nombre"), on_sort=self.sort_customers),
                    ft.DataColumn(ft.Text("Email"), on_sort=self.sort_customers),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=[]
            )

            # Botón para agregar cliente
            self.add_button = ft.ElevatedButton(
                "Agregar Cliente",
                on_click=lambda e: self.page.go("/agregar_comprador")
            )

            self.load_customers()

            # Diseño del contenido
            content = ft.Column([
                self.header,
                ft.Row([
                    self.search_field,
                    self.export_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.progress_bar,
                self.add_button,
                ft.Divider(height=20), 
                self.customer_table,
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

            # Cargar clientes al iniciar la página
            self.load_customers()

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

    def filter_customers(self, e):
        """Filtrar clientes según el texto de búsqueda"""
        search_term = self.search_field.value.lower()
        filtered = [
            customer for customer in self.all_customers
            if search_term in customer.name.lower() or search_term in customer.email.lower()
        ]
        self.update_table(filtered)
        self.update()

    def export_to_csv(self, e):
        """Exportar la lista de clientes a un archivo CSV"""
        try:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Nombre", "Email"])
            for customer in self.all_customers:
                writer.writerow([customer.id, customer.name, customer.email])
            csv_data = output.getvalue()
            # Codificar datos CSV para URL
            csv_url = f"data:text/csv;charset=utf-8,{csv_data}"
            self.page.launch_url(csv_url)
            show_success_message(self.page, "Clientes exportados exitosamente.")
        except Exception as e:
            show_error_message(self.page, f"Error al exportar clientes: {str(e)}")

    def sort_customers(self, e):
        """Ordenar clientes según la columna clicada"""
        column = e.column_index
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        if column == 0:  # ID
            self.all_customers.sort(key=lambda c: c.id, reverse=self.sort_reverse)
        elif column == 1:  # Nombre
            self.all_customers.sort(key=lambda c: c.name.lower(), reverse=self.sort_reverse)
        elif column == 2:  # Email
            self.all_customers.sort(key=lambda c: c.email.lower(), reverse=self.sort_reverse)

        self.update_table(self.get_paginated_customers())

    def prev_page(self, e):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()

    def next_page(self, e):
        """Ir a la página siguiente"""
        total_pages = (len(self.all_customers) + self.customers_per_page - 1) // self.customers_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_pagination()

    def update_pagination(self):
        """Actualizar la tabla basada en la página actual"""
        paginated = self.get_paginated_customers()
        self.update_table(paginated)
        total_pages = (len(self.all_customers) + self.customers_per_page - 1) // self.customers_per_page
        self.page_info.value = f"Páginas: {self.current_page} de {total_pages}"
        self.page_info.update()

    def get_paginated_customers(self):
        """Obtener clientes para la página actual"""
        start = (self.current_page - 1) * self.customers_per_page
        end = start + self.customers_per_page
        return self.all_customers[start:end]

    def update_table(self, customers):
        """Actualizar la tabla de clientes con la lista proporcionada"""
        self.customer_table.rows.clear()
        for customer in customers:
            self.add_customer_to_table(customer)
        self.customer_table.update()

    def add_customer_to_table(self, customer):
        """Método auxiliar para agregar un cliente a la tabla"""
        self.customer_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(customer.id))),
                    ft.DataCell(ft.Text(customer.name)),
                    ft.DataCell(ft.Text(customer.email)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                tooltip="Ver Detalles",
                                on_click=lambda e, c=customer: self.view_customer(c)
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, c=customer: self.edit_customer(c)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda e, c=customer: self.delete_customer(c)
                            ),
                        ])
                    ),
                ]
            )
        )

    def view_customer(self, customer):
        """Ver información detallada de un cliente"""
        try:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles del Cliente: {customer.name}"),
                content=ft.Column([
                    ft.Text(f"ID: {customer.id}"),
                    ft.Text(f"Nombre: {customer.name}"),
                    ft.Text(f"Email: {customer.email}"),
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
            show_error_message(self.page, f"Error al ver detalles del cliente: {str(e)}")

    def edit_customer(self, customer):
        """Navegar a la página de edición de cliente"""
        try:
            self.page.client_storage.set("edit_customer_id", customer.id)
            self.page.go("/editar_comprador")
        except Exception as e:
            show_error_message(self.page, f"Error al editar el comprador: {str(e)}")

    def delete_customer(self, customer):
        """Mostrar diálogo de confirmación antes de eliminar"""
        try:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Eliminación"),
                content=ft.Text(f"¿Está seguro que desea eliminar al cliente {customer.name}?"),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: self.close_dialog()
                    ),
                    ft.TextButton(
                        "Eliminar",
                        on_click=lambda e: self.confirm_delete_customer(customer)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error al mostrar diálogo de confirmación: {str(e)}")

    def confirm_delete_customer(self, customer):
        """Eliminar el cliente después de la confirmación"""
        try:
            self.customer_service.delete_customer(customer.id)
            show_success_message(self.page, "Cliente eliminado exitosamente.")
            self.load_customers()
            self.close_dialog()
        except Exception as e:
            show_error_message(self.page, f"Error al eliminar el cliente: {str(e)}")

    def close_dialog(self):
        """Cerrar el diálogo actualmente abierto"""
        self.page.dialog.open = False
        self.page.update()

    def load_customers(self):
        """Cargar clientes con indicación de progreso"""
        try:
            self.progress_bar.visible = True
            self.update()

            self.all_customers = self.customer_service.get_all_customers()
            self.current_page = 1
            self.update_pagination()
        except Exception as e:
            show_error_message(self.page, f"Error al cargar los clientes: {str(e)}")
        finally:
            self.progress_bar.visible = False
            self.update()