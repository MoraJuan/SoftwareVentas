import flet as ft
from services.authService import AuthService
from ui.components.alerts import show_error_message, show_success_message

class LoginView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.auth_service = AuthService(session)
        self.build_ui()
    
    def build_ui(self):
        self.username_field = ft.TextField(
            label="Usuario",
            width=300,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            width=300,
            password=True
        )
        
        self.login_button = ft.ElevatedButton(
            "Iniciar sesión",
            width=300,
            on_click=self.handle_login
        )
        
        self.register_link = ft.TextButton(
            "¿No tienes cuenta? Regístrate",
            on_click=lambda _: self.page.go("/register")
        )
        
        self.reset_password_link = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            on_click=lambda _: self.page.go("/reset-password")
        )
        
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Iniciar sesión", size=30, weight=ft.FontWeight.BOLD),
                    self.username_field,
                    self.password_field,
                    self.login_button,
                    self.register_link,
                    self.reset_password_link
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
                padding=30
            )
        )
        
        self.controls = [
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.colors.BLUE_GREY_50,
            )
        ]
    
    def handle_login(self, e):
        try:
            if not all([self.username_field.value, self.password_field.value]):
                show_error_message(self.page, "Todos los campos son obligatorios")
                return
            
            user = self.auth_service.authenticate_user(
                self.username_field.value,
                self.password_field.value
            )
            
            if user:
                token = self.auth_service.create_access_token(user)
                self.page.client_storage.set("token", token)
                self.page.client_storage.set("user_role", user.role.value)
                show_success_message(self.page, "Inicio de sesión exitoso")
                self.page.go("/dashboard")
            else:
                show_error_message(self.page, "Credenciales inválidas")
                
        except Exception as e:
            show_error_message(self.page, f"Error al iniciar sesión: {str(e)}")