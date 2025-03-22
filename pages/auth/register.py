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

            # Campos de registro
            self.name_field = ft.TextField(
                label="Nombre Completo",
                width=field_width,
                prefix_icon=ft.icons.PERSON,
                hint_text="Ingrese su nombre completo",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.username_field = ft.TextField(
                label="Usuario",
                width=field_width,
                prefix_icon=ft.icons.ACCOUNT_CIRCLE,
                hint_text="Ingrese un nombre de usuario",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.email_field = ft.TextField(
                label="Correo Electrónico",
                width=field_width,
                prefix_icon=ft.icons.EMAIL,
                hint_text="Ingrese su correo electrónico",
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
                hint_text="Ingrese una contraseña",
                label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
                border_color=ft.colors.OUTLINE
            )

            self.confirm_password_field = ft.TextField(
                label="Confirmar Contraseña",
                width=field_width,
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
                width=field_width,
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
                visible=False,
                size=12 if self.is_mobile else 14
            )

            # Formulario de registro
            self.register_form = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Crear Cuenta",
                        size=20 if self.is_mobile else 24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(height=15 if self.is_mobile else 20),
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
                        self.register_form
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
            name = self.name_field.value
            username = self.username_field.value
            email = self.email_field.value
            password = self.password_field.value
            confirm_password = self.confirm_password_field.value

            if not all([name, username, email, password, confirm_password]):
                self.show_error("Por favor complete todos los campos")
                return

            if password != confirm_password:
                self.show_error("Las contraseñas no coinciden")
                return

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

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.update()
        elif self.register_form:
            # Ajustar dinámicamente el ancho del formulario en pantallas no móviles
            new_form_width = min(self.page.width * 0.9, 400)
            self.register_form.width = new_form_width
            self.name_field.width = new_form_width - 60
            self.username_field.width = new_form_width - 60
            self.email_field.width = new_form_width - 60
            self.password_field.width = new_form_width - 60
            self.confirm_password_field.width = new_form_width - 60
            self.register_form.content.controls[2].width = new_form_width - 60  # name_field
            self.register_form.content.controls[3].width = new_form_width - 60  # username_field
            self.register_form.content.controls[4].width = new_form_width - 60  # email_field
            self.register_form.content.controls[5].width = new_form_width - 60  # password_field
            self.register_form.content.controls[6].width = new_form_width - 60  # confirm_password_field
            self.register_form.content.controls[9].width = new_form_width - 60  # register_button
            self.update()