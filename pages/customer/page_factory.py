"""
Factory para crear componentes de compradores sin importaciones circulares
"""

class CustomerPageFactory:
    @staticmethod
    def create_customer_page(page, session, go_back_callback=None):
        """Crea una instancia de PageCustomer"""
        from pages.customer.PageCustomer import PageCustomer
        return PageCustomer(page, session, go_back_callback)
    
    @staticmethod
    def create_customer_form(page, session, edit_mode=False, go_back_callback=None):
        """Crea una instancia de PageCustomerForm"""
        from pages.customer.PageCustomerForm import PageCustomerForm
        return PageCustomerForm(page, session, edit_mode, go_back_callback) 