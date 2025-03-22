import flet as ft
from pages.supplier.PageSupplier import PageSupplier
from pages.customer.PageCustomer import PageCustomer
from pages.expences.PageExpences import PageExpense
from ui.components.alerts import show_error_message
import logging

class PageReports(ft.UserControl):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.session = session
        self.is_mobile = self.page.width < 600
        self.current_view = ft.Column(expand=True)  # Contenedor para vistas hijas
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            # Títulos
            title = ft.Text(
                "Reportes",
                size=20 if self.is_mobile else 24,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.ON_SURFACE
            )
            subtitle = ft.Text(
                "Selecciona un reporte",
                size=14 if self.is_mobile else 16,
                color=ft.colors.ON_SURFACE_VARIANT
            )

            # Botones de navegación con íconos
            report_actions = ft.Column(
                [
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.BUSINESS, color=ft.colors.PRIMARY),
                            ft.Text("Proveedores", color=ft.colors.ON_SURFACE)
                        ]),
                        width=min(self.page.width * 0.8, 300) if self.is_mobile else 300,
                        height=50,
                        on_click=lambda _: self.show_suppliers()
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.PEOPLE, color=ft.colors.PRIMARY),
                            ft.Text("Clientes", color=ft.colors.ON_SURFACE)
                        ]),
                        width=min(self.page.width * 0.8, 300) if self.is_mobile else 300,
                        height=50,
                        on_click=lambda _: self.show_customers()
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.MONEY_OFF, color=ft.colors.PRIMARY),
                            ft.Text("Gastos", color=ft.colors.ON_SURFACE)
                        ]),
                        width=min(self.page.width * 0.8, 300) if self.is_mobile else 300,
                        height=50,
                        on_click=lambda _: self.show_expenses()
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            )

            # Contenido principal
            content_column = ft.Column(
                [
                    title,
                    subtitle,
                    ft.Container(height=20),
                    report_actions
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )

            self.main_content = ft.Container(
                content=content_column,
                padding=10 if self.is_mobile else 20,
                expand=True
            )
            self.controls = [self.main_content]

        except Exception as e:
            logging.error(f"Error construyendo UI de reportes: {str(e)}")
            self.controls = [ft.Text(f"Error al cargar la página de reportes: {str(e)}", color=ft.colors.ERROR)]

    def show_suppliers(self):
        # Marcar que estamos navegando desde Reports
        self.page.current_view = 'reports'
        self.controls.clear()
        self.controls.append(PageSupplier(self.page, self.session, self.go_back))
        self.update()

    def show_customers(self):
        # Marcar que estamos navegando desde Reports
        self.page.current_view = 'reports'
        self.controls.clear()
        self.controls.append(PageCustomer(self.page, self.session, self.go_back))
        self.update()

    def show_expenses(self):
        self.controls.clear()
        self.controls.append(PageExpense(self.page, self.session, self.go_back))
        self.update()

    def go_back(self):
        self.controls.clear()
        self.controls.append(self.main_content)
        self.update()

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.go_back()  # Volver a la vista principal al redimensionar
            self.update()
        else:
            for button in self.main_content.content.controls[3].controls:
                button.width = min(self.page.width * 0.8, 300) if self.is_mobile else 300
            self.update()

    def build(self):
        return ft.Column(self.controls, expand=True)