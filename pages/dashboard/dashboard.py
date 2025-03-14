import flet as ft
import logging
from datetime import datetime, timedelta
import random
from services.saleService import SaleService
from services.productService import ProductService
from services.expenseService import ExpenseService
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from .stats import create_stats_row
from ui.components.alerts import show_error_message
from .content import DashboardContent
from ui.components.stats_card import StatsCard


class DashboardView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.product_service = ProductService(session)
        self.expense_service = ExpenseService(session)
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(0, self.page)  # Índice 0 para Dashboard

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Dashboard", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                self.build_dashboard_content()
            ], spacing=0, scroll=ft.ScrollMode.AUTO)

            # Contenedor principal
            self.controls = [
                ft.Container(
                    content=ft.Row([
                        self.navigation_rail,
                        ft.VerticalDivider(width=1, color=ft.colors.OUTLINE_VARIANT),
                        ft.Container(
                            padding=20,
                            content=main_content,
                            expand=True
                        )
                    ]),
                    expand=True
                )
            ]

        except Exception as e:
            error_message = f"Error construyendo UI: {str(e)}"
            logging.error(error_message)
            
            # Función para mostrar un error
            def error_boundary():
                return ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=64),
                        ft.Text(
                            "Error al cargar el dashboard",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        ft.Text(
                            error_message,
                            color=ft.colors.ON_SURFACE
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True
                )
            
            self.controls = [error_boundary()]

    def build_dashboard_content(self):
        try:
            # Sección de estadísticas
            stats_section = self.build_stats_section()
            
            # Sección de gráficos
            charts_section = self.build_charts_section()
            
            # Sección de actividad reciente
            activity_section = self.build_activity_section()
            
            # Organizar en pestañas
            tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Resumen",
                        icon=ft.icons.DASHBOARD,
                        content=ft.Container(
                            content=ft.Column([
                                stats_section,
                                charts_section
                            ], spacing=20),
                            padding=10
                        )
                    ),
                    ft.Tab(
                        text="Actividad",
                        icon=ft.icons.HISTORY,
                        content=ft.Container(
                            content=activity_section,
                            padding=10
                        )
                    ),
                ],
                expand=1
            )
            
            return tabs
            
        except Exception as e:
            logging.error(f"Error construyendo contenido del dashboard: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def build_stats_section(self):
        try:
            # Datos de ejemplo (en una aplicación real, estos vendrían de la base de datos)
            ventas_hoy = random.randint(5000, 15000)
            ventas_semana = ventas_hoy * random.randint(5, 7)
            productos_vendidos = random.randint(10, 50)
            clientes_nuevos = random.randint(1, 10)
            
            # Crear tarjetas de estadísticas
            return ft.ResponsiveRow([
                ft.Container(
                    content=StatsCard(
                        title="Ventas de Hoy",
                        value=ventas_hoy,
                        icon=ft.icons.PAYMENTS,
                        color=ft.colors.GREEN
                    ),
                    col={"sm": 6, "md": 3},
                    padding=5
                ),
                ft.Container(
                    content=StatsCard(
                        title="Ventas de la Semana",
                        value=ventas_semana,
                        icon=ft.icons.CALENDAR_MONTH,
                        color=ft.colors.BLUE
                    ),
                    col={"sm": 6, "md": 3},
                    padding=5
                ),
                ft.Container(
                    content=StatsCard(
                        title="Productos Vendidos",
                        value=productos_vendidos,
                        icon=ft.icons.INVENTORY,
                        color=ft.colors.AMBER
                    ),
                    col={"sm": 6, "md": 3},
                    padding=5
                ),
                ft.Container(
                    content=StatsCard(
                        title="Clientes Nuevos",
                        value=clientes_nuevos,
                        icon=ft.icons.PERSON_ADD,
                        color=ft.colors.PURPLE
                    ),
                    col={"sm": 6, "md": 3},
                    padding=5
                ),
            ])
            
        except Exception as e:
            logging.error(f"Error construyendo sección de estadísticas: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def build_charts_section(self):
        try:
            # Crear gráficos de ejemplo
            return ft.ResponsiveRow([
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Ventas por Categoría",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.ON_SURFACE
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        "Gráfico no disponible en esta versión",
                                        color=ft.colors.ON_SURFACE_VARIANT
                                    ),
                                    alignment=ft.alignment.center,
                                    height=200
                                )
                            ]),
                            padding=15
                        )
                    ),
                    col={"sm": 12, "md": 6},
                    padding=5
                ),
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Ventas por Mes",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.ON_SURFACE
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        "Gráfico no disponible en esta versión",
                                        color=ft.colors.ON_SURFACE_VARIANT
                                    ),
                                    alignment=ft.alignment.center,
                                    height=200
                                )
                            ]),
                            padding=15
                        )
                    ),
                    col={"sm": 12, "md": 6},
                    padding=5
                ),
            ])
            
        except Exception as e:
            logging.error(f"Error construyendo sección de gráficos: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def build_activity_section(self):
        try:
            # Crear lista de actividades recientes de ejemplo
            activities = []
            
            # Generar algunas actividades de ejemplo
            for i in range(5):
                days_ago = i
                date = (datetime.now() - timedelta(days=days_ago)).strftime("%d/%m/%Y")
                
                if i % 3 == 0:
                    activity = f"Venta realizada por ${random.randint(1000, 5000)}"
                    icon = ft.icons.SHOPPING_CART
                    color = ft.colors.GREEN
                elif i % 3 == 1:
                    activity = f"Nuevo producto agregado al inventario"
                    icon = ft.icons.INVENTORY
                    color = ft.colors.BLUE
                else:
                    activity = f"Nuevo cliente registrado"
                    icon = ft.icons.PERSON_ADD
                    color = ft.colors.PURPLE
                
                activities.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=color),
                        title=ft.Text(activity, color=ft.colors.ON_SURFACE),
                        subtitle=ft.Text(f"Fecha: {date}", color=ft.colors.ON_SURFACE_VARIANT),
                        trailing=ft.IconButton(
                            icon=ft.icons.MORE_VERT,
                            icon_color=ft.colors.ON_SURFACE_VARIANT
                        )
                    )
                )
            
            return ft.Column([
                ft.Text(
                    "Actividad Reciente",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                ft.Card(
                    content=ft.Column(activities)
                )
            ], spacing=10)
            
        except Exception as e:
            logging.error(f"Error construyendo sección de actividad: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def handle_logout(self, e):
        try:
            self.page.client_storage.remove("token")
            self.page.client_storage.remove("user_role")
            self.page.go("/login")
        except Exception as e:
            show_error_message(self.page, f"Error al cerrar sesión: {str(e)}")

    def handle_resize(self):
        try:
            self.build_ui()
            self.update()
        except Exception as e:
            show_error_message(self.page, f"Error al redimensionar: {str(e)}")
