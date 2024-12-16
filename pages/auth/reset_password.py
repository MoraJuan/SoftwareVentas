import flet as ft
from services.authService import AuthService
from ui.components.alerts import show_error_message, show_success_message

class ResetPasswordView:
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.auth_service = AuthService(session)
        self.build_ui()
    
    def build_ui(self):
        self.email_field = ft.TextField(
            label="Correo electrónico",
            width=300,
            autofocus=True
        )
        
        self.reset_button = ft.ElevatedButton(
            "Restablecer contraseña",
            width=300,
            on_click=self.handle_reset
        )
        
        self.login_link = ft.TextButton(
            "Volver al inicio de sesión",
            on_click=lambda _: self.page.go("/login")
        )
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Restablecer contraseña", 
                           size=30, 
                           weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Ingresa tu correo electrónico y te enviaremos "
                        "instrucciones para restablecer tu contraseña."
                    ),
                    self.email_field,
                    self.reset_button,
                    self.login_link
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
                alignment=ft.alignment.center,
                padding=50
            )
        )
    
    def handle_reset(self, e):
        try:
            if not self.email_field.value:
                show_error_message(self.page, "Ingresa tu correo electrónico")
                return
            
            self.auth_service.send_reset_password_email(self.email_field.value)
            show_success_message(
                self.page,
                "Se han enviado las instrucciones a tu correo electrónico"
            )
            self.page.go("/login")
            
        except Exception as e:
            show_error_message(
                self.page, 
                f"Error al restablecer contraseña: {str(e)}"
            )