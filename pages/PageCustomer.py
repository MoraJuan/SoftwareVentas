import flet as ft
from sqlalchemy.orm import Session
from services.customerService import CustomerService
from ui.components.data_table import DataTable
from ui.components.alerts import show_success_message, show_error_message

class PageCustomer(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(route="/ver_compradores", controls=[], padding=20)
        self.page = page
        self.session = session
        self.page.title = "Lista de Compradores"
        self.customer_service = CustomerService(session)
        self.build_ui()

    def build_ui(self):
        self.customer_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
            ],
            rows=[]
        )

        self.home_button = ft.IconButton(
            icon=ft.icons.HOME,
            tooltip="Volver al inicio",
            on_click=lambda e: self.page.go("/dashboard")
        )

        self.add_button = ft.ElevatedButton(
            "Agregar Comprador",
            on_click=lambda e: self.page.go("/agregar_comprador")
        )

        self.controls = [
            ft.Column([
                ft.Row([
                    ft.Text("Compradores", weight=ft.FontWeight.BOLD, size=20),
                    self.home_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.add_button,
                self.customer_table
            ], spacing=20)
        ]

        self.load_customers()
        # Do not call self.update() here; it's handled automatically

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
                        ]
                    )
                )
            self.update()  # Update the view to reflect the new data
        except Exception as e:
            show_error_message(self.page, f"Error al cargar los compradores: {str(e)}")

    def on_edit_customer(self, customer):
        try:
            self.page.client_storage.set("edit_customer_id", customer["ID"])
            self.page.go("/editar_comprador")
        except Exception as e:
            show_error_message(
                self.page, f"Error al editar el comprador: {str(e)}")

    def on_delete_customer(self, customer):
        try:
            customer_id = customer["ID"]
            self.customer_service.delete_customer(customer_id)
            show_success_message(self.page, "Comprador eliminado exitosamente")
            self.load_customers()
        except Exception as e:
            show_error_message(
                self.page, f"Error al eliminar el comprador: {str(e)}")