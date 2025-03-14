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
            self.load_product_data()

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
                 ft.Text("Editar Producto" if self.edit_mode else "Nuevo Producto", weight=ft.FontWeight.BOLD, size=20),
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

            product_data = {
                "name": name,
                "price": price,
                "stock": stock
            }
            
            if self.edit_mode:
                # Obtener el ID del producto a editar
                product_id = self.page.client_storage.get("edit_product_id")
                if product_id:
                    # Actualizar el producto existente
                    self.product_service.update_product(product_id, product_data)
                    show_success_message(self.page, "Producto actualizado exitosamente.")
                    # Regresar a la vista de inventario
                    self.page.client_storage.remove("edit_product_id")
                    self.page.go("/ver_inventario")
            else:
                # Crear un nuevo producto
                self.product_service.create_product(product_data)
                show_success_message(self.page, "Producto agregado exitosamente.")
                self.clear_inputs()
        except ValueError:
            show_error_message(
                self.page, "Por favor ingrese valores numéricos válidos para precio y stock.")
        except Exception as e:
            show_error_message(
                self.page, f"Error al {'actualizar' if self.edit_mode else 'agregar'} el producto: {str(e)}")

    def clear_inputs(self):
        self.name_input.value = ""
        self.price_input.value = ""
        self.stock_input.value = ""
        self.page.update()
    
    def go_back(self, e):
        if self.edit_mode:
            self.page.client_storage.remove("edit_product_id")
        self.page.go("/ver_inventario")

    def load_product_data(self):
        try:
            # Obtener el ID del producto a editar del almacenamiento del cliente
            product_id = self.page.client_storage.get("edit_product_id")
            if product_id:
                # Obtener los datos del producto
                product = self.product_service.get_product_by_id(product_id)
                if product:
                    # Cargar los datos en los campos del formulario
                    self.name_input.value = product.name
                    self.price_input.value = str(product.price)
                    self.stock_input.value = str(product.stock)
                    self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error al cargar los datos del producto: {str(e)}")