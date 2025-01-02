import flet as ft
from datetime import datetime
from services.saleService import SaleService
from services.productService import ProductService
from ui.components.navigation import create_navigation_rail, get_route_for_index
from .stats import create_stats_row
from ui.components.alerts import show_error_message


class DashboardView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/dashboard",
            padding=0,
            bgcolor=ft.colors.BACKGROUND
        )
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.product_service = ProductService(session)
        self.build_ui()

    def build_ui(self):
        try:
            # Create navigation rail with proper constraints
            self.navigation_rail = create_navigation_rail(
                0, self.handle_navigation)

            # Main content area
            content_area = ft.Container(
                content=self.build_dashboard_content(),
                expand=True,
                padding=20,
            )

            # Error boundary wrapper
            def error_boundary(error):
                return ft.Container(
                    content=ft.Column([
                        ft.Text("Error loading dashboard content",
                                size=20, color=ft.colors.RED),
                        ft.Text(str(error), color=ft.colors.RED),
                        ft.ElevatedButton(
                            "Retry", on_click=lambda _: self.build_ui())
                    ]),
                    padding=20
                )

            # Set the view's content
            self.controls = [
                ft.Container(
                    content=ft.Row([
                        self.navigation_rail,
                        content_area
                    ]),
                    expand=True
                )]

        except Exception as e:
            show_error_message(
                self.page, f"Error building dashboard: {str(e)}")
            self.controls = [error_boundary(e)]

    def build_dashboard_content(self):
        try:
            # Stats section with responsive grid
            stats_row = create_stats_row(
                self.sale_service, self.product_service)

            # Charts section with responsive layout
            charts_container = ft.ResponsiveRow([
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Sales Overview", size=20,
                                        weight=ft.FontWeight.BOLD),
                                ft.Container(height=300)  # Chart placeholder
                            ]),
                            padding=20
                        )
                    ),
                    col={"sm": 12, "md": 6, "lg": 6},
                    padding=10
                ),
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Top Products", size=20,
                                        weight=ft.FontWeight.BOLD),
                                ft.Container(height=300)  # Chart placeholder
                            ]),
                            padding=20
                        )
                    ),
                    col={"sm": 12, "md": 6, "lg": 6},
                    padding=10
                )
            ])

            # Recent activity section
            activity_list = ft.ListView(
                expand=1,
                spacing=10,
                padding=20,
                height=200
            )

            return ft.Column([
                stats_row,
                charts_container,
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Recent Activity", size=20,
                                    weight=ft.FontWeight.BOLD),
                            activity_list
                        ]),
                        padding=20
                    )
                )
            ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=20)

        except Exception as e:
            show_error_message(
                self.page, f"Error building dashboard content: {str(e)}")
            return ft.Container(
                content=ft.Text(f"Error: {str(e)}", color=ft.colors.RED),
                padding=20
            )

    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")

    def handle_logout(self, e):
        try:
            self.page.client_storage.remove("token")
            self.page.client_storage.remove("user_role")
            self.page.go("/login")
        except Exception as e:
            show_error_message(self.page, f"Logout error: {str(e)}")

    def handle_resize(self):
        try:
            self.build_ui()
            self.update()
        except Exception as e:
            show_error_message(self.page, f"Resize error: {str(e)}")
