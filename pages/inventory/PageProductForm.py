import flet as ft
from services.productService import ProductService
from ui.components.data_table import DataTable
from ui.components.alerts import show_error_message, show_success_message
import logging
from pages.categories import PageCategory
from services.categoryService import CategoryService
from services.subcategoryService import SubcategoryService
from services.supplierService import SupplierService


class PageProductForm(ft.UserControl):
    def __init__(self, page: ft.Page, session, edit_mode=False):
        super().__init__()
        self.page = page
        self.session = session
        self.is_mobile = self.page.width < 600
        self.edit_mode = edit_mode
        self.all_products = []
        self.table = None
        self.table_container = None
        self.search_field = None
        
        # Inicializar servicios
        self.product_service = ProductService(session)
        self.category_service = CategoryService(session)
        self.subcategory_service = SubcategoryService(session)
        self.supplier_service = SupplierService(session)
        
        # Cargar datos
        self.categories = self.category_service.get_active_categories()
        self.subcategories = []
        self.suppliers = self.supplier_service.get_all_suppliers()
        
        # Configurar eventos
        self.page.on_resize = self.handle_resize
        
        # Construir UI
        self.build_ui()
        
        # Cargar datos si estamos en modo de edición
        if self.edit_mode:
            self.load_product_data()

    def handle_resize(self, e):
        # Actualizar el estado móvil
        self.is_mobile = self.page.width < 600
        # Reconstruir la UI
        self.build_ui()
        self.page.update()

    def build_ui(self):
        try:
            if self.edit_mode:
                title = "Editar producto"
            else:
                title = "Agregar producto"

            content_column = ft.Column([
                ft.Text(
                        title,
                        size=20 if self.is_mobile else 24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                self.create_form_layout()
                ])

            self.controls = [
                ft.Container(
                    content=content_column,
                    padding=10 if self.is_mobile else 20
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de inventario: {str(e)}")
            self.controls = [ft.Text(f"Error al cargar el inventario: {str(e)}", color=ft.colors.ERROR)]
        
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
        category_options = [ft.dropdown.Option(
            "0", "Seleccione una categoría")]

        # Ordenar categorías por nombre antes de añadirlas al dropdown
        sorted_categories = sorted(self.categories, key=lambda cat: cat.name)

        for category in sorted_categories:
            category_options.append(ft.dropdown.Option(
                str(category.id), category.name))

        self.category_input = ft.Dropdown(
            label="Categoría",
            width=300,
            options=category_options,
            value="0",  # Valor por defecto
            on_change=self.update_subcategories  # Añadir evento para actualizar subcategorías
        )

        # Dropdown para subcategorías
        subcategory_options = [ft.dropdown.Option("0", "Seleccione una subcategoría")]
        
        self.subcategory_input = ft.Dropdown(
            label="Subcategoría",
            width=300,
            options=subcategory_options,
            value="0"  # Valor por defecto
        )

        # Dropdown para proveedores
        supplier_options = [ft.dropdown.Option("0", "Seleccione un proveedor")]
        
        if self.suppliers:
            sorted_suppliers = sorted(self.suppliers, key=lambda sup: sup.name)
            for supplier in sorted_suppliers:
                supplier_options.append(ft.dropdown.Option(
                    str(supplier.id), supplier.name))
                    
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

        # Botón para gestionar proveedores
        self.manage_suppliers_button = ft.OutlinedButton(
            text="Gestionar Proveedores",
            icon=ft.icons.BUSINESS,
            on_click=lambda _: self.page.go("/proveedores")
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

        # Crear un layout responsivo para dispositivos móviles y escritorio
        form_width = min(self.page.width * 0.9, 1200) if self.is_mobile else min(self.page.width * 0.7, 1200)
        field_width = form_width * 0.9 if self.is_mobile else 300

        # Actualizar el ancho de los campos según el tamaño de la pantalla
        for field in [self.name_input, self.price_input, self.stock_input, 
                     self.description_input, self.category_input, self.subcategory_input,
                     self.supplier_input, self.barcode_input, self.code_input]:
            field.width = field_width

        # Sección de información básica
        basic_info_section = ft.Container(
            content=ft.Column([
                ft.Text("Información Básica del Producto",
                        weight=ft.FontWeight.BOLD, size=16),
                self.name_input,
                ft.Row([
                    ft.Column([self.price_input], expand=True),
                    ft.Column([self.stock_input], expand=True)
                ]) if not self.is_mobile else ft.Column([self.price_input, self.stock_input]),
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        )

        # Sección de categorías y detalles
        categories_section = ft.Container(
            content=ft.Column([
                ft.Text("Categorización",
                        weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    ft.Column([
                        self.category_input,
                        self.subcategory_input,
                    ], expand=True),
                    ft.Column([
                        # Espaciador para alinear con el dropdown
                        ft.Container(height=25),
                        self.manage_categories_button,
                    ]) if not self.is_mobile else ft.Container()
                ]),
                self.manage_categories_button if self.is_mobile else ft.Container(),
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        )

        # Sección de detalles adicionales
        additional_info_section = ft.Container(
            content=ft.Column([
                ft.Text("Información Adicional",
                        weight=ft.FontWeight.BOLD, size=16),
                self.description_input,
                ft.Row([
                    ft.Column([
                        self.supplier_input,
                        # Botón de gestión de proveedores
                        ft.Container(
                            content=self.manage_suppliers_button,
                            alignment=ft.alignment.center_right,
                            margin=ft.margin.only(top=5)
                        ) if not self.is_mobile else ft.Container(),
                    ], expand=True),
                    ft.Column([self.barcode_input], expand=True)
                ]) if not self.is_mobile else ft.Column([
                    self.supplier_input,
                    # Botón de gestión de proveedores para móvil
                    ft.Container(
                        content=self.manage_suppliers_button,
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=5, bottom=10)
                    ),
                    self.barcode_input
                ]),
                self.code_input,
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        )

        # Botones de acción
        action_buttons = ft.Row([
            self.cancel_button,
            self.save_button
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)

        # Construir formulario completo
        form_container = ft.Container(
            content=ft.Column([
                ft.Text("Editar Producto" if self.edit_mode else "Nuevo Producto",
                       weight=ft.FontWeight.BOLD, size=20),
                basic_info_section,
                categories_section,
                additional_info_section,
                action_buttons
            ]),
            width=form_width,
            padding=10
        )

        # Envolver en un ScrollView para asegurar que todo el contenido sea accesible
        return ft.Column([
            ft.Container(
                content=form_container,
                alignment=ft.alignment.center
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def update_subcategories(self, e):
        """Actualiza las opciones de subcategorías según la categoría seleccionada."""
        try:
            # Obtener el ID de la categoría seleccionada
            category_id = int(self.category_input.value or 0)
            logging.info(f"Actualizando subcategorías para categoría ID: {category_id}")
            
            # Inicializar las opciones con el valor por defecto
            subcategory_options = [ft.dropdown.Option("0", "Seleccione una subcategoría")]
            
            if category_id >= 0:
                # Obtener las subcategorías activas para esta categoría
                logging.info(f"Consultando subcategorías para categoría ID: {category_id}")
                self.subcategories = self.subcategory_service.get_active_subcategories(category_id=category_id)
                
                # Ordenar subcategorías por nombre
                if self.subcategories:
                    sorted_subcategories = sorted(self.subcategories, key=lambda sub: sub.name)
                    for subcategory in sorted_subcategories:
                        
                        subcategory_options.append(ft.dropdown.Option(
                            str(subcategory.id), subcategory.name))
                else:
                    logging.warning(f"No se encontraron subcategorías para la categoría ID: {category_id}")
                    # Agregar una opción que indique que no hay subcategorías
                    subcategory_options.append(ft.dropdown.Option(
                        "-1", "No hay subcategorías disponibles"))
            else:
                # Indicar que primero se debe seleccionar una categoría
                subcategory_options = [ft.dropdown.Option("0", "Primero seleccione una categoría")]
            
            logging.info(f"Subcategorías: {subcategory_options}")
            # Actualizar las opciones y resetear el valor
            self.subcategory_input.options = subcategory_options
            self.subcategory_input.value = "0"
            
            # Actualizar la UI para mostrar los cambios
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al actualizar subcategorías: {str(e)}")
            show_error_message(self.page, f"Error al cargar subcategorías: {str(e)}")
            # Imprimir el stack trace para facilitar la depuración
            import traceback
            logging.error(traceback.format_exc())
    
    def add_product(self, e):
        try:
            name = self.name_input.value
            price = float(self.price_input.value or 0)
            stock = int(self.stock_input.value or 0)
            description = self.description_input.value
            subcategory_id = int(self.subcategory_input.value or 0)
            category_id = int(self.category_input.value or 0)
            supplier_id = int(self.supplier_input.value or 0)
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
                "subcategory_id": subcategory_id,
                "supplier_id": supplier_id,
                "barcode": barcode,
                "code": code
            }

            if self.edit_mode:
                # Obtener el ID del producto a editar
                product_id = self.page.client_storage.get("edit_product_id")
                if product_id:
                    # Actualizar el producto existente
                    self.product_service.update_product(
                        product_id, product_data)
                    show_success_message(
                        self.page, "Producto actualizado exitosamente.")
                    # Regresar a la vista de inventario
                    self.page.client_storage.remove("edit_product_id")
                    self.page.go("/ver_inventario")
            else:
                # Crear un nuevo producto
                self.product_service.create_product(product_data)
                show_success_message(
                    self.page, "Producto agregado exitosamente.")
                self.clear_inputs()
        except ValueError:
            show_error_message(
                self.page, "Por favor ingrese valores numéricos válidos para precio y stock.")
        except Exception as e:
            show_error_message(
                self.page, f"Error al {'actualizar' if self.edit_mode else 'agregar'} el producto: {str(e)}")
    
    def go_back(self, e):
        """Vuelve a la pantalla anterior."""
        self.page.go("/ver_inventario")
    
    def clear_inputs(self):
        self.name_input.value = ""
        self.price_input.value = ""
        self.stock_input.value = ""
        self.description_input.value = ""
        self.category_input.value = "0"
        self.subcategory_input.value = "0"
        self.barcode_input.value = ""
        self.supplier_input.value = "0"
        self.code_input.value = ""
        self.adjustment_input.value = "0"
        self.reason_input.value = ""
        self.page.update()
    
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
                        # Actualizar subcategorías después de establecer la categoría
                        self.update_subcategories(None)
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
                        # Actualizar subcategorías después de establecer la categoría
                        self.update_subcategories(None)
                    
                    if product.subcategory_id:
                        self.subcategory_input.value = str(product.subcategory_id)
                    else:
                        # Si no es un ID, buscar la subcategoría por nombre o usar el valor por defecto
                        found = False
                        for subcategory in self.subcategories:
                            if subcategory.name == product.subcategory:
                                self.subcategory_input.value = str(subcategory.id)
                                found = True
                                break
                        if not found:
                            self.subcategory_input.value = "0"  # Valor por defecto si no se encuentra

                    if product.supplier_id:
                        self.supplier_input.value = str(product.supplier_id)

                    self.barcode_input.value = product.barcode or ""
                    self.code_input.value = product.code or ""

                    self.page.update()
        except Exception as e:
            show_error_message(
                self.page, f"Error al cargar los datos del producto: {str(e)}")