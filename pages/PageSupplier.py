import flet as ft
from sqlalchemy.orm import Session
from pages.dashboard.navigation import create_navigation_rail, get_route_for_index
from services.supplierService import SupplierService
from ui.components.alerts import show_success_message, show_error_message
from ui.components.data_table import DataTable


class PageSupplier(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_proveedores", controls=[], padding=20)
        self.page = page
        self.session = session
        self.page.title = "Lista de Proveedores"
        self.supplier_service = SupplierService(session)
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            0, self.handle_navigation)

        # Tabla de proveedores
        self.supplier_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        self.home_button = ft.IconButton(
            icon=ft.icons.HOME,
            tooltip="Volver al inicio",
            on_click=lambda e: self.page.go("/dashboard")
        )

        self.add_button = ft.ElevatedButton(
            "Agregar Proveedor",
            on_click=lambda e: self.page.go("/agregar_proveedor")
        )

        # Layout de la vista
        self.controls = [
            ft.Row([
                self.navigation_rail,
                ft.Column([
                    ft.Row([
                        ft.Text("Proveedores",
                                weight=ft.FontWeight.BOLD, size=20),
                    ]),
                    self.add_button,
                    self.supplier_table
                ])
            ])
        ]

        self.load_suppliers()

    def load_suppliers(self):
        try:
            suppliers = self.supplier_service.get_all_suppliers()
            self.supplier_table.rows.clear()
            for supplier in suppliers:
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
            self.update()  # Actualiza la vista después de modificar la tabla
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los proveedores: {str(e)}")

    def edit_supplier(self, supplier):
        try:
            self.page.client_storage.set("edit_supplier_id", supplier.id)
            self.page.go("/editar_proveedor")
        except Exception as e:
            show_error_message(
                self.page, f"Error al editar el proveedor: {str(e)}")

    def delete_supplier(self, supplier):
        try:
            self.supplier_service.delete_supplier(supplier.id)
            show_success_message(
                self.page, "Proveedor eliminado exitosamente.")
            self.load_suppliers()
        except Exception as e:
            show_error_message(
                self.page, f"Error al eliminar el proveedor: {str(e)}")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")
