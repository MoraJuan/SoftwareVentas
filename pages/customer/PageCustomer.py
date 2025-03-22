import flet as ft
from services.customerService import CustomerService  # Asumimos este servicio
from ui.components.data_table import DataTable
from ui.components.alerts import show_error_message, show_success_message
import logging

class PageCustomer(ft.UserControl):
    def __init__(self, page: ft.Page, session, go_back_callback):
        super().__init__()
        self.page = page
        self.session = session
        self.go_back_callback = go_back_callback
        self.customer_service = CustomerService(session)
        self.is_mobile = self.page.width < 600
        self.all_customers = []
        self.table = None
        self.table_container = None
        self.search_field = None
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            self.load_customers()

            self.search_field = ft.TextField(
                label="Buscar clientes",
                prefix_icon=ft.icons.SEARCH,
                width=min(self.page.width * 0.8, 500) if self.is_mobile else 500,
                border_radius=20,
                on_change=self.filter_customers,
                hint_text="Ingrese el nombre del cliente...",
                height=50
            )

            customer_actions = ft.Row([
                ft.FilledButton(
                    text="Agregar/Editar",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self.add_customer()
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    tooltip="Volver a Reportes",
                    on_click=lambda _: self.go_back_callback(),
                    icon_color=ft.colors.PRIMARY
                )
            ], wrap=True, spacing=10)

            table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            customer_data = self.get_customer_data()
            self.table = DataTable(
                columns=["ID", "Nombre", "Teléfono", "Email", "Dirección", "Acciones"],
                data=customer_data,
                items_per_page=10,
                on_select=self.edit_customer,
                on_delete=self.delete_customer
            )
            self.table_container = ft.Column(
                [self.table],
                width=table_width,
                scroll=ft.ScrollMode.AUTO if self.is_mobile else None,
                expand=True,
                spacing=0
            )
            self.table_wrapper = ft.Container(
                content=self.table_container,
                padding=10,
                border_radius=5,
                bgcolor=ft.colors.SURFACE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK)
                )
            )

            content_column = ft.Column(
                [
                    ft.Text("Clientes", size=20 if self.is_mobile else 24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.Text("Gestión de clientes", size=14 if self.is_mobile else 16, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Container(height=10),
                    customer_actions,
                    ft.Row([
                        self.search_field,
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            on_click=self.load_customers,
                            icon_color=ft.colors.PRIMARY
                        )
                    ]),
                    ft.Container(height=10),
                    self.table_wrapper,
                    ft.Text(f"Total: {len(self.all_customers)} clientes", size=12, text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )

            self.controls = [
                ft.Container(
                    content=content_column,
                    padding=10 if self.is_mobile else 20
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de clientes: {str(e)}")
            self.controls = [ft.Text(f"Error al cargar los clientes: {str(e)}", color=ft.colors.ERROR)]

    def load_customers(self, e=None):
        try:
            logging.info("Iniciando carga de clientes")
            self.all_customers = self.customer_service.get_all_customers()
            logging.info(f"Clientes cargados: {len(self.all_customers)}")
            if self.table:
                self.table.set_data(self.get_customer_data())
                logging.info("Datos establecidos en la tabla")
            self.update()
        except Exception as e:
            logging.error(f"Error al cargar clientes: {str(e)}")
            show_error_message(self.page, f"Error al cargar clientes: {str(e)}")

    def filter_customers(self, e):
        search_text = self.search_field.value.lower()
        filtered = [
            c for c in self.all_customers
            if search_text in c.name.lower()
        ] if search_text else self.all_customers.copy()
        self.table.set_data([
            {
                "ID": str(c.id),
                "Nombre": c.name,
                "Teléfono": c.phone or "N/A",
                "Email": c.email,
                "Dirección": c.address,
                "customer": c
            } for c in filtered
        ])

    def get_customer_data(self):
        return [
            {
                "ID": str(c.id),
                "Nombre": c.name,
                "Teléfono": c.phone or "N/A",
                "Email": c.email,
                "Dirección": c.address,
                "customer": c
            } for c in self.all_customers
        ]

    # def edit_customer(self, row_data):
    #     customer = row_data["customer"]
    #     self.page.client_storage.set("edit_customer_id", customer.id)
    #     self.page.go("/editar_cliente")
    
    def edit_customer(self, row_data):
        customer = row_data["customer"]
        self.page.client_storage.set("edit_customer_id", customer.id)
        
        # Usar la factory para crear el formulario
        from pages.customer.page_factory import CustomerPageFactory
        customer_form = CustomerPageFactory.create_customer_form(self.page, self.session, edit_mode=True)
        
        self.controls.clear()
        self.controls.append(customer_form)
        self.update()

    def delete_customer(self, row_data):
        customer = row_data["customer"]
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"¿Eliminar cliente {customer.name}?"),
            content=ft.Text("Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_customer(customer))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def confirm_delete_customer(self, customer):
        self.customer_service.delete_customer(customer.id)
        self.close_dialog()
        self.load_customers()
        show_success_message(self.page, f"Cliente {customer.name} eliminado correctamente")

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.update()
        elif self.table_container:
            new_table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            self.table_container.width = new_table_width
            self.table_container.scroll = ft.ScrollMode.AUTO if self.is_mobile else None
            self.search_field.width = min(self.page.width * 0.8, 500) if self.is_mobile else 500
            self.update()
        
    def add_customer(self):
        # Usar la factory para crear el formulario
        from pages.customer.page_factory import CustomerPageFactory
        customer_form = CustomerPageFactory.create_customer_form(self.page, self.session)
        
        self.controls.clear()
        self.controls.append(customer_form)
        self.update()   

    def build(self):
        return ft.Column(self.controls, expand=True)