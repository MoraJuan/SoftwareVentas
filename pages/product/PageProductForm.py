import flet as ft
from sqlalchemy.orm import Session
from services.productService import ProductService
from ui.components.alerts import show_success_message, show_error_message

class PageProductForm(ft.View):
    def __init__(self, page: ft.Page, session: Session, edit_mode=False):
        super().__init__(route="/agregar_producto", controls=[], padding=20)
        self.page = page
        self.session = session
        self.edit_mode = edit_mode
        self.product_service = ProductService(session)
        self.page.title = "Agregar Producto" if not edit_mode else "Editar Producto"
        self.build_ui()

    def build_ui(self):
        self.controls = [
            self.create_form_layout()
        ]
        
        if self.edit_mode:
            self.load_supplier_data()

    def create_form_layout(self):
        self.name_input = ft.TextField(
            label="Nombre del Producto",
            width=300,
        )
        self.price_input = ft.TextField(
            label="Precio",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.stock_input = ft.TextField(
            label="Stock",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.cancel_button = ft.ElevatedButton(
            text="Volver",
            icon=ft.icons.CANCEL,
            on_click=self.go_back
        )
        self.save_button = ft.ElevatedButton(
            text="Guardar",
            icon=ft.icons.SAVE,
            on_click=self.add_product
        )

        return ft.Row([
            ft.Column([
                 ft.Text("Editar Proveedor" if self.edit_mode else "Nuevo Proveedor", weight=ft.FontWeight.BOLD, size=20),
                self.name_input,
                self.price_input,
                self.stock_input,
                ft.Row([
                        self.cancel_button,
                        self.save_button
                    ], spacing=10)
            ], spacing=20)
        ])

    def add_product(self, e):
        try:
            name = self.name_input.value
            price = float(self.price_input.value)
            stock = int(self.stock_input.value)

            if not name:
                show_error_message(
                    self.page, "El nombre del producto es obligatorio.")
                return

            new_product = {
                "name": name,
                "price": price,
                "stock": stock
            }
            self.product_service.create_product(new_product)
            show_success_message(self.page, "Producto agregado exitosamente.")
            self.clear_inputs()
        except ValueError:
            show_error_message(
                self.page, "Por favor ingrese valores numéricos válidos para precio y stock.")
        except Exception as e:
            show_error_message(
                self.page, f"Error al agregar el producto: {str(e)}")

    def clear_inputs(self):
        self.name_input.value = ""
        self.price_input.value = ""
        self.stock_input.value = ""
        self.page.update()
    
    def go_back(self, e):
        if self.edit_mode:
            self.page.client_storage.remove("edit_supplier_id")
        self.page.go("/ver_productos")