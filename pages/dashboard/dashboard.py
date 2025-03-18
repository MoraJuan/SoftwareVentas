import flet as ft
import logging
from datetime import datetime, timedelta
import random
from collections import defaultdict
import calendar
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
            # Obtener datos reales de la base de datos
            # Obtener fecha actual y fechas para los rangos
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)
            
            # Ventas de hoy
            ventas_hoy = self.sale_service.get_total_sales_amount(today, tomorrow)
            
            # Ventas de la semana
            ventas_semana = self.sale_service.get_total_sales_amount(start_of_week, tomorrow)
            
            # Obtener productos vendidos en el último mes
            ventas_mes = self.sale_service.get_sales_by_date_range(start_of_month, tomorrow)
            productos_vendidos = 0
            for venta in ventas_mes:
                if hasattr(venta, 'items'):
                    productos_vendidos += len(venta.items)
            
            # Contar clientes únicos en el último mes
            clientes_unicos = set()
            for venta in ventas_mes:
                if hasattr(venta, 'customer_id') and venta.customer_id:
                    clientes_unicos.add(venta.customer_id)
            clientes_nuevos = len(clientes_unicos)
            
            # Crear tarjetas de estadísticas
            return ft.ResponsiveRow([
                ft.Container(
                    content=StatsCard(
                        title="Ventas de Hoy",
                        value=f"${ventas_hoy:.2f}",
                        icon=ft.icons.PAYMENTS,
                        color=ft.colors.GREEN
                    ),
                    col={"sm": 6, "md": 3},
                    padding=5
                ),
                ft.Container(
                    content=StatsCard(
                        title="Ventas de la Semana",
                        value=f"${ventas_semana:.2f}",
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
                        title="Clientes Únicos",
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
            # Obtener datos para las gráficas
            # Fecha actual y fechas para los rangos
            today = datetime.now()
            start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Obtener todas las ventas del año
            ventas_año = self.sale_service.get_sales_by_date_range(start_of_year, today)
            
            # Crear gráficos nativos de Flet
            category_chart = self.create_category_chart_flet(ventas_año)
            monthly_chart = self.create_monthly_chart_flet(ventas_año)
            
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
                                category_chart
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
                                monthly_chart
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
            
    def create_category_chart_flet(self, ventas):
        try:
            # Agrupar ventas por categoría de producto
            category_sales = defaultdict(float)
            
            for venta in ventas:
                try:
                    if hasattr(venta, 'items'):
                        for item in venta.items:
                            try:
                                if hasattr(item, 'product') and item.product is not None and hasattr(item.product, 'category') and item.product.category:
                                    category = item.product.category
                                    # Verificar si el item tiene el atributo subtotal
                                    if hasattr(item, 'subtotal') and item.subtotal is not None:
                                        category_sales[category] += item.subtotal
                                    elif hasattr(item, 'unit_price') and hasattr(item, 'quantity'):
                                        # Calcular subtotal si no está disponible directamente
                                        category_sales[category] += item.unit_price * item.quantity
                            except Exception as item_error:
                                logging.error(f"Error procesando item de venta: {str(item_error)}")
                                continue
                except Exception as venta_error:
                    logging.error(f"Error procesando venta: {str(venta_error)}")
                    continue
            
            # Si no hay datos, mostrar mensaje
            if not category_sales:
                return ft.Container(
                    content=ft.Text(
                        "No hay datos de ventas por categoría",
                        color=ft.colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    height=300
                )
            
            # Ordenar categorías por monto de ventas (descendente)
            sorted_categories = sorted(category_sales.items(), key=lambda x: x[1], reverse=True)
            
            # Tomar las 5 categorías principales y agrupar el resto como "Otros"
            if len(sorted_categories) > 5:
                top_categories = sorted_categories[:5]
                others_sum = sum(amount for _, amount in sorted_categories[5:])
                if others_sum > 0:
                    categories = [cat for cat, _ in top_categories] + ["Otros"]
                    amounts = [amount for _, amount in top_categories] + [others_sum]
                else:
                    categories = [cat for cat, _ in top_categories]
                    amounts = [amount for _, amount in top_categories]
            else:
                categories = [cat for cat, _ in sorted_categories]
                amounts = [amount for _, amount in sorted_categories]
            
            # Calcular el total para los porcentajes
            total = sum(amounts)
            
            # Colores para las categorías
            colors = [
                ft.colors.BLUE,
                ft.colors.GREEN,
                ft.colors.AMBER,
                ft.colors.RED,
                ft.colors.PURPLE,
                ft.colors.TEAL,
                ft.colors.ORANGE,
                ft.colors.PINK
            ]
            
            # Crear gráfico de pastel con PieChart de Flet
            pie_sections = []
            for i, (category, amount) in enumerate(zip(categories, amounts)):
                percentage = (amount / total) * 100 if total > 0 else 0
                color = colors[i % len(colors)]
                
                pie_sections.append(
                    ft.PieChartSection(
                        value=amount,
                        title=f"{category} (${amount:.2f})",
                        color=color,
                        radius=150,
                        title_style=ft.TextStyle(
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE
                        )
                    )
                )
            
            # Crear leyenda
            legend = ft.Column(spacing=5)
            for i, (category, amount) in enumerate(zip(categories, amounts)):
                percentage = (amount / total) * 100 if total > 0 else 0
                color = colors[i % len(colors)]
                
                legend.controls.append(
                    ft.Row([
                        ft.Container(
                            width=20,
                            height=20,
                            bgcolor=color,
                            border_radius=5
                        ),
                        ft.Text(
                            f"{category}: ${amount:.2f} ({percentage:.1f}%)",
                            color=ft.colors.ON_SURFACE
                        )
                    ], spacing=10)
                )
            
            # Crear contenedor con el gráfico y la leyenda
            return ft.Container(
                content=ft.Column([
                    ft.PieChart(
                        sections=pie_sections,
                        sections_space=0,
                        center_space_radius=0,
                        expand=True
                    ),
                    legend
                ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=300,
                alignment=ft.alignment.center
            )
            
        except Exception as e:
            logging.error(f"Error creando gráfico de categorías: {str(e)}")
            return ft.Container(
                content=ft.Text(
                    f"Error al crear gráfico: {str(e)}",
                    color=ft.colors.ERROR,
                    text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.alignment.center,
                height=300
            )
    
    def create_monthly_chart_flet(self, ventas):
        try:
            # Agrupar ventas por mes
            monthly_sales = defaultdict(float)
            
            for venta in ventas:
                try:
                    if hasattr(venta, 'date') and venta.date is not None:
                        month = venta.date.month
                        if hasattr(venta, 'total_amount') and venta.total_amount is not None:
                            monthly_sales[month] += venta.total_amount
                except Exception as venta_error:
                    logging.error(f"Error procesando venta para gráfico mensual: {str(venta_error)}")
                    continue
            
            # Si no hay datos, mostrar mensaje
            if not monthly_sales:
                return ft.Container(
                    content=ft.Text(
                        "No hay datos de ventas mensuales",
                        color=ft.colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    height=300
                )
            
            # Preparar datos para el gráfico
            months = list(range(1, 13))  # 1-12 para todos los meses
            sales_data = [monthly_sales.get(month, 0) for month in months]
            
            # Nombres de los meses
            try:
                month_names = []
                for m in months:
                    try:
                        month_name = calendar.month_abbr[m]
                        month_names.append(month_name)
                    except:
                        month_names.append(f"Mes {m}")
            except:
                month_names = [f"Mes {m}" for m in months]
            
            # Encontrar el valor máximo para escalar el gráfico
            max_value = max(sales_data) if sales_data else 0
            
            # Crear gráfico de barras con BarChart de Flet
            bar_groups = []
            for i, (month, value) in enumerate(zip(month_names, sales_data)):
                bar_groups.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=value,
                                width=20,
                                color=ft.colors.BLUE,
                                tooltip=f"{month}: ${value:.2f}",
                                border_radius=0
                            )
                        ]
                    )
                )
            
            # Crear etiquetas para el eje X
            x_axis = ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            ft.Text(
                                month,
                                size=10,
                                color=ft.colors.ON_SURFACE,
                                text_align=ft.TextAlign.CENTER
                            ),
                            alignment=ft.alignment.center,
                            width=30
                        )
                    )
                    for i, month in enumerate(month_names)
                ],
                labels_size=32
            )
            
            # Crear etiquetas para el eje Y
            y_ticks = 5
            y_interval = max_value / y_ticks if max_value > 0 else 1
            y_axis = ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i * y_interval,
                        label=ft.Text(f"${i * y_interval:.0f}", size=10, color=ft.colors.ON_SURFACE)
                    )
                    for i in range(y_ticks + 1)
                ]
            )
            
            # Crear gráfico de barras
            bar_chart = ft.BarChart(
                bar_groups=bar_groups,
                border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                left_axis=y_axis,
                bottom_axis=x_axis,
                horizontal_grid_lines=ft.ChartGridLines(
                    color=ft.colors.OUTLINE_VARIANT,
                    interval=y_interval
                ),
                tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.SURFACE_VARIANT),
                max_y=max_value * 1.1,  # Añadir un 10% más para espacio
                interactive=True,
                expand=True
            )
            
            return ft.Container(
                content=bar_chart,
                height=300,
                border_radius=5,
                padding=10
            )
            
        except Exception as e:
            logging.error(f"Error creando gráfico mensual: {str(e)}")
            return ft.Container(
                content=ft.Text(
                    f"Error al crear gráfico: {str(e)}",
                    color=ft.colors.ERROR,
                    text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.alignment.center,
                height=300
            )

    def build_activity_section(self):
        try:
            # Obtener datos reales de actividad reciente
            # Obtener fecha actual y fecha de hace 30 días
            today = datetime.now()
            thirty_days_ago = today - timedelta(days=30)
            
            # Obtener ventas recientes
            recent_sales = self.sale_service.get_sales_by_date_range(thirty_days_ago, today)
            
            # Ordenar por fecha (más reciente primero)
            recent_sales.sort(key=lambda x: x.date, reverse=True)
            
            # Limitar a las 10 actividades más recientes
            recent_sales = recent_sales[:10]
            
            # Crear lista de actividades
            activities = []
            
            for sale in recent_sales:
                # Formatear fecha
                date_str = sale.date.strftime("%d/%m/%Y %H:%M")
                
                # Crear descripción de la venta
                activity = f"Venta #{sale.id} por ${sale.total_amount:.2f}"
                
                # Determinar cliente
                customer_name = sale.customer.name if sale.customer else "Cliente no registrado"
                
                # Crear elemento de lista
                activities.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.SHOPPING_CART, color=ft.colors.GREEN),
                        title=ft.Text(activity, color=ft.colors.ON_SURFACE),
                        subtitle=ft.Text(f"Cliente: {customer_name} | Fecha: {date_str}", color=ft.colors.ON_SURFACE_VARIANT),
                        trailing=ft.IconButton(
                            icon=ft.icons.VISIBILITY,
                            icon_color=ft.colors.ON_SURFACE_VARIANT,
                            tooltip="Ver detalles",
                            on_click=lambda _, s=sale.id: self.page.go(f"/ver_reportes/ventas?id={s}")
                        )
                    )
                )
            
            # Si no hay actividades recientes, mostrar mensaje
            if not activities:
                activities.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.INFO, color=ft.colors.BLUE),
                        title=ft.Text("No hay actividad reciente", color=ft.colors.ON_SURFACE),
                        subtitle=ft.Text("No se han registrado ventas en los últimos 30 días", color=ft.colors.ON_SURFACE_VARIANT)
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
