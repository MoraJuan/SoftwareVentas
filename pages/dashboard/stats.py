import flet as ft
from datetime import datetime
from services.saleService import SaleService
from services.productService import ProductService
from ui.components.stats_card import StatsCard

def create_stats_row(sale_service: SaleService, product_service: ProductService):
    today = datetime.now().date()
    today_sales = sale_service.get_total_sales_amount(today, today)
    low_stock_count = len([p for p in product_service.get_all_products() if p.stock < 10])
    
    return ft.Row([
        StatsCard(
            title="Ventas Hoy",
            value=f"${today_sales:.2f}",
            icon=ft.icons.TRENDING_UP,
            color=ft.colors.GREEN
        ),
        StatsCard(
            title="Productos Bajos",
            value=low_stock_count,
            icon=ft.icons.WARNING,
            color=ft.colors.ORANGE
        ),
        StatsCard(
            title="Clientes Nuevos",
            value="0",
            icon=ft.icons.PERSON_ADD,
            color=ft.colors.BLUE
        ),
    ])