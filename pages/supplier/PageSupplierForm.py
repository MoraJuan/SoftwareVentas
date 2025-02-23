import flet as ft
from sqlalchemy.orm import Session
from services.supplierService import SupplierService
from ui.components.alerts import show_success_message, show_error_message
import re

class PageSupplierForm(ft.View):
    def __init__(self, page: ft.Page, session: Session, edit_mode=False):
        super().__init__(
            route="/agregar_proveedor" if not edit_mode else "/editar_proveedor",
            controls=[],
            padding=20
        )
        self.page = page
        self.session = session
        self.edit_mode = edit_mode
        self.supplier_service = SupplierService(session)
        self.page.title = "Agregar Proveedor" if not edit_mode else "Editar Proveedor"
        self.build_ui()

    def build_ui(self):
        self.name_field = ft.TextField(
            label="Nombre", width=300, autofocus=True)
        self.email_field = ft.TextField(
            label="Email", width=300)
        self.phone_field = ft.TextField(
            label="Teléfono", width=300)
        self.address_field = ft.TextField(
            label="Dirección", width=300)

        self.cancel_button = ft.ElevatedButton(
            text="Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.go_back
        )
        self.save_button = ft.ElevatedButton(
            text="Guardar",
            icon=ft.icons.SAVE,
            on_click=self.save_supplier
        )

        self.controls = [
            ft.Column([
                ft.Row([
                    ft.Text(
                        "Editar Proveedor" if self.edit_mode else "Nuevo Proveedor",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        tooltip="Volver",
                        on_click=self.go_back
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Column([
                    self.name_field,
                    self.email_field,
                    self.phone_field,
                    self.address_field,
                    ft.Row([
                        self.cancel_button,
                        self.save_button
                    ], spacing=10)
                ], spacing=10)
            ], spacing=20)
        ]

        if self.edit_mode:
            self.load_supplier_data()

    def load_supplier_data(self):
        try:
            supplier_id = self.page.client_storage.get("edit_supplier_id")
            if supplier_id:
                supplier = self.supplier_service.get_supplier_by_id(
                    supplier_id)
                if supplier:
                    self.name_field.value = supplier.name
                    self.email_field.value = supplier.email
                    self.phone_field.value = supplier.phone
                    self.address_field.value = supplier.address
                    self.update()  # Actualiza la vista después de cargar los datos
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los datos del proveedor: {str(e)}")

    def save_supplier(self, e):
            try:
                name = self.name_field.value.strip()
                email = self.email_field.value.strip()
                phone = self.phone_field.value.strip()
                address = self.address_field.value.strip()

                # Validaciones
                if not all([name, email, phone, address]):
                    show_error_message(
                        self.page, "Por favor complete todos los campos")
                    return

                if not self.validate_email(email):
                    show_error_message(
                        self.page, "Por favor ingrese un correo electrónico válido")
                    return

                if not self.validate_phone(phone):
                    show_error_message(
                        self.page, "Por favor ingrese un número de teléfono válido")
                    return

                supplier_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "address": address
                }

                if self.edit_mode:
                    supplier_id = self.page.client_storage.get("edit_supplier_id")
                    self.supplier_service.update_supplier(
                        supplier_id, supplier_data)
                    message = "Proveedor actualizado exitosamente"
                else:
                    self.supplier_service.create_supplier(supplier_data)
                    message = "Proveedor creado exitosamente"

                show_success_message(self.page, message)
                self.go_back(None)

            except Exception as e:
                show_error_message(
                    self.page, f"Error al guardar el proveedor: {str(e)}")

    def validate_email(self, email: str) -> bool:
        """Valida el formato del correo electrónico"""
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(regex, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """Valida que el número de teléfono solo contenga dígitos y tenga una longitud adecuada"""
        return phone.isdigit() and 7 <= len(phone) <= 15

    def go_back(self, e):
        if self.edit_mode:
            self.page.client_storage.remove("edit_supplier_id")
        self.page.go("/ver_proveedores")
