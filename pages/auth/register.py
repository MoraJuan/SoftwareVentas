import flet as ft
from services.authService import AuthService
from ui.components.alerts import show_error_message, show_success_message
from models.User import UserRole

class RegisterView:
    def __init__(self, page: ft.Page, session):
        self.page = page
        self.auth_service = AuthService(session)
        self.build_ui()
    
    def build_ui(self):
        self.username_field = ft.TextField(
            label="Usuario",
            width=300,
            autofocus=True
        )
        
        self.email_field = ft.TextField(
            label="Correo electrónico",
            width=300
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            width=300,
            password=True
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirmar contraseña",
            width=300,
            password=True
        )
        
        self.role_dropdown = ft.Dropdown(
            label="Rol",
            width=300,
            options=[
                ft.dropdown.Option("EMPLOYEE", "Empleado"),
                ft.dropdown.Option("MANAGER", "Gerente")
            ]
        )
        
        self.register_button = ft.ElevatedButton(
            "Registrarse",
            width=300,
            on_click=self.handle_register
        )
        
        self.login_link = ft.TextButton(
            "¿Ya tienes cuenta? Inicia sesión",
            on_click=lambda _: self.page.go("/login")
        )
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Registro", size=30, weight=ft.FontWeight.BOLD),
                    self.username_field,
                    self.email_field,
                    self.password_field,
                    self.confirm_password_field,
                    self.role_dropdown,
                    self.register_button,
                    self.login_link
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
                alignment=ft.alignment.center,
                padding=50
            )
        )
    
    def handle_register(self, e):
        try:
            # Validaciones
            if not all([
                self.username_field.value,
                self.email_field.value,
                self.password_field.value,
                self.confirm_password_field.value
            ]):
                show_error_message(self.page, "Todos los campos son obligatorios")
                return
            
            if self.password_field.value != self.confirm_password_field.value:
                show_error_message(self.page, "Las contraseñas no coinciden")
                return
            
            # Crear usuario
            user_data = {
                "username": self.username_field.value,
                "email": self.email_field.value,
                "password": self.password_field.value,
                "role": self.role_dropdown.value or "EMPLOYEE"
            }
            
            user = self.auth_service.register_user(user_data)
            show_success_message(self.page, "Usuario registrado exitosamente")
            self.page.go("/login")
            
        except Exception as e:
            show_error_message(self.page, f"Error al registrar usuario: {str(e)}")