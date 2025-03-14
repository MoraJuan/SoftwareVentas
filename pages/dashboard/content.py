import flet as ft
from datetime import datetime, timedelta
from ui.components.stats_card import StatsCard
from ui.components.charts import LineChart, PieChart
from ui.components.financial_balance import FinancialBalanceCard
from ui.components.income_expense_chart import IncomeExpenseChart


class DashboardContent:
    def __init__(self, page: ft.Page, services):
        self.page = page
        self.sale_service = services['sale_service']
        self.product_service = services['product_service']
        self.expense_service = services['expense_service']

    def build(self):
        # Cargar datos para las ventas recientes
        self.recent_sales = self._get_recent_sales()
        
        return ft.Container(
            expand=True,
            content=ft.Column([
                # Encabezado con saludo personalizado
                self._build_header_section(),
                
                # Sección de estadísticas rápidas
                self._build_stats_section(),
                
                # Secciones principales en pestañas
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            text="Estado Financiero",
                            icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            content=ft.Container(
                                content=self._build_financial_section(),
                                padding=ft.padding.only(top=15, bottom=5)
                            )
                        ),
                        ft.Tab(
                            text="Análisis de Ventas",
                            icon=ft.icons.INSERT_CHART_OUTLINED,
                            content=ft.Container(
                                content=self._build_charts_section(),
                                padding=ft.padding.only(top=15, bottom=5)
                            )
                        ),
                        ft.Tab(
                            text="Ventas Recientes",
                            icon=ft.icons.RECEIPT_LONG_OUTLINED,
                            content=ft.Container(
                                content=self._build_sales_table_section(),
                                padding=ft.padding.only(top=15, bottom=5)
                            )
                        ),
                    ],
                    expand=1
                )
            ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
                expand=True),
            padding=ft.padding.only(left=20, right=20, top=10, bottom=10)
        )

    def _build_header_section(self):
        # Obtener la hora actual para personalizar el saludo
        current_hour = datetime.now().hour
        greeting = "Buenos días" if 5 <= current_hour < 12 else "Buenas tardes" if 12 <= current_hour < 19 else "Buenas noches"
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        f"{greeting}",
                        size=16,
                        color=ft.colors.GREY_700
                    ),
                    ft.Text(
                        "Panel de Control",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.PRIMARY
                    )
                ], spacing=2),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            name=ft.icons.CALENDAR_TODAY_ROUNDED,
                            color=ft.colors.PRIMARY,
                            size=20
                        ),
                        ft.Text(
                            datetime.now().strftime("%d de %B, %Y"),
                            size=14,
                            color=ft.colors.GREY_700
                        )
                    ], spacing=5),
                    padding=ft.padding.all(10),
                    border_radius=20,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.PRIMARY)
                )
            ]),
            margin=ft.margin.only(bottom=15)
        )

    def _build_stats_section(self):
        return ft.Container(
            content=ft.Row([
                StatsCard(
                    title="Ventas Hoy",
                    value=self._get_today_sales(),
                    icon=ft.icons.TRENDING_UP_ROUNDED,
                    color=ft.colors.GREEN
                ),
                StatsCard(
                    title="Productos Bajos",
                    value=self._get_low_stock_count(),
                    icon=ft.icons.INVENTORY_2_ROUNDED,
                    color=ft.colors.AMBER
                ),
                StatsCard(
                    title="Clientes Nuevos",
                    value=0,
                    icon=ft.icons.PERSON_ADD_ROUNDED,
                    color=ft.colors.BLUE
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.margin.only(bottom=10)
        )

    def _build_financial_section(self):
        return ft.Row([
            FinancialBalanceCard(self.sale_service, self.expense_service),
            IncomeExpenseChart(self.sale_service, self.expense_service)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_charts_section(self):
        return ft.Row([
            LineChart(title="Ventas últimos 7 días", data=[]),
            PieChart(title="Productos más vendidos", data=[]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_sales_table_section(self):
        return ft.Container(
            content=self._build_sales_table(),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.with_opacity(0.02, ft.colors.BLACK)
        )

    def _build_sales_table(self):
        # Crear filas para la tabla
        rows = []
        
        # Agregar ventas recientes a la tabla
        for sale in self.recent_sales:
            # Determinar el color del estado
            status_color = ft.colors.GREEN if sale.status == "completed" else ft.colors.AMBER
            
            # Formatear fecha
            date_formatted = sale.date.strftime("%d/%m/%Y") if hasattr(sale, 'date') and sale.date else "N/A"
            
            # Obtener nombre del cliente
            customer_name = sale.customer.name if hasattr(sale, 'customer') and sale.customer else "Cliente desconocido"
            
            # Crear fila
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(sale.id))),
                    ft.DataCell(ft.Text(customer_name)),
                    ft.DataCell(ft.Text(f"${sale.total_amount:.2f}")),
                    ft.DataCell(ft.Text(date_formatted)),
                    ft.DataCell(ft.Container(
                        ft.Text(
                            "Completada" if sale.status == "completed" else "Pendiente",
                            color=ft.colors.WHITE,
                            size=12,
                            weight=ft.FontWeight.W_500
                        ),
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        border_radius=15,
                        bgcolor=status_color,
                        alignment=ft.alignment.center
                    ))
                ]
            )
            rows.append(row)
            
        # Si no hay ventas, mostrar mensaje informativo
        if not rows:
            return ft.Column([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=[],
                    border=None,
                    vertical_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.BLACK)),
                    horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.BLACK)),
                    heading_row_height=40,
                    data_row_max_height=50,
                    column_spacing=10
                ),
                ft.Container(
                    content=ft.Text(
                        "No hay ventas recientes para mostrar",
                        italic=True,
                        color=ft.colors.GREY_600
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ])
            
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            border=None,
            vertical_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.BLACK)),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.BLACK)),
            heading_row_height=40,
            data_row_max_height=50,
            column_spacing=10
        )

    def _get_today_sales(self):
        today = datetime.now().date()
        return self.sale_service.get_total_sales_amount(today, today)

    def _get_low_stock_count(self):
        return len([p for p in self.product_service.get_all_products() if p.stock < 10])
        
    def _get_recent_sales(self):
        # Obtener ventas de los últimos 7 días
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        try:
            sales = self.sale_service.get_sales_by_date_range(start_date, end_date)
            # Limitar a las 5 ventas más recientes
            return sorted(sales, key=lambda s: s.date, reverse=True)[:5]
        except Exception as e:
            print(f"Error al obtener ventas recientes: {str(e)}")
            return []
