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
        # Input fields
        self.username_field = ft.TextField(
            label="Usuario",
            width=300,
            autofocus=True,
            bgcolor=ft.colors.BLACK38,
            border_color=ft.colors.WHITE,
            color=ft.colors.WHITE,
            border_radius=ft.border_radius.all(5),
        )

        self.password_field = ft.TextField(
            label="Contraseña",
            width=300,
            password=True,
            bgcolor=ft.colors.BLACK38,
            border_color=ft.colors.WHITE,
            color=ft.colors.WHITE,
            border_radius=ft.border_radius.all(5),
        )

        # Login button
        self.login_button = ft.ElevatedButton(
            "Iniciar sesión",
            width=300,
            on_click=self.handle_login,
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLUE_GREY_900,
            elevation=3,
        )

        # Card container for login form
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Iniciar sesión",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                        ),
                        self.username_field,
                        self.password_field,
                        self.login_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                padding=50,
                border_radius=ft.border_radius.all(12),
                bgcolor=ft.colors.BLACK54,
            ),
            width=350,  # Fixed width for the card
        )

        # Full-page centered layout
        self.controls = [
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,  # Centers horizontally and vertically
                expand=True,  # Ensures the container takes the full page
            )
        ]

    def handle_login(self, e):
        try:
            if not all([self.username_field.value, self.password_field.value]):
                show_error_message(self.page, "Todos los campos son obligatorios")
                return

            user = self.auth_service.authenticate_user(
                self.username_field.value, self.password_field.value
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
