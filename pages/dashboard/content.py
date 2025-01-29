import flet as ft
from datetime import datetime
from ui.components.stats_card import StatsCard
from ui.components.charts import LineChart, PieChart


class DashboardContent:
    def __init__(self, page: ft.Page, services):
        self.page = page
        self.sale_service = services['sale_service']
        self.product_service = services['product_service']

    def build(self):
        return ft.Container(
            expand=True,
            content=ft.Column([
                ft.Text(
                    "Dashboard",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                self._build_stats_section(),
                self._build_charts_section(),
                self._build_sales_table()
            ],
                scroll=ft.ScrollMode.AUTO,
                spacing=20),
            padding=20
        )

    def _build_stats_section(self):
        return ft.Row([
            StatsCard(
                title="Ventas Hoy",
                value=self._get_today_sales(),
                icon=ft.icons.TRENDING_UP,
                color=ft.colors.GREEN
            ),
            StatsCard(
                title="Productos Bajos",
                value=self._get_low_stock_count(),
                icon=ft.icons.WARNING,
                color=ft.colors.ORANGE
            ),
            StatsCard(
                title="Clientes Nuevos",
                value=0,
                icon=ft.icons.PERSON_ADD,
                color=ft.colors.BLUE
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_charts_section(self):
        return ft.Row([
            LineChart(title="Ventas últimos 7 días", data=[]),
            PieChart(title="Productos más vendidos", data=[]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_sales_table(self):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Estado")),
            ],
            rows=[]
        )

    def _get_today_sales(self):
        today = datetime.now().date()
        return self.sale_service.get_total_sales_amount(today, today)

    def _get_low_stock_count(self):
        return len([p for p in self.product_service.get_all_products() if p.stock < 10])
