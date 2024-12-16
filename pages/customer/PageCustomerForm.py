import flet as ft
from sqlalchemy.orm import Session
from services.customerService import CustomerService
from ui.components.alerts import show_success_message, show_error_message

class PageCustomerForm(ft.View):
    def __init__(self, page: ft.Page, session: Session, edit_mode=False):
        super().__init__(
            route="/agregar_comprador" if not edit_mode else "/editar_comprador",
            controls=[],
            padding=20
        )
        self.page = page
        self.session = session
        self.edit_mode = edit_mode
        self.customer_service = CustomerService(session)
        self.page.title = "Agregar Comprador" if not edit_mode else "Editar Comprador"
        self.build_ui()

    def build_ui(self):
        self.name_field = ft.TextField(
            label="Nombre",
            width=300,
            autofocus=True
        )
        self.email_field = ft.TextField(
            label="Email",
            width=300
        )

        self.cancel_button = ft.ElevatedButton(
            text="Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.go_back
        )
        self.save_button = ft.ElevatedButton(
            text="Guardar",
            icon=ft.icons.SAVE,
            on_click=self.save_customer
        )

        self.controls = [
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text(
                            "Editar Comprador" if self.edit_mode else "Nuevo Comprador",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            tooltip="Volver",
                            on_click=self.go_back
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10
                ),
                ft.Container(
                    content=ft.Column([
                        self.name_field,
                        self.email_field,
                        ft.Row([
                            self.cancel_button,
                            self.save_button
                        ], spacing=10)
                    ]),
                    padding=10
                )
            ], spacing=20)
        ]

        if self.edit_mode:
            self.load_customer_data()

    def load_customer_data(self):
        try:
            customer_id = self.page.client_storage.get("edit_customer_id")
            if customer_id:
                customer = self.customer_service.get_customer_by_id(customer_id)
                if customer:
                    self.name_field.value = customer.name
                    self.email_field.value = customer.email
                    self.update()
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los datos del comprador: {str(e)}")

    def save_customer(self, e):
        try:
            if not all([self.name_field.value, self.email_field.value]):
                show_error_message(self.page, "Por favor complete todos los campos")
                return

            customer_data = {
                "name": self.name_field.value,
                "email": self.email_field.value
            }

            if self.edit_mode:
                customer_id = self.page.client_storage.get("edit_customer_id")
                self.customer_service.update_customer(customer_id, customer_data)
                message = "Comprador actualizado exitosamente"
            else:
                self.customer_service.create_customer(customer_data)
                message = "Comprador creado exitosamente"

            show_success_message(self.page, message)
            self.go_back(None)

        except Exception as e:
            show_error_message(self.page, f"Error al guardar el comprador: {str(e)}")

    def go_back(self, e):
        if self.edit_mode:
            self.page.client_storage.remove("edit_customer_id")
        self.page.go("/ver_compradores")