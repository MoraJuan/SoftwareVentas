import flet as ft
from sqlalchemy.orm import Session
from services.customerService import CustomerService
from ui.components.data_table import DataTable
from ui.components.alerts import show_success_message, show_error_message
from ui.components.navigation import create_navigation_rail, get_route_for_index


class PageCustomer(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_compradores", controls=[], padding=0)
        self.page = page
        self.session = session
        self.page.title = "Lista de Compradores"
        self.customer_service = CustomerService(session)
        self.build_ui()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            0, self.handle_navigation)

        self.customer_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        self.add_button = ft.ElevatedButton(
            "Agregar Comprador",
            on_click=lambda e: self.page.go("/agregar_comprador")
        )

        self.controls = [
            ft.Container(
                content=ft.Row([
                    self.navigation_rail,
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Compradores",
                                        weight=ft.FontWeight.BOLD, size=20),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            self.add_button,
                            self.customer_table
                        ],
                            spacing=20,
                            scroll=ft.ScrollMode.AUTO
                        ),
                        expand=True,
                        padding=20
                    )
                ]),
                expand=True,
            )]

        self.load_customers()

    def load_customers(self):
        try:
            customers = self.customer_service.get_all_customers()
            self.customer_table.rows.clear()
            for customer in customers:
                self.customer_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(customer.id))),
                            ft.DataCell(ft.Text(customer.name)),
                            ft.DataCell(ft.Text(customer.email)),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda e, c=customer: self.on_edit_customer(
                                            c)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda e, c=customer: self.on_delete_customer(
                                            c)
                                    ),
                                ])
                            ),
                        ]
                    )
                )
            self.update()  # Update the view to reflect the new data
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los compradores: {str(e)}")

    def on_edit_customer(self, customer):
        try:
            self.page.client_storage.set("edit_customer_id", customer.id)
            self.page.go("/editar_comprador")
        except Exception as e:
            show_error_message(
                self.page, f"Error al editar el comprador: {str(e)}")

    def on_delete_customer(self, customer):
        try:
            self.customer_service.delete_customer(customer.id)
            show_success_message(self.page, "Comprador eliminado exitosamente")
            self.load_customers()
        except Exception as e:
            show_error_message(
                self.page, f"Error al eliminar el comprador: {str(e)}")

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")
