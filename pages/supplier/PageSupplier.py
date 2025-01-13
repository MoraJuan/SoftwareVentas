import flet as ft
from sqlalchemy.orm import Session
from services.supplierService import SupplierService
from ui.components.alerts import show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index

class PageSupplier(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_proveedores", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Proveedores"
        self.supplier_service = SupplierService(session)
        self.build_ui()

    def build_ui(self):
        # Barra de navegación lateral
        self.navigation_rail = create_navigation_rail(
            4, self.handle_navigation
        )

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

        # Botón para agregar un nuevo proveedor
        self.add_button = ft.ElevatedButton(
            "Agregar Proveedor",
            on_click=lambda e: self.page.go("/agregar_proveedor"),
            expand=False,
        )

        # Estructura principal de la vista
        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,  # Barra de navegación lateral
                    ft.Container(
                        padding=20,
                        expand=True,
                        content=ft.Column([
                            ft.Text("Proveedores", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                controls=[self.add_button],
                                alignment=ft.MainAxisAlignment.START,  # Alinear el botón al inicio
                                spacing=20,
                            ),
                            ft.Divider(height=20),  # Separador entre el botón y la tabla
                            self.supplier_table  # Tabla de proveedores
                        ], spacing=20)
                    )
                ]),
                expand=True
            )
        ]

        # Cargar datos iniciales
        self.load_suppliers()

    def load_suppliers(self):
        try:
            # Obtener lista de proveedores
            suppliers = self.supplier_service.get_all_suppliers()
            self.supplier_table.rows.clear()

            # Agregar filas a la tabla con datos de los proveedores
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
                                        on_click=lambda e, s=supplier: self.edit_supplier(s)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda e, s=supplier: self.delete_supplier(s)
                                    ),
                                ])
                            ),
                        ]
                    )
                )
            self.supplier_table.update()  # Actualizar la tabla
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los proveedores: {str(e)}"
            )

    def edit_supplier(self, supplier):
        try:
            self.page.client_storage.set("edit_supplier_id", supplier.id)
            self.page.go("/editar_proveedor")
        except Exception as e:
            show_error_message(
                self.page, f"Error al editar el proveedor: {str(e)}"
            )

    def delete_supplier(self, supplier):
        try:
            self.supplier_service.delete_supplier(supplier.id)
            self.load_suppliers()
        except Exception as e:
            show_error_message(
                self.page, f"Error al eliminar el proveedor: {str(e)}"
            )

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Error de navegación: {str(e)}")
