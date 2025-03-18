import flet as ft
from flet import Theme, ThemeMode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os
import logging

from pages.dashboard.dashboard import DashboardView
from pages.reports.PageReports import PageReports
from pages.reports.PageSeeSaleReports import SeeSalesView
from pages.expenses.PageExpense import PageExpense
from pages.sales.PageSales import PageSales
from pages.sales.make_sale import MakeSaleView
from pages.inventory.PageInventory import PageInventory
from pages.inventory.InventoryManagementPage import InventoryManagementPage
from pages.inventory.InventoryHistoryPage import InventoryHistoryPage
from pages.product.PageProductForm import PageProductForm
from pages.product.PageProduct import PageProduct
from pages.supplier.PageSupplierForm import PageSupplierForm
from pages.supplier.PageSupplier import PageSupplier
from pages.customer.PageCustomer import PageCustomer
from pages.customer.PageCustomerForm import PageCustomerForm
from pages.suppliers.PageSuppliers import PageSuppliers
from pages.auth.login import LoginView
from pages.auth.register import RegisterView

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    try:
        # Configurar la página
        page.title = "Sistema de Ventas"
        # Usar la nueva API para configurar la ventana
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        page.theme_mode = ThemeMode.LIGHT
        page.padding = 0
        page.update()
        
        # Para forzar el inicio de sesión, descomenta la siguiente línea
        # page.client_storage.remove("token")

        # Crear conexión a la base de datos
        engine = create_engine('sqlite:///ventas.db')
        Session = sessionmaker(bind=engine)
        session = Session()

        # Cargar preferencia de tema guardada
        def load_theme_preference():
            try:
                if os.path.exists('theme_preference.json'):
                    with open('theme_preference.json', 'r') as f:
                        data = json.load(f)
                        return data.get('theme_mode', 'light')
                return 'light'
            except Exception as e:
                logger.error(f"Error al cargar preferencia de tema: {str(e)}")
                return 'light'

        # Guardar preferencia de tema
        def save_theme_preference(theme_mode):
            try:
                with open('theme_preference.json', 'w') as f:
                    json.dump({'theme_mode': theme_mode}, f)
            except Exception as e:
                logger.error(f"Error al guardar preferencia de tema: {str(e)}")

        # Función para cambiar el tema
        def toggle_theme():
            try:
                page.theme_mode = ThemeMode.DARK if page.theme_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
                save_theme_preference('dark' if page.theme_mode == ThemeMode.DARK else 'light')
                page.update()
            except Exception as e:
                logger.error(f"Error al cambiar tema: {str(e)}")

        # Hacer la función de tema disponible globalmente
        page.toggle_theme = toggle_theme

        # Establecer tema inicial desde preferencia guardada
        theme_preference = load_theme_preference()
        page.theme_mode = ThemeMode.DARK if theme_preference == 'dark' else ThemeMode.LIGHT
        page.update()

        # Función para verificar autenticación
        def is_authenticated():
            # Verificar si hay un token almacenado
            token = page.client_storage.get("token")
            return token is not None

        # Función para cambiar de vista
        def route_change(route):
            try:
                page.views.clear()
                
                # Rutas públicas que no requieren autenticación
                public_routes = ["/login", "/register"]
                
                # Si no está autenticado y no es una ruta pública, redirigir a login
                if not is_authenticated() and page.route not in public_routes:
                    logger.info("Usuario no autenticado, redirigiendo a login")
                    page.go("/login")
                    return
                
                # Crear vista según la ruta
                if page.route == "/login":
                    logger.info("Cargando vista de login")
                    page.views.append(LoginView(page, session))
                elif page.route == "/register":
                    logger.info("Cargando vista de registro")
                    page.views.append(RegisterView(page, session))
                elif page.route == "/":
                    logger.info("Cargando vista de dashboard")
                    page.views.append(DashboardView(page, session))
                elif page.route == "/ver_reportes":
                    logger.info("Cargando vista de reportes")
                    page.views.append(PageReports(page, session))
                elif page.route == "/ver_reportes/ventas":
                    logger.info("Cargando vista de reportes de ventas")
                    page.views.append(SeeSalesView(page, session))
                elif page.route == "/ver_reportes/gastos":
                    logger.info("Cargando vista de gastos")
                    page.views.append(PageExpense(page, session))
                elif page.route == "/ver_ventas":
                    logger.info("Cargando vista de ventas")
                    page.views.append(PageSales(page, session))
                elif page.route == "/realizar_venta":
                    logger.info("Cargando vista de realizar venta")
                    page.views.append(MakeSaleView(page, session))
                elif page.route == "/ver_inventario":
                    logger.info("Cargando vista de inventario")
                    page.views.append(PageInventory(page, session))
                elif page.route == "/gestionar_inventario":
                    logger.info("Cargando vista de gestión de inventario")
                    page.views.append(InventoryManagementPage(page, session))
                elif page.route == "/historial_inventario":
                    logger.info("Cargando vista de historial de inventario")
                    page.views.append(InventoryHistoryPage(page, session))
                elif page.route == "/agregar_producto":
                    logger.info("Cargando vista de agregar producto")
                    page.views.append(PageProductForm(page, session))
                elif page.route == "/editar_producto":
                    logger.info("Cargando vista de editar producto")
                    page.views.append(PageProductForm(page, session, edit_mode=True))
                elif page.route == "/ver_productos":
                    logger.info("Redirigiendo a vista de inventario")
                    page.go("/ver_inventario")
                    return
                elif page.route == "/ajustar_stock":
                    logger.info("Redirigiendo a vista de gestión de inventario")
                    page.go("/gestionar_inventario")
                    return
                elif page.route == "/ver_proveedores":
                    logger.info("Cargando vista de proveedores")
                    page.views.append(PageSuppliers(page, session))
                elif page.route == "/agregar_proveedor":
                    logger.info("Cargando vista de agregar proveedor")
                    page.views.append(PageSupplierForm(page, session))
                elif page.route == "/editar_proveedor":
                    logger.info("Cargando vista de editar proveedor")
                    page.views.append(PageSupplierForm(page, session, edit_mode=True))
                elif page.route == "/ver_compradores":
                    logger.info("Cargando vista de compradores")
                    page.views.append(PageCustomer(page, session))
                elif page.route == "/agregar_comprador":
                    logger.info("Cargando vista de agregar comprador")
                    page.views.append(PageCustomerForm(page, session))
                elif page.route == "/editar_comprador":
                    logger.info("Cargando vista de editar comprador")
                    page.views.append(PageCustomerForm(page, session, edit_mode=True))
                else:
                    # Si la ruta no existe, redirigir al dashboard o login según autenticación
                    logger.info(f"Ruta no encontrada: {page.route}")
                    if is_authenticated():
                        page.views.append(DashboardView(page, session))
                    else:
                        page.views.append(LoginView(page, session))
                    
                page.update()
                
            except Exception as e:
                logger.error(f"Error en cambio de ruta: {str(e)}")
                # En caso de error, mostrar el dashboard o login según autenticación
                page.views.clear()
                if is_authenticated():
                    page.views.append(DashboardView(page, session))
                else:
                    page.views.append(LoginView(page, session))
                page.update()

        # Función para manejar el botón de retroceso
        def view_pop(view):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        # Configurar manejadores de eventos
        page.on_route_change = route_change
        page.on_view_pop = view_pop

        # Iniciar en login o dashboard según autenticación
        if is_authenticated():
            logger.info("Usuario autenticado, iniciando en dashboard")
            page.go('/')
        else:
            logger.info("Usuario no autenticado, iniciando en login")
            page.go('/login')

    except Exception as e:
        logger.error(f"Error en la inicialización de la aplicación: {str(e)}")
        # Mostrar mensaje de error en la página
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=64),
                    ft.Text(
                        "Error al iniciar la aplicación",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Text(
                        str(e),
                        color=ft.colors.ON_SURFACE
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center
            )
        )
        page.update()

if __name__ == '__main__':
    ft.app(target=main)
