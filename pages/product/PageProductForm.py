import flet as ft
from sqlalchemy.orm import Session
from services.productService import ProductService
from services.categoryService import CategoryService
from services.supplierService import SupplierService
from ui.components.alerts import show_success_message, show_error_message
from datetime import datetime
from models.Product import Product

class PageProductForm(ft.View):
    def __init__(self, page: ft.Page, session: Session, edit_mode=False):
        super().__init__(route="/agregar_producto", controls=[], padding=20)
        self.page = page
        self.session = session
        self.edit_mode = edit_mode
        self.product_service = ProductService(session)
        self.category_service = CategoryService(session)
        self.supplier_service = SupplierService(session)
        self.page.title = "Agregar Producto" if not edit_mode else "Editar Producto"
        
        # Estado para el producto seleccionado
        self.selected_product = None
        
        # Cargar categorías
        self.categories = self.category_service.get_active_categories()
        
        # Cargar proveedores
        self.suppliers = self.supplier_service.get_all_suppliers()
        
        self.build_ui()

    def build_ui(self):
        self.controls = [
            self.create_form_layout()
        ]
        
        if self.edit_mode:
            self.load_product_data()

    def create_form_layout(self):
        # Información básica del producto
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
        
        # Información adicional del producto
        self.description_input = ft.TextField(
            label="Descripción",
            width=300,
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        # Dropdown para categorías
        category_options = [ft.dropdown.Option("0", "Seleccione una categoría")]
        
        # Ordenar categorías por nombre antes de añadirlas al dropdown
        sorted_categories = sorted(self.categories, key=lambda cat: cat.name)
        
        for category in sorted_categories:
            category_options.append(ft.dropdown.Option(str(category.id), category.name))
            
        self.category_input = ft.Dropdown(
            label="Categoría",
            width=300,
            options=category_options,
            value="0"  # Valor por defecto
        )
        
        # Dropdown para proveedores
        supplier_options = [ft.dropdown.Option("0", "Seleccione un proveedor")]
        sorted_suppliers = sorted(self.suppliers, key=lambda sup: sup.name)
        for supplier in sorted_suppliers:
            supplier_options.append(ft.dropdown.Option(str(supplier.id), supplier.name))
        self.supplier_input = ft.Dropdown(
            label="Proveedor",
            width=300,
            options=supplier_options,
            value="0"  # Valor por defecto
        )
        
        # Botón para gestionar categorías
        self.manage_categories_button = ft.OutlinedButton(
            text="Gestionar Categorías",
            icon=ft.icons.CATEGORY,
            on_click=lambda _: self.page.go("/categorias")
        )
        
        # Otros campos
        self.barcode_input = ft.TextField(
            label="Código de Barras",
            width=300,
        )
        self.code_input = ft.TextField(
            label="Código Interno",
            width=300,
        )
        
        # Ajustes de inventario
        self.adjustment_input = ft.TextField(
            label="Cantidad a ajustar",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0"
        )
        self.reason_input = ft.TextField(
            label="Motivo del ajuste",
            width=300,
            hint_text="Razón del ajuste de inventario"
        )

        # Botones de acción básicos
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
        
        # Botones para ajuste de inventario
        self.add_stock_button = ft.FilledButton(
            text="Añadir Stock",
            icon=ft.icons.ADD,
            on_click=self.add_stock,
            disabled=not self.edit_mode
        )
        self.remove_stock_button = ft.FilledTonalButton(
            text="Reducir Stock",
            icon=ft.icons.REMOVE,
            on_click=self.remove_stock,
            disabled=not self.edit_mode
        )
        self.set_stock_button = ft.OutlinedButton(
            text="Ajustar a Valor",
            icon=ft.icons.SETTINGS,
            on_click=self.adjust_stock,
            disabled=not self.edit_mode
        )

        # Crear un diseño en tabs para organizar mejor la información
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Información Básica",
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Información Básica del Producto", weight=ft.FontWeight.BOLD, size=16),
                            self.name_input,
                            self.price_input,
                            self.stock_input,
                            ft.Row([
                                self.cancel_button,
                                self.save_button
                            ], spacing=10)
                        ], spacing=20),
                        padding=20
                    )
                ),
                ft.Tab(
                    text="Información Adicional",
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Detalles Adicionales", weight=ft.FontWeight.BOLD, size=16),
                            self.description_input,
                            ft.Row([
                                ft.Column([
                                    self.category_input,
                                ], expand=True),
                                ft.Column([
                                    ft.Container(height=25),  # Espaciador para alinear con el dropdown
                                    self.manage_categories_button,
                                ])
                            ]),
                            self.barcode_input,
                            self.supplier_input,
                            self.code_input,
                            ft.Row([
                                self.cancel_button,
                                self.save_button
                            ], spacing=10)
                        ], spacing=20),
                        padding=20
                    )
                ),
                ft.Tab(
                    text="Gestión de Inventario",
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Ajuste de Inventario", weight=ft.FontWeight.BOLD, size=16),
                            self.adjustment_input,
                            self.reason_input,
                            ft.Row([
                                self.add_stock_button,
                                self.remove_stock_button,
                                self.set_stock_button
                            ], spacing=10),
                            ft.Container(height=20),
                            ft.Row([
                                self.cancel_button
                            ], spacing=10)
                        ], spacing=20),
                        padding=20
                    )
                ),
            ],
        )

        return ft.Column([
            ft.Text("Editar Producto" if self.edit_mode else "Nuevo Producto", weight=ft.FontWeight.BOLD, size=20),
            tabs
        ])

    def add_product(self, e):
        try:
            name = self.name_input.value
            price = float(self.price_input.value or 0)
            stock = int(self.stock_input.value or 0)
            description = self.description_input.value
            category_id = int(self.category_input.value)
            supplier_id = int(self.supplier_input.value)
            barcode = self.barcode_input.value
            code = self.code_input.value

            if not name:
                show_error_message(
                    self.page, "El nombre del producto es obligatorio.")
                return

            product_data = {
                "name": name,
                "price": price,
                "stock": stock,
                "description": description,
                "category_id": category_id,
                "supplier_id": supplier_id,
                "barcode": barcode,
                "code": code
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
        self.description_input.value = ""
        self.category_input.value = "0"
        self.barcode_input.value = ""
        self.supplier_input.value = "0"
        self.code_input.value = ""
        self.adjustment_input.value = "0"
        self.reason_input.value = ""
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
                    self.selected_product = product
                    # Cargar los datos en los campos del formulario
                    self.name_input.value = product.name
                    self.price_input.value = str(product.price)
                    self.stock_input.value = str(product.stock)
                    self.description_input.value = product.description or ""
                    
                    # Manejar la categoría - podría ser un ID o un nombre
                    if product.category_id:
                        self.category_input.value = str(product.category_id)
                    else:
                        # Si no es un ID, buscar la categoría por nombre o usar el valor por defecto
                        found = False
                        for category in self.categories:
                            if category.name == product.category:
                                self.category_input.value = str(category.id)
                                found = True
                                break
                        if not found:
                            self.category_input.value = "0"  # Valor por defecto si no se encuentra
                    
                    if product.supplier_id:
                        self.supplier_input.value = str(product.supplier_id)
                    
                    self.barcode_input.value = product.barcode or ""
                    self.code_input.value = product.code or ""
                    
                    # Habilitar los botones de ajuste de inventario
                    self.add_stock_button.disabled = False
                    self.remove_stock_button.disabled = False
                    self.set_stock_button.disabled = False
                    
                    self.page.update()
        except Exception as e:
            show_error_message(self.page, f"Error al cargar los datos del producto: {str(e)}")
    
    def add_stock(self, e):
        """Añade stock al producto"""
        if not self.selected_product:
            show_error_message(self.page, "Debe seleccionar un producto primero")
            return
            
        try:
            adjustment_amount = int(self.adjustment_input.value or 0)
            reason = self.reason_input.value or "Ajuste manual"
            
            if adjustment_amount <= 0:
                show_error_message(self.page, "La cantidad a añadir debe ser mayor a cero")
                return
                
            new_stock = self.selected_product.stock + adjustment_amount
            
            # Actualizar stock en la base de datos
            self.product_service.update_stock(
                self.selected_product.id,
                new_stock,
                reason,
                "add",
                adjustment_amount
            )
            
            # Actualizar el campo de stock en el formulario
            self.stock_input.value = str(new_stock)
            self.adjustment_input.value = "0"
            self.reason_input.value = ""
            self.page.update()
            
            show_success_message(
                self.page,
                f"Stock actualizado: {self.selected_product.stock} → {new_stock}"
            )
            
            # Actualizar el producto seleccionado
            self.selected_product = self.product_service.get_product_by_id(self.selected_product.id)
            
        except ValueError:
            show_error_message(self.page, "Por favor ingrese un valor numérico válido")
        except Exception as e:
            show_error_message(self.page, f"Error al añadir stock: {str(e)}")
    
    def remove_stock(self, e):
        """Reduce stock del producto"""
        if not self.selected_product:
            show_error_message(self.page, "Debe seleccionar un producto primero")
            return
            
        try:
            adjustment_amount = int(self.adjustment_input.value or 0)
            reason = self.reason_input.value or "Ajuste manual"
            
            if adjustment_amount <= 0:
                show_error_message(self.page, "La cantidad a reducir debe ser mayor a cero")
                return
                
            if adjustment_amount > self.selected_product.stock:
                show_error_message(self.page, "No puede reducir más stock del disponible")
                return
                
            new_stock = self.selected_product.stock - adjustment_amount
            
            # Actualizar stock en la base de datos
            self.product_service.update_stock(
                self.selected_product.id,
                new_stock,
                reason,
                "remove",
                adjustment_amount
            )
            
            # Actualizar el campo de stock en el formulario
            self.stock_input.value = str(new_stock)
            self.adjustment_input.value = "0"
            self.reason_input.value = ""
            self.page.update()
            
            show_success_message(
                self.page,
                f"Stock actualizado: {self.selected_product.stock} → {new_stock}"
            )
            
            # Actualizar el producto seleccionado
            self.selected_product = self.product_service.get_product_by_id(self.selected_product.id)
            
        except ValueError:
            show_error_message(self.page, "Por favor ingrese un valor numérico válido")
        except Exception as e:
            show_error_message(self.page, f"Error al reducir stock: {str(e)}")
    
    def adjust_stock(self, e):
        """Ajusta el stock a un valor específico"""
        if not self.selected_product:
            show_error_message(self.page, "Debe seleccionar un producto primero")
            return
            
        try:
            new_stock = int(self.adjustment_input.value or 0)
            reason = self.reason_input.value or "Ajuste manual a valor específico"
            
            if new_stock < 0:
                show_error_message(self.page, "El stock no puede ser negativo")
                return
                
            old_stock = self.selected_product.stock
            adjustment_amount = abs(new_stock - old_stock)
            adjustment_type = "add" if new_stock > old_stock else "remove" if new_stock < old_stock else "set"
            
            # Actualizar stock en la base de datos
            self.product_service.update_stock(
                self.selected_product.id,
                new_stock,
                reason,
                adjustment_type,
                adjustment_amount
            )
            
            # Actualizar el campo de stock en el formulario
            self.stock_input.value = str(new_stock)
            self.adjustment_input.value = "0"
            self.reason_input.value = ""
            self.page.update()
            
            show_success_message(
                self.page,
                f"Stock ajustado: {old_stock} → {new_stock}"
            )
            
            # Actualizar el producto seleccionado
            self.selected_product = self.product_service.get_product_by_id(self.selected_product.id)
            
        except ValueError:
            show_error_message(self.page, "Por favor ingrese un valor numérico válido")
        except Exception as e:
            show_error_message(self.page, f"Error al ajustar stock: {str(e)}")
    
    def show_snackbar(self, message, color=None):
        """Muestra un mensaje en la parte inferior de la pantalla"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color or ft.colors.SURFACE_VARIANT
        )
        self.page.snack_bar.open = True
        self.page.update()