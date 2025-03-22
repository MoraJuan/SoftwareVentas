"""
Factory para crear componentes de proveedores sin importaciones circulares
"""

class SupplierPageFactory:
    @staticmethod
    def create_supplier_page(page, session, go_back_callback=None):
        """Crea una instancia de PageSupplier"""
        from pages.supplier.PageSupplier import PageSupplier
        return PageSupplier(page, session, go_back_callback)
    
    @staticmethod
    def create_supplier_form(page, session, edit_mode=False, go_back_callback=None):
        """Crea una instancia de PageSupplierForm"""
        from pages.supplier.PageSupplierForm import PageSupplierForm
        return PageSupplierForm(page, session, edit_mode, go_back_callback) 