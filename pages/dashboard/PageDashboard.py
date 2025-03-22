# pages/dashboard.py
import flet as ft
import logging
from ui.components.stats_card import StatsCard
from datetime import datetime, timedelta
from services.saleService import SaleService
from services.productService import ProductService
from collections import defaultdict
import calendar


class PageDashboard(ft.UserControl):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.product_service = ProductService(session)
        # Estado para el layout responsivo
        self.is_mobile = self.page.width < 768 if hasattr(
            self.page, 'width') else False
        self.is_tablet = 768 <= self.page.width < 1200 if hasattr(
            self.page, 'width') else False
        self.is_desktop = self.page.width >= 1200 if hasattr(
            self.page, 'width') else True

        self.build_ui()

    def build_ui(self):
        # Contenido básico del dashboard
        self.content = ft.Column(
            controls=[
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Resumen general", size=16),
                self.build_dashboard_content()
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def build(self):
        return ft.Container(
            content=self.content,
            padding=10,
            alignment=ft.alignment.top_left,
            expand=True,
            width=self.page.width if hasattr(self.page, 'width') else None,
        )

    def build_dashboard_content(self):
        # Sección de estadísticas
        stats_section = self.build_stats_section()

        # Sección de gráficos
        charts_section = self.build_charts_section()

        # Sección de actividad reciente
        activity_section = self.build_activity_section()

        # Crear contenedores para cada sección
        self.resumen_container = ft.Container(
            content=ft.Column([
                stats_section,
                charts_section
            ],
                visible=True,  # Inicialmente visible
            ))

        self.actividad_container = ft.Container(
            content=activity_section,
            visible=False,  # Inicialmente oculto
        )

        # Función para cambiar entre tabs
        def cambiar_tab(e):
            tab_seleccionado = e.control.data
            if tab_seleccionado == "resumen":
                self.resumen_container.visible = True
                self.actividad_container.visible = False
                self.resumen_tab.bgcolor = ft.colors.PRIMARY_CONTAINER
                self.actividad_tab.bgcolor = None
            elif tab_seleccionado == "actividad":
                self.resumen_container.visible = False
                self.actividad_container.visible = True
                self.resumen_tab.bgcolor = None
                self.actividad_tab.bgcolor = ft.colors.PRIMARY_CONTAINER
            self.update()

        # Crear tabs
        self.resumen_tab = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.DASHBOARD,
                    tooltip="Resumen",
                ),
                ft.Text(
                    "Resumen",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
            ],
                spacing=10,
            ),
            padding=10,
            border_radius=5,
            bgcolor=ft.colors.PRIMARY_CONTAINER,  # Inicialmente seleccionado
            on_click=cambiar_tab,
            data="resumen",
        )

        self.actividad_tab = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.HISTORY,
                    tooltip="Actividad",
                ),
                ft.Text(
                    "Actividad",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
            ],
                spacing=10,
            ),
            padding=10,
            border_radius=5,
            on_click=cambiar_tab,
            data="actividad",
        )

        return ft.Column(
            controls=[
                # Tabs
                ft.Row(
                    [self.resumen_tab, self.actividad_tab],
                    spacing=10,
                ),

                # Contenedores de contenido
                ft.Container(
                    content=ft.Column(
                        [self.resumen_container, self.actividad_container],
                    ),
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    padding=10,
                    margin=ft.margin.only(top=10),
                ),
            ],
            spacing=10,
            expand=True
        )

    def build_stats_section(self):
        try:
            # Obtener datos reales de la base de datos
            # Obtener fecha actual y fechas para los rangos
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)

            # Ventas de hoy
            ventas_hoy = self.sale_service.get_total_sales_amount(
                today, tomorrow)

            # Ventas de la semana
            ventas_semana = self.sale_service.get_total_sales_amount(
                start_of_week, tomorrow)

            # Obtener productos vendidos en el último mes
            ventas_mes = self.sale_service.get_sales_by_date_range(
                start_of_month, tomorrow)
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
            logging.error(
                f"Error construyendo sección de estadísticas: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def build_charts_section(self):
        try:
            # Obtener datos para las gráficas
            # Fecha actual y fechas para los rangos
            today = datetime.now()
            start_of_year = today.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            # Obtener todas las ventas del año
            ventas_año = self.sale_service.get_sales_by_date_range(
                start_of_year, today)

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

                                    # Verificar si la categoría es un ID numérico y convertirla a nombre
                                    if str(category).isdigit():
                                        category_name = self.product_service.get_category_name_by_id(
                                            category)
                                        if category_name:
                                            category = category_name

                                    # Verificar si el item tiene el atributo subtotal
                                    if hasattr(item, 'subtotal') and item.subtotal is not None:
                                        category_sales[category] += item.subtotal
                                    elif hasattr(item, 'unit_price') and hasattr(item, 'quantity'):
                                        # Calcular subtotal si no está disponible directamente
                                        category_sales[category] += item.unit_price * \
                                            item.quantity
                            except Exception as item_error:
                                logging.error(
                                    f"Error procesando item de venta: {str(item_error)}")
                                continue
                except Exception as venta_error:
                    logging.error(
                        f"Error procesando venta: {str(venta_error)}")
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
                    height=self.get_chart_height()
                )

            # Ordenar categorías por monto de ventas (descendente)
            sorted_categories = sorted(
                category_sales.items(), key=lambda x: x[1], reverse=True)

            # Limitar categorías según dispositivo
            max_categories = 3 if self.is_mobile else 5

            # Tomar las categorías principales y agrupar el resto como "Otros"
            if len(sorted_categories) > max_categories:
                top_categories = sorted_categories[:max_categories]
                others_sum = sum(
                    amount for _, amount in sorted_categories[max_categories:])
                if others_sum > 0:
                    categories = [cat for cat, _ in top_categories] + ["Otros"]
                    amounts = [amount for _,
                               amount in top_categories] + [others_sum]
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

                # Adaptar tamaño del radio según dispositivo
                pie_radius = 90 if self.is_mobile else 150
                font_size = 10 if self.is_mobile else 14

                pie_sections.append(
                    ft.PieChartSection(
                        value=amount,
                        title=f"{category.name if hasattr(category, 'name') else 'Otros'} (${amount:.0f})" if not self.is_mobile else f"${amount:.0f}",
                        color=color,
                        radius=pie_radius,
                        title_style=ft.TextStyle(
                            size=font_size,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE
                        )
                    )
                )

            # Crear leyenda, simplificada en móvil
            legend = ft.Column(spacing=5)
            for i, (category, amount) in enumerate(zip(categories, amounts)):
                percentage = (amount / total) * 100 if total > 0 else 0
                color = colors[i % len(colors)]

                # Texto más compacto en móvil
                if self.is_mobile:
                    legend_text = f"{category.name if hasattr(category, 'name') else 'Otros'}: {percentage:.1f}%"
                else:
                    legend_text = f"{category.name if hasattr(category, 'name') else 'Otros'}: ${amount:.2f} ({percentage:.1f}%)"

                legend.controls.append(
                    ft.Row([
                        ft.Container(
                            width=15 if self.is_mobile else 20,
                            height=15 if self.is_mobile else 20,
                            bgcolor=color,
                            border_radius=5
                        ),
                        ft.Text(
                            legend_text,
                            color=ft.colors.ON_SURFACE,
                            size=12 if self.is_mobile else 14
                        )
                    ], spacing=8 if self.is_mobile else 10)
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
                ], spacing=10 if self.is_mobile else 20),
                height=self.get_chart_height()
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
                height=self.get_chart_height()
            )

    def build_activity_section(self):
        # Crear contenedores para cada sección
        self.ventas_container = ft.Container(
            content=self.build_recent_sales_section(),
            visible=True,  # Inicialmente visible
        )
        
        self.inventario_container = ft.Container(
            content=self.build_recent_inventory_section(),
            visible=False,  # Inicialmente oculto
        )
        
        # Función para cambiar entre tabs
        def cambiar_tab_actividad(e):
            tab_seleccionado = e.control.data
            if tab_seleccionado == "ventas":
                self.ventas_container.visible = True
                self.inventario_container.visible = False
                self.ventas_tab.bgcolor = ft.colors.PRIMARY_CONTAINER
                self.inventario_tab.bgcolor = None
            elif tab_seleccionado == "inventario":
                self.ventas_container.visible = False
                self.inventario_container.visible = True
                self.ventas_tab.bgcolor = None
                self.inventario_tab.bgcolor = ft.colors.PRIMARY_CONTAINER
            self.update()
        
        # Crear tabs
        self.ventas_tab = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.SHOPPING_CART,
                    tooltip="Ventas Recientes",
                ),
                ft.Text(
                    "Ventas Recientes",
                    size=14,
                    weight=ft.FontWeight.BOLD
                ),
            ],
                spacing=5,
            ),
            padding=10,
            border_radius=5,
            bgcolor=ft.colors.PRIMARY_CONTAINER,  # Inicialmente seleccionado
            on_click=cambiar_tab_actividad,
            data="ventas",
        )
        
        self.inventario_tab = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.INVENTORY,
                    tooltip="Inventario",
                ),
                ft.Text(
                    "Inventario",
                    size=14,
                    weight=ft.FontWeight.BOLD
                ),
            ],
                spacing=5,
            ),
            padding=10,
            border_radius=5,
            on_click=cambiar_tab_actividad,
            data="inventario",
        )
        
        return ft.Column([
            ft.Text("Actividad Reciente", size=16, weight=ft.FontWeight.BOLD),
            # Tabs
            ft.Row(
                [self.ventas_tab, self.inventario_tab],
                spacing=5,
            ),
            
            # Contenedores de contenido
            ft.Container(
                content=ft.Column(
                    [self.ventas_container, self.inventario_container],
                ),
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                padding=10,
                margin=ft.margin.only(top=10),
            ),
        ],
        spacing=10)

    def get_chart_height(self):
        """Devuelve la altura apropiada para gráficos según el dispositivo"""
        if self.is_mobile:
            return 250
        elif self.is_tablet:
            return 280
        else:
            return 300

    def create_monthly_chart_flet(self, ventas):
        try:
            # Inicializar ventas mensuales
            today = datetime.now()
            year = today.year
            monthly_sales = {month: 0 for month in range(1, 13)}

            # Agrupar ventas por mes
            for venta in ventas:
                if hasattr(venta, 'date') and venta.date is not None:
                    # Solo contar ventas del año actual
                    if venta.date.year == year:
                        month = venta.date.month
                        if hasattr(venta, 'total_amount') and venta.total_amount is not None:
                            monthly_sales[month] += venta.total_amount

            # Si no hay datos, mostrar mensaje
            if sum(monthly_sales.values()) == 0:
                return ft.Container(
                    content=ft.Text(
                        "No hay datos de ventas mensuales para este año",
                        color=ft.colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    height=self.get_chart_height()
                )

            # Limitar a últimos 6 meses en móvil, todo el año en desktop
            if self.is_mobile:
                current_month = today.month
                # Mostrar últimos 6 meses
                start_month = max(1, current_month - 5)
                months_to_display = range(start_month, current_month + 1)
                monthly_sales = {month: amount for month, amount in monthly_sales.items(
                ) if month in months_to_display}

            # Nombres de los meses
            month_names = [
                calendar.month_abbr[1], calendar.month_abbr[2],
                calendar.month_abbr[3], calendar.month_abbr[4],
                calendar.month_abbr[5], calendar.month_abbr[6],
                calendar.month_abbr[7], calendar.month_abbr[8],
                calendar.month_abbr[9], calendar.month_abbr[10],
                calendar.month_abbr[11], calendar.month_abbr[12]
            ]

            # En móvil, usar nombres de mes más cortos
            if self.is_mobile:
                # Usar 3 letras en vez de 1
                month_names = [name[:3] for name in month_names]

            # Calcular valor máximo para el eje Y
            max_value = max(monthly_sales.values()) if monthly_sales else 0

            # Calcular intervalo para el eje Y (redondeado a un número "bonito")
            y_interval = max(1, 10 ** (len(str(int(max_value))) - 1))
            while max_value / y_interval > 10:
                y_interval *= 2

            # Número de divisiones en el eje Y
            y_ticks = max(4, int(max_value / y_interval)) + 1

            # Crear barras para cada mes
            bar_groups = []

            for month, amount in monthly_sales.items():
                bar_groups.append(
                    ft.BarChartGroup(
                        x=month - 1,  # Índice 0-based para los meses
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=amount,
                                width=18 if not self.is_mobile else 12,
                                color=ft.colors.PRIMARY,
                                tooltip=f"{month_names[month - 1]}: ${amount:.2f}",
                                border_radius=0
                            )
                        ]
                    )
                )

            # Crear eje X con nombres de meses
            x_axis = ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            content=ft.Text(
                                month_names[i],
                                size=10 if not self.is_mobile else 8,
                                color=ft.colors.ON_SURFACE,
                                text_align=ft.TextAlign.CENTER if self.is_mobile else ft.TextAlign.LEFT
                            ),
                            # Ajustar espacio
                            padding=ft.padding.only(
                                bottom=5) if self.is_mobile else None
                        )
                    )
                    for i in range(len(month_names)) if i + 1 in monthly_sales.keys()
                ]
            )

            # Crear eje Y
            y_axis = ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i * y_interval,
                        label=ft.Text(
                            f"${i * y_interval:.0f}",
                            size=10 if not self.is_mobile else 8,
                            color=ft.colors.ON_SURFACE
                        )
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
                tooltip_bgcolor=ft.colors.SURFACE_VARIANT,
                max_y=max_value * 1.1,  # Añadir un 10% más para espacio
                interactive=True,
                expand=True
            )

            return ft.Container(
                content=bar_chart,
                height=self.get_chart_height(),
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
                height=self.get_chart_height()
            )

    def build_recent_sales_section(self):
        try:
            # Obtener datos reales de actividad reciente
            # Obtener fecha actual y fecha de hace 30 días
            today = datetime.now()
            thirty_days_ago = today - timedelta(days=30)

            # Obtener ventas recientes
            recent_sales = self.sale_service.get_sales_by_date_range(
                thirty_days_ago, today)

            # Ordenar por fecha (más reciente primero)
            recent_sales.sort(key=lambda x: x.date, reverse=True)

            # Limitar a las 5 ventas más recientes en móvil, 10 en otros dispositivos
            limit = 5 if self.is_mobile else 10
            recent_sales = recent_sales[:limit]

            # Crear contenedor principal con altura adaptativa
            container_height = 350 if self.is_mobile else 400
            content = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                height=container_height
            )

            # Si no hay ventas, mostrar mensaje
            if not recent_sales:
                content.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Icon(
                                    name=ft.icons.INFO,
                                    color=ft.colors.PRIMARY,
                                    size=50
                                ),
                                ft.Text(
                                    "No hay ventas recientes",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.ON_SURFACE,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Text(
                                    "Las ventas recientes se mostrarán aquí",
                                    size=14,
                                    color=ft.colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.CENTER
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=20,
                            alignment=ft.alignment.center
                        ),
                        elevation=0
                    )
                )
                return content

            # Para cada venta, crear una tarjeta expandible
            for sale in recent_sales:
                # Formatear fecha
                date_str = sale.date.strftime("%d/%m/%Y %H:%M")

                # Determinar cliente
                customer_name = sale.customer.name if sale.customer else "Cliente no registrado"

                # Crear tabla de productos
                products_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Producto")),
                        ft.DataColumn(ft.Text("Cantidad")),
                        ft.DataColumn(ft.Text("Precio")),
                        ft.DataColumn(ft.Text("Subtotal"))
                    ],
                    rows=[]
                )

                # Para cada item de la venta, añadir una fila a la tabla
                for item in sale.items:
                    products_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(
                                        item.product.name if item.product else "Producto eliminado")
                                ),
                                ft.DataCell(
                                    ft.Text(str(item.quantity))
                                ),
                                ft.DataCell(
                                    ft.Text(f"${item.unit_price:.2f}")
                                ),
                                ft.DataCell(
                                    ft.Text(f"${item.subtotal:.2f}")
                                )
                            ]
                        )
                    )

                # Crear una tarjeta expandible para cada venta, con diseño adaptado al dispositivo
                if self.is_mobile:
                    # Versión móvil: más compacta, con menos información
                    sale_card = ft.Card(
                        content=ft.Column([
                            # Encabezado - Siempre visible, más compacto
                            ft.ListTile(
                                leading=ft.Container(
                                    content=ft.Icon(ft.icons.SHOPPING_CART,
                                                    color=ft.colors.ON_INVERSE_SURFACE,
                                                    size=16),
                                    bgcolor=ft.colors.PRIMARY,
                                    border_radius=8,
                                    padding=5,
                                    width=26,
                                    height=26
                                ),
                                title=ft.Text(
                                    f"Venta #{sale.id}",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.ON_SURFACE,
                                    size=14
                                ),
                                subtitle=ft.Text(
                                    f"${sale.total_amount:.2f} • {date_str}",
                                    color=ft.colors.ON_SURFACE_VARIANT,
                                    size=12
                                ),
                                trailing=ft.IconButton(
                                    icon=ft.icons.ARROW_FORWARD_IOS,
                                    icon_size=16,
                                    tooltip="Ver detalles",
                                    on_click=lambda _, s=sale.id: self.page.go(
                                        f"/ver_reportes/ventas?id={s}")
                                ),
                                dense=True
                            )
                        ]),
                        elevation=1,
                        margin=ft.margin.only(bottom=5)
                    )
                else:
                    # Versión desktop: completa con detalles expandibles
                    sale_card = ft.Card(
                        content=ft.Column([
                            # Encabezado - Siempre visible
                            ft.ListTile(
                                leading=ft.Container(
                                    content=ft.Icon(
                                        ft.icons.SHOPPING_CART, color=ft.colors.ON_INVERSE_SURFACE),
                                    bgcolor=ft.colors.PRIMARY,
                                    border_radius=8,
                                    padding=8
                                ),
                                title=ft.Text(
                                    f"Venta #{sale.id} por ${sale.total_amount:.2f}",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.ON_SURFACE
                                ),
                                subtitle=ft.Column([
                                    ft.Text(
                                        f"Cliente: {customer_name}", color=ft.colors.ON_SURFACE_VARIANT),
                                    ft.Text(
                                        f"Fecha: {date_str}", color=ft.colors.ON_SURFACE_VARIANT, size=12)
                                ], spacing=2, tight=True),
                                trailing=ft.IconButton(
                                    icon=ft.icons.EXPAND_MORE,
                                    tooltip="Ver detalles",
                                    on_click=lambda e, s=sale.id: self.toggle_sale_details(
                                        e, s)
                                )
                            ),

                            # Contenedor para detalles - Inicialmente oculto
                            ft.Container(
                                content=ft.Column([
                                    ft.Divider(),
                                    ft.Text("Productos:",
                                            weight=ft.FontWeight.BOLD),
                                    products_table,
                                    ft.Row([
                                        ft.Container(expand=True),
                                        ft.FilledButton(
                                            "Ver detalles",
                                            icon=ft.icons.VISIBILITY,
                                            on_click=lambda _, s=sale.id: self.page.go(
                                                f"/ver_reportes/ventas?id={s}")
                                        )
                                    ], alignment=ft.MainAxisAlignment.END)
                                ]),
                                padding=10,
                                visible=False,
                                # Usaremos la key para identificar este contenedor
                                key=f"sale_details_{sale.id}"
                            )
                        ]),
                        elevation=2,
                        margin=ft.margin.only(bottom=10)
                    )

                # Añadir la tarjeta al contenedor principal
                content.controls.append(sale_card)

            return content

        except Exception as e:
            logging.error(
                f"Error construyendo sección de ventas recientes: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)

    def build_recent_inventory_section(self):
        try:
            # Obtener cambios recientes en el inventario, limitados según dispositivo
            limit = 5 if self.is_mobile else 10
            inventory_changes = self.product_service.inventory_history_service.get_recent_history(
                limit=limit)

            # Crear lista de actividades
            activities = []

            for change in inventory_changes:
                # Formatear fecha
                date_str = change.date.strftime(
                    "%d/%m/%Y %H:%M") if not self.is_mobile else change.date.strftime("%d/%m %H:%M")

                # Determinar ícono y color según el tipo de cambio
                icon_name = ft.icons.ARROW_UPWARD
                icon_color = ft.colors.GREEN
                bg_color = ft.colors.GREEN

                if change.change_type == "salida":
                    icon_name = ft.icons.ARROW_DOWNWARD
                    icon_color = ft.colors.RED
                    bg_color = ft.colors.RED
                elif change.change_type == "ajuste":
                    icon_name = ft.icons.SYNC
                    icon_color = ft.colors.BLUE
                    bg_color = ft.colors.BLUE

                # Obtener nombre del producto
                product_name = "Producto no disponible"
                if change.product:
                    product_name = change.product.name

                # Crear descripción del cambio
                if change.change_type == "entrada":
                    activity = f"Entrada de {abs(change.change_amount)} unidades"
                elif change.change_type == "salida":
                    activity = f"Salida de {abs(change.change_amount)} unidades"
                else:
                    activity = f"Ajuste de {change.previous_stock} → {change.new_stock} unidades"

                if self.is_mobile:
                    # Versión móvil: Más compacta, con menos información
                    activities.append(
                        ft.ListTile(
                            leading=ft.Container(
                                content=ft.Icon(
                                    icon_name, color=ft.colors.ON_INVERSE_SURFACE, size=16),
                                bgcolor=bg_color,
                                border_radius=8,
                                padding=5,
                                width=26,
                                height=26
                            ),
                            title=ft.Text(
                                product_name if len(
                                    product_name) < 25 else product_name[:22] + "...",
                                color=ft.colors.ON_SURFACE,
                                size=14
                            ),
                            subtitle=ft.Text(
                                f"{activity} • {date_str}",
                                color=ft.colors.ON_SURFACE_VARIANT,
                                size=12
                            ),
                            dense=True
                        )
                    )
                else:
                    # Versión desktop: Completa con toda la información
                    activities.append(
                        ft.ListTile(
                            leading=ft.Container(
                                content=ft.Icon(
                                    icon_name, color=ft.colors.ON_INVERSE_SURFACE),
                                bgcolor=bg_color,
                                border_radius=8,
                                padding=8
                            ),
                            title=ft.Text(
                                activity, color=ft.colors.ON_SURFACE),
                            subtitle=ft.Column([
                                ft.Text(product_name,
                                        color=ft.colors.ON_SURFACE_VARIANT),
                                ft.Text(
                                    date_str, color=ft.colors.ON_SURFACE_VARIANT, size=12)
                            ], spacing=2, tight=True)
                        )
                    )

            # Si no hay cambios recientes, mostrar mensaje
            if not activities:
                activities.append(
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.icons.INFO, color=ft.colors.PRIMARY),
                        title=ft.Text(
                            "No hay cambios recientes en el inventario", color=ft.colors.ON_SURFACE),
                        subtitle=ft.Text(
                            "Los cambios en el inventario se mostrarán aquí", color=ft.colors.ON_SURFACE_VARIANT)
                    )
                )

            return ft.Column(
                controls=activities,
                scroll=ft.ScrollMode.AUTO,
                spacing=2,
                height=400
            )

        except Exception as e:
            logging.error(
                f"Error construyendo sección de inventario reciente: {str(e)}")
            return ft.Text(f"Error: {str(e)}", color=ft.colors.ERROR)
