import flet as ft
from services.saleService import SaleService
from services.productService import ProductService
from ..stats import create_stats_row

def create_stats_section(session):
    sale_service = SaleService(session)
    product_service = ProductService(session)
    return create_stats_row(sale_service, product_service)