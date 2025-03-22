import flet as ft
from services.supplierService import SupplierService
from ui.components.data_table import DataTable
from ui.components.alerts import show_error_message, show_success_message
import logging

class PageSupplier(ft.UserControl):
    def __init__(self, page: ft.Page, session, go_back_callback):
        super().__init__()
        self.page = page
        self.session = session
        self.go_back_callback = go_back_callback
        self.supplier_service = SupplierService(session)
        self.is_mobile = self.page.width < 600
        self.all_suppliers = []
        self.table = None
        self.table_container = None
        self.search_field = None
        self.main_content = None
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            self.load_suppliers()

            self.search_field = ft.TextField(
                label="Buscar proveedores",
                prefix_icon=ft.icons.SEARCH,
                width=min(self.page.width * 0.8, 500) if self.is_mobile else 500,
                border_radius=20,
                on_change=self.filter_suppliers,
                hint_text="Ingrese el nombre del proveedor...",
                height=50
            )

            supplier_actions = ft.Row([
                ft.FilledButton(
                    text="Agregar/Editar",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self.add_supplier()
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    tooltip="Volver a Reportes",
                    on_click=lambda _: self.go_back_callback(),
                    icon_color=ft.colors.PRIMARY
                )
            ], wrap=True, spacing=10)

            table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            supplier_data = self.get_supplier_data()
            self.table = DataTable(
                columns=["ID", "Nombre", "Teléfono", "Email", "Dirección", "Acciones"],
                data=supplier_data,
                items_per_page=10,
                on_select=self.edit_supplier,
                on_delete=self.delete_supplier
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
                    ft.Text("Proveedores", size=20 if self.is_mobile else 24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.Text("Gestión de proveedores", size=14 if self.is_mobile else 16, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Container(height=10),
                    supplier_actions,
                    ft.Row([
                        self.search_field,
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            on_click=self.load_suppliers,
                            icon_color=ft.colors.PRIMARY
                        )
                    ]),
                    ft.Container(height=10),
                    self.table_wrapper,
                    ft.Text(f"Total: {len(self.all_suppliers)} proveedores", size=12, text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )

            self.main_content = ft.Container(
                content=content_column,
                padding=10 if self.is_mobile else 20
            )
            
            self.controls = [self.main_content]

        except Exception as e:
            logging.error(f"Error construyendo UI de proveedores: {str(e)}")
            self.controls = [ft.Text(f"Error al cargar los proveedores: {str(e)}", color=ft.colors.ERROR)]

    def load_suppliers(self, e=None):
        try:
            logging.info("Iniciando carga de proveedores")
            self.all_suppliers = self.supplier_service.get_all_suppliers()
            logging.info(f"Proveedores cargados: {len(self.all_suppliers)}")
            if self.table:
                self.table.set_data(self.get_supplier_data())
                logging.info("Datos establecidos en la tabla")
            self.update()
        except Exception as e:
            logging.error(f"Error al cargar proveedores: {str(e)}")
            show_error_message(self.page, f"Error al cargar proveedores: {str(e)}")

    def filter_suppliers(self, e):
        search_text = self.search_field.value.lower()
        filtered = [
            s for s in self.all_suppliers
            if search_text in s.name.lower()
        ] if search_text else self.all_suppliers.copy()
        self.table.set_data([
            {
                "ID": str(s.id),
                "Nombre": s.name,
                "Teléfono": s.phone or "N/A",
                "Email": s.email,
                "Dirección": s.address,
                "supplier": s
            } for s in filtered
        ])

    def get_supplier_data(self):
        return [
            {
                "ID": str(s.id),
                "Nombre": s.name,
                "Teléfono": s.phone or "N/A",
                "Email": s.email,
                "Dirección": s.address,
                "supplier": s
            } for s in self.all_suppliers
        ]

    def delete_supplier(self, row_data):
        supplier = row_data["supplier"]
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"¿Eliminar proveedor {supplier.name}?"),
            content=ft.Text("Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_supplier(supplier))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def confirm_delete_supplier(self, supplier):
        self.supplier_service.delete_supplier(supplier.id)
        self.close_dialog()
        self.load_suppliers()
        show_success_message(self.page, f"Proveedor {supplier.name} eliminado correctamente")

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
    
    def edit_supplier(self, row_data):
        supplier = row_data["supplier"]
        self.page.client_storage.set("edit_supplier_id", supplier.id)
        
        # Usar la factory para crear el formulario
        from pages.supplier.page_factory import SupplierPageFactory
        supplier_form = SupplierPageFactory.create_supplier_form(self.page, self.session, edit_mode=True)
        
        self.controls.clear()
        self.controls.append(supplier_form)
        self.update()

    def add_supplier(self):
        # Usar la factory para crear el formulario
        from pages.supplier.page_factory import SupplierPageFactory
        supplier_form = SupplierPageFactory.create_supplier_form(self.page, self.session)
        
        self.controls.clear()
        self.controls.append(supplier_form)
        self.update()

    def go_back(self):
        self.controls.clear()
        self.controls.append(self.main_content)
        self.update()

    def build(self):
        return ft.Column(self.controls, expand=True)