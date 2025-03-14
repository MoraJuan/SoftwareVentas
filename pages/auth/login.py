import flet as ft
import logging
import uuid
import hashlib
from datetime import datetime
from services.authService import AuthService
from ui.components.alerts import show_error_message, show_success_message


class LoginView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/login",
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

            # Campos de inicio de sesión
            self.username_field = ft.TextField(
                label="Usuario",
                width=300,
                prefix_icon=ft.icons.PERSON,
                hint_text="Ingrese su nombre de usuario",
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
                hint_text="Ingrese su contraseña",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            # Botón de inicio de sesión
            login_button = ft.ElevatedButton(
                "Iniciar Sesión",
                width=300,
                icon=ft.icons.LOGIN,
                on_click=self.handle_login,
                style=ft.ButtonStyle(
                    color=ft.colors.ON_PRIMARY,
                    bgcolor=ft.colors.PRIMARY
                )
            )

            # Enlace para registrarse
            register_link = ft.TextButton(
                "¿No tiene una cuenta? Regístrese aquí",
                on_click=lambda _: self.page.go("/register")
            )

            # Mensaje de error (inicialmente oculto)
            self.error_text = ft.Text(
                "",
                color=ft.colors.ERROR,
                visible=False
            )

            # Formulario de inicio de sesión
            login_form = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Iniciar Sesión",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(height=20),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ft.Container(height=10),
                    login_button,
                    register_link
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
                        login_form
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor=ft.colors.SURFACE
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de login: {str(e)}")
            self.controls = [
                ft.Container(
                    content=ft.Text(f"Error al cargar la página de inicio de sesión: {str(e)}"),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]

    def handle_login(self, e):
        try:
            username = self.username_field.value
            password = self.password_field.value

            # Validar campos
            if not username or not password:
                self.show_error("Por favor complete todos los campos")
                return

            # En un entorno real, verificaríamos las credenciales contra la base de datos
            # Para este ejemplo, aceptamos cualquier usuario/contraseña
            # Simular autenticación exitosa
            
            # Generar un token de sesión simple
            token = str(uuid.uuid4())
            
            # Guardar el token en el almacenamiento del cliente
            self.page.client_storage.set("token", token)
            self.page.client_storage.set("username", username)
            self.page.client_storage.set("login_time", datetime.now().isoformat())
            
            # Redirigir al dashboard
            self.page.go("/")
            
        except Exception as e:
            logging.error(f"Error en inicio de sesión: {str(e)}")
            self.show_error(f"Error al iniciar sesión: {str(e)}")

    def show_error(self, message):
        self.error_text.value = message
        self.error_text.visible = True
        self.update()
