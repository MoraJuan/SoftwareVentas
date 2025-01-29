import flet as ft
import csv
from io import StringIO
from sqlalchemy.orm import Session
from services.supplierService import SupplierService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class PageSupplier(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_proveedores", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Proveedores"
        self.supplier_service = SupplierService(session)
        self.all_suppliers = []
        self.current_page = 1
        self.suppliers_per_page = 10
        self.sort_column = None
        self.sort_reverse = False
        self.build_ui()

    def build_ui(self):
        try:
            # Barra de navegación lateral
            self.navigation_rail = create_navigation_rail(
                2, self.handle_navigation)

            self.header = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        icon_color=ft.colors.BLUE,
                        tooltip="Volver a Reportes",
                        on_click=lambda _: self.page.go("/ver_reportes")
                    ),
                    ft.Text(
                        "Proveedores ",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                ],
                alignment=ft.MainAxisAlignment.START
            )

            # Campo de búsqueda
            self.search_field = ft.TextField(
                label="Buscar proveedor",
                width=300,
                prefix_icon=ft.icons.SEARCH,
                on_change=self.filter_suppliers
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

            # Tabla de proveedores
            self.supplier_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID"), on_sort=self.sort_suppliers),
                    ft.DataColumn(ft.Text("Nombre"),
                                  on_sort=self.sort_suppliers),
                    ft.DataColumn(ft.Text("Email"),
                                  on_sort=self.sort_suppliers),
                    ft.DataColumn(ft.Text("Teléfono"),
                                  on_sort=self.sort_suppliers),
                    ft.DataColumn(ft.Text("Dirección"),
                                  on_sort=self.sort_suppliers),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=[]
            )

            # Botón para agregar proveedor
            self.add_button = ft.ElevatedButton(
                "Agregar Proveedor",
                on_click=lambda e: self.page.go("/agregar_proveedor")
            )

            self.load_suppliers()

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
                self.supplier_table,
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

    def filter_suppliers(self, e):
        """Filtrar proveedores según el texto de búsqueda"""
        search_term = self.search_field.value.lower()
        filtered = [
            supplier for supplier in self.all_suppliers
            if search_term in supplier.name.lower() or search_term in supplier.email.lower()
        ]
        self.update_table(filtered)
        self.update()

    def export_to_csv(self, e):
        """Exportar la lista de proveedores a un archivo CSV"""
        try:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Nombre", "Email", "Teléfono", "Dirección"])
            for supplier in self.all_suppliers:
                writer.writerow(
                    [supplier.id, supplier.name, supplier.email, supplier.phone, supplier.address])
            csv_data = output.getvalue()
            # Codificar datos CSV para URL
            csv_url = f"data:text/csv;charset=utf-8,{csv_data}"
            self.page.launch_url(csv_url)
            show_success_message(
                self.page, "Proveedores exportados exitosamente.")
        except Exception as e:
            show_error_message(
                self.page, f"Error al exportar proveedores: {str(e)}")

    def sort_suppliers(self, e):
        """Ordenar proveedores según la columna clicada"""
        column = e.column_index
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        if column == 0:  # ID
            self.all_suppliers.sort(
                key=lambda s: s.id, reverse=self.sort_reverse)
        elif column == 1:  # Nombre
            self.all_suppliers.sort(
                key=lambda s: s.name.lower(), reverse=self.sort_reverse)
        elif column == 2:  # Email
            self.all_suppliers.sort(
                key=lambda s: s.email.lower(), reverse=self.sort_reverse)
        elif column == 3:  # Teléfono
            self.all_suppliers.sort(
                key=lambda s: s.phone, reverse=self.sort_reverse)
        elif column == 4:  # Dirección
            self.all_suppliers.sort(
                key=lambda s: s.address.lower(), reverse=self.sort_reverse)

        self.update_table(self.get_paginated_suppliers())

    def prev_page(self, e):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()

    def next_page(self, e):
        """Ir a la página siguiente"""
        total_pages = (len(self.all_suppliers) +
                       self.suppliers_per_page - 1) // self.suppliers_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_pagination()

    def update_pagination(self):
        """Actualizar la tabla basada en la página actual"""
        paginated = self.get_paginated_suppliers()
        self.update_table(paginated)
        total_pages = (len(self.all_suppliers) +
                       self.suppliers_per_page - 1) // self.suppliers_per_page
        self.page_info.value = f"Páginas: {self.current_page} de {total_pages}"
        self.page_info.update()

    def get_paginated_suppliers(self):
        """Obtener proveedores para la página actual"""
        start = (self.current_page - 1) * self.suppliers_per_page
        end = start + self.suppliers_per_page
        return self.all_suppliers[start:end]

    def update_table(self, suppliers):
        """Actualizar la tabla de proveedores con la lista proporcionada"""
        self.supplier_table.rows.clear()
        for supplier in suppliers:
            self.add_supplier_to_table(supplier)
        self.supplier_table.update()

    def add_supplier_to_table(self, supplier):
        """Método auxiliar para agregar un proveedor a la tabla"""
        self.supplier_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(supplier.id))),
                    ft.DataCell(ft.Text(supplier.name)),
                    ft.DataCell(ft.Text(supplier.email)),
                    ft.DataCell(ft.Text(supplier.phone)),
                    ft.DataCell(ft.Text(supplier.address)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                tooltip="Ver Detalles",
                                on_click=lambda e, s=supplier: self.view_supplier(
                                    s)
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, s=supplier: self.edit_supplier(
                                    s)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda e, s=supplier: self.delete_supplier(
                                    s)
                            ),
                        ])
                    ),
                ]
            )
        )

    def view_supplier(self, supplier):
        """Ver información detallada de un proveedor"""
        try:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles del Proveedor: {supplier.name}"),
                content=ft.Column([
                    ft.Text(f"ID: {supplier.id}"),
                    ft.Text(f"Nombre: {supplier.name}"),
                    ft.Text(f"Email: {supplier.email}"),
                    ft.Text(f"Teléfono: {supplier.phone}"),
                    ft.Text(f"Dirección: {supplier.address}"),
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
            show_error_message(
                self.page, f"Error al ver detalles del proveedor: {str(e)}")

    def edit_supplier(self, supplier):
        """Navegar a la página de edición de proveedor"""
        try:
            self.page.go(f"/editar_proveedor/{supplier.id}")
        except Exception as e:
            show_error_message(
                self.page, f"Error al editar proveedor: {str(e)}")

    def delete_supplier(self, supplier):
        """Eliminar un proveedor"""
        try:
            self.supplier_service.delete_supplier(supplier.id)
            show_success_message(self.page, f"Proveedor {
                                 supplier.name} eliminado.")
            self.load_suppliers()  # Recargar la lista
        except Exception as e:
            show_error_message(
                self.page, f"Error al eliminar proveedor: {str(e)}")

    def load_suppliers(self):
        """Cargar los proveedores desde el servicio"""
        try:
            self.all_suppliers = self.supplier_service.get_all_suppliers()
            self.update_pagination()
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar proveedores: {str(e)}")
