import flet as ft
import logging
import uuid
from datetime import datetime
from services.authService import AuthService
from ui.components.alerts import show_error_message, show_success_message
from models.User import UserRole

class RegisterView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/register",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.auth_service = AuthService(session)
        self.build_ui()
    
    def build_ui(self):
        try:
            # Logo y título
            logo = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        name=ft.icons.STORE_ROUNDED,
                        size=80,
                        color=ft.colors.PRIMARY
                    ),
                    ft.Text(
                        "DiagSoft",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.PRIMARY
                    ),
                    ft.Text(
                        "Sistema de Gestión de Ventas",
                        size=16,
                        color=ft.colors.ON_SURFACE_VARIANT
                    )
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
                margin=ft.margin.only(bottom=40)
            )

            # Campos de registro
            self.name_field = ft.TextField(
                label="Nombre Completo",
                width=300,
                prefix_icon=ft.icons.PERSON,
                hint_text="Ingrese su nombre completo",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.username_field = ft.TextField(
                label="Usuario",
                width=300,
                prefix_icon=ft.icons.ACCOUNT_CIRCLE,
                hint_text="Ingrese un nombre de usuario",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.email_field = ft.TextField(
                label="Correo Electrónico",
                width=300,
                prefix_icon=ft.icons.EMAIL,
                hint_text="Ingrese su correo electrónico",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.password_field = ft.TextField(
                label="Contraseña",
                width=300,
                prefix_icon=ft.icons.LOCK,
                password=True,
                can_reveal_password=True,
                hint_text="Ingrese una contraseña",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.confirm_password_field = ft.TextField(
                label="Confirmar Contraseña",
                width=300,
                prefix_icon=ft.icons.LOCK_OUTLINE,
                password=True,
                can_reveal_password=True,
                hint_text="Confirme su contraseña",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            # Botón de registro
            register_button = ft.ElevatedButton(
                "Registrarse",
                width=300,
                icon=ft.icons.APP_REGISTRATION,
                on_click=self.handle_register,
                style=ft.ButtonStyle(
                    color=ft.colors.ON_PRIMARY,
                    bgcolor=ft.colors.PRIMARY
                )
            )

            # Enlace para iniciar sesión
            login_link = ft.TextButton(
                "¿Ya tiene una cuenta? Inicie sesión aquí",
                on_click=lambda _: self.page.go("/login")
            )

            # Mensaje de error (inicialmente oculto)
            self.error_text = ft.Text(
                "",
                color=ft.colors.ERROR,
                visible=False
            )

            # Formulario de registro
            register_form = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Crear Cuenta",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(height=20),
                    self.name_field,
                    self.username_field,
                    self.email_field,
                    self.password_field,
                    self.confirm_password_field,
                    self.error_text,
                    ft.Container(height=10),
                    register_button,
                    login_link
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15),
                padding=30,
                border_radius=10,
                border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                width=400
            )

            # Contenedor principal
            self.controls = [
                ft.Container(
                    content=ft.Column([
                        logo,
                        register_form
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor=ft.colors.SURFACE
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de registro: {str(e)}")
            self.controls = [
                ft.Container(
                    content=ft.Text(f"Error al cargar la página de registro: {str(e)}"),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]

    def handle_register(self, e):
        try:
            # Obtener valores de los campos
            name = self.name_field.value
            username = self.username_field.value
            email = self.email_field.value
            password = self.password_field.value
            confirm_password = self.confirm_password_field.value

            # Validar campos
            if not all([name, username, email, password, confirm_password]):
                self.show_error("Por favor complete todos los campos")
                return

            if password != confirm_password:
                self.show_error("Las contraseñas no coinciden")
                return

            # Crear usuario
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "role": "EMPLOYEE"
            }
            
            user = self.auth_service.register_user(user_data)
            show_success_message(self.page, "Usuario registrado exitosamente")
            self.page.go("/login")
            
        except Exception as e:
            logging.error(f"Error en registro: {str(e)}")
            self.show_error(f"Error al registrarse: {str(e)}")

    def show_error(self, message):
        self.error_text.value = message
        self.error_text.visible = True
        self.update()