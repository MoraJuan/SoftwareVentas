import flet as ft
import logging
import uuid
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
        self.is_mobile = self.page.width < 600  # Breakpoint para móvil
        self.build_ui()
        self.page.on_resize = self.handle_resize  # Listener para redimensionamiento

    def build_ui(self):
        try:
            # Determinar tamaños según el breakpoint
            logo_size = 60 if self.is_mobile else 80
            title_size = 24 if self.is_mobile else 32
            subtitle_size = 14 if self.is_mobile else 16
            form_width = min(self.page.width * 0.9, 400) if self.is_mobile else 400
            field_width = form_width - 60  # Restar padding interno

            # Logo y título
            logo = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        name=ft.icons.STORE_ROUNDED,
                        size=logo_size,
                        color=ft.colors.PRIMARY
                    ),
                    ft.Text(
                        "DiagSoft",
                        size=title_size,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.PRIMARY
                    ),
                    ft.Text(
                        "Sistema de Gestión de Ventas",
                        size=subtitle_size,
                        color=ft.colors.ON_SURFACE_VARIANT
                    )
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
                margin=ft.margin.only(bottom=20 if self.is_mobile else 40)
            )

            # Campos de inicio de sesión
            self.username_field = ft.TextField(
                label="Usuario",
                width=field_width,
                prefix_icon=ft.icons.PERSON,
                hint_text="Ingrese su nombre de usuario",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.password_field = ft.TextField(
                label="Contraseña",
                width=field_width,
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
                width=field_width,
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
                visible=False,
                size=12 if self.is_mobile else 14
            )

            # Formulario de inicio de sesión
            self.login_form = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Iniciar Sesión",
                        size=20 if self.is_mobile else 24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(height=15 if self.is_mobile else 20),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ft.Container(height=10),
                    login_button,
                    register_link
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10 if self.is_mobile else 15),
                padding=30 if self.is_mobile else 30,
                border_radius=10,
                border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                width=form_width,
                bgcolor=ft.colors.SURFACE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK)
                )
            )

            # Contenedor principal
            self.controls = [
                ft.Container(
                    content=ft.Column([
                        logo,
                        self.login_form
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20 if self.is_mobile else 30),
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

            if not username or not password:
                self.show_error("Por favor complete todos los campos")
                return

            token = str(uuid.uuid4())
            self.page.client_storage.set("token", token)
            self.page.client_storage.set("username", username)
            self.page.client_storage.set("login_time", datetime.now().isoformat())
            self.page.go("/")

        except Exception as e:
            logging.error(f"Error en inicio de sesión: {str(e)}")
            self.show_error(f"Error al iniciar sesión: {str(e)}")

    def show_error(self, message):
        self.error_text.value = message
        self.error_text.visible = True
        self.update()

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.update()
        elif self.login_form:
            # Ajustar dinámicamente el ancho del formulario en pantallas no móviles
            new_form_width = min(self.page.width * 0.9, 400)
            self.login_form.width = new_form_width
            self.username_field.width = new_form_width - 60
            self.password_field.width = new_form_width - 60
            self.login_form.content.controls[2].width = new_form_width - 60  # username_field
            self.login_form.content.controls[3].width = new_form_width - 60  # password_field
            self.login_form.content.controls[6].width = new_form_width - 60  # login_button
            self.update()