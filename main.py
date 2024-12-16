import flet
from flet import Page
from database.connection import init_db, SessionLocal
from pages.PageHome import PageHome
from pages.PageProduct import PageProduct
from pages.PageSupplier import PageSupplier
from pages.PageSupplierForm import PageSupplierForm
from pages.PageCustomer import PageCustomer
from pages.PageCustomerForm import PageCustomerForm
from pages.sales.make_sale import MakeSaleView
from pages.sales.see_sales import SeeSalesView
from pages.auth import LoginView
from pages.auth import RegisterView
from pages.auth import ResetPasswordView
from pages.dashboard.dashboard import DashboardView
from pages.PageSeeSale import SeeSalesView
# Inicializar la base de datos
init_db()

# Crear una sesión
session = SessionLocal()

def main(page: Page):
    page.title = "DiagSoft"
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    
    def route_change(route):
        page.views.clear()
        
        # Verificar autenticación
        token = page.client_storage.get("token")
        public_routes = ["/login", "/register", "/reset-password"]
        
        if not token and page.route not in public_routes:
            page.go("/login")
            return
            
        # Crear vista según la ruta
        view = None
        if page.route == "/login":
            view = LoginView(page, session)
        #elif page.route == "/register":
        #    view = RegisterView(page, session)
        #elif page.route == "/reset-password":
        #    view = ResetPasswordView(page, session)
        elif page.route == "/dashboard":
            view = DashboardView(page, session)
        elif page.route == "/" or page.route == "/home":
            view = PageHome(page)
        elif page.route == "/realizar_venta":
            view = MakeSaleView(page, session)
        elif page.route == "/ver_productos":
            view = PageProduct(page, session)
        elif page.route == "/ver_proveedores":
            view = PageSupplier(page, session)
        elif page.route == "/agregar_proveedor":
            view = PageSupplierForm(page, session, edit_mode=False)
        elif page.route == "/editar_proveedor":
            view = PageSupplierForm(page, session, edit_mode=True)
        elif page.route == "/ver_compradores":
            view = PageCustomer(page, session)
        elif page.route == "/agregar_comprador":
            view = PageCustomerForm(page, session, edit_mode=False)
        elif page.route == "/editar_comprador":
            view = PageCustomerForm(page, session, edit_mode=True)
        elif page.route == "/ver_ventas":
            view = SeeSalesView(page, session)
        
        # Actualizar la página
        if view:
            page.views.append(view)
        page.update()

    page.on_route_change = route_change
    page.go("/login")

if __name__ == "__main__":
    flet.app(target=main, assets_dir="assets")