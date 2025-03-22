import flet as ft
from sqlalchemy.orm import Session
from services.supplierService import SupplierService
from ui.components.alerts import show_success_message, show_error_message
import re

class PageSupplierForm(ft.UserControl):
    def __init__(self, page: ft.Page, session: Session, edit_mode=False):
        super().__init__()
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
            label="Dirección", width=300, multiline=True)
        self.description_field = ft.TextField(
            label="Descripción", width=300, multiline=True)

        # Si estamos en modo edición, cargamos los datos del proveedor
        if self.edit_mode:
            self.load_supplier_data()

        self.save_button = ft.ElevatedButton(
            text="Guardar",
            width=100,
            on_click=self.save_supplier
        )
        self.cancel_button = ft.OutlinedButton(
            text="Cancelar",
            width=100,
            on_click=self.go_back
        )

        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Editar Proveedor" if self.edit_mode else "Agregar Proveedor",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=20),
                    self.name_field,
                    self.email_field,
                    self.phone_field,
                    self.address_field,
                    self.description_field,
                    ft.Container(height=20),
                    ft.Row([
                        self.cancel_button,
                        self.save_button
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=20,
                width=400,
                border_radius=10,
                bgcolor=ft.colors.SURFACE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK)
                )
            )
        ]

    def load_supplier_data(self):
        try:
            supplier_id = self.page.client_storage.get("edit_supplier_id")
            if supplier_id:
                supplier = self.supplier_service.get_supplier_by_id(supplier_id)
                if supplier:
                    self.name_field.value = supplier.name
                    self.email_field.value = supplier.email
                    self.phone_field.value = supplier.phone or ""
                    self.address_field.value = supplier.address
                    self.description_field.value = supplier.description or ""
        except Exception as e:
            show_error_message(self.page, f"Error al cargar los datos del proveedor: {str(e)}")

    def save_supplier(self, e):
        try:
            # Validar campos
            if not self.name_field.value:
                show_error_message(self.page, "El nombre es obligatorio")
                return
            
            if not self.email_field.value:
                show_error_message(self.page, "El email es obligatorio")
                return
            
            if not self.validate_email(self.email_field.value):
                show_error_message(self.page, "El formato del email es inválido")
                return
            
            if self.phone_field.value and not self.validate_phone(self.phone_field.value):
                show_error_message(self.page, "El teléfono debe contener solo dígitos")
                return
            
            if not self.address_field.value:
                show_error_message(self.page, "La dirección es obligatoria")
                return
            
            # Preparar datos
            supplier_data = {
                "name": self.name_field.value,
                "email": self.email_field.value,
                "phone": self.phone_field.value,
                "address": self.address_field.value,
                "description": self.description_field.value
            }
            
            if self.edit_mode:
                # Obtener el ID del proveedor a editar
                supplier_id = self.page.client_storage.get("edit_supplier_id")
                if supplier_id:
                    # Actualizar proveedor
                    self.supplier_service.update_supplier(supplier_id, supplier_data)
                    show_success_message(self.page, "Proveedor actualizado correctamente")
                    self.page.client_storage.remove("edit_supplier_id")
            else:
                # Crear nuevo proveedor
                self.supplier_service.create_supplier(supplier_data)
                show_success_message(self.page, "Proveedor creado correctamente")
            
            # Volver a la lista de proveedores
            self.go_back(None)
            
        except Exception as e:
            show_error_message(self.page, f"Error al guardar el proveedor: {str(e)}")

    def validate_email(self, email: str) -> bool:
        """Valida que el email tenga un formato correcto"""
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """Valida que el número de teléfono solo contenga dígitos y tenga una longitud adecuada"""
        return phone.isdigit() and 7 <= len(phone) <= 15

    def go_back(self, e):
        if self.edit_mode:
            self.page.client_storage.remove("edit_supplier_id")
        
        # Usar la factory para crear la página de proveedores
        from pages.supplier.page_factory import SupplierPageFactory
        supplier_page = SupplierPageFactory.create_supplier_page(
            self.page, 
            self.session, 
            lambda: None  # Placeholder for go_back_callback
        )
        
        self.controls.clear()
        self.controls.append(supplier_page)
        self.update()
