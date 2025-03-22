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
        
        # Verificar que la página sea válida antes de acceder a su ancho
        if self.page is None:
            logging.error("Error: page es None en __init__ de PageProductForm")
            self.is_mobile = True  # Valor por defecto
            self.is_tablet = False
        else:
            self.is_mobile = self.page.width < 600
            self.is_tablet = 600 <= self.page.width < 1024
            
        self.edit_mode = edit_mode
        self.all_products = []
        self.table = None
        self.table_container = None
        self.search_field = None
        
        # Inicializar campos que serán usados por handle_resize
        self.form_container = None
        self.name_input = None
        self.price_input = None
        self.stock_input = None
        self.description_input = None
        self.category_input = None
        self.subcategory_input = None
        self.supplier_input = None
        self.barcode_input = None
        self.code_input = None
        self.manage_categories_button = None
        self.manage_suppliers_button = None
        
        # Inicializar servicios
        try:
            self.product_service = ProductService(session)
            self.category_service = CategoryService(session)
            self.subcategory_service = SubcategoryService(session)
            self.supplier_service = SupplierService(session)
            
            # Cargar datos
            self.categories = self.category_service.get_active_categories() or []
            self.subcategories = []
            self.suppliers = self.supplier_service.get_all_suppliers() or []
            
            # Verificar que el servicio de subcategorías funcione correctamente
            logging.info("Verificando servicio de subcategorías...")
            if self.categories and len(self.categories) > 0:
                test_category_id = self.categories[0].id
                test_subcategories = self.subcategory_service.get_active_subcategories(category_id=test_category_id)
                logging.info(f"Subcategorías de prueba para categoría {test_category_id}: {test_subcategories}")
        except Exception as e:
            logging.error(f"Error al inicializar servicios: {str(e)}")
            self.categories = []
            self.subcategories = []
            self.suppliers = []
        
        # Configurar eventos solo si la página es válida
        if self.page is not None:
            self.page.on_resize = self.handle_resize
        
        # Construir UI
        self.build_ui()
        
        # Cargar datos si estamos en modo de edición
        if self.edit_mode:
            self.load_product_data()

    def handle_resize(self, e):
        try:
            # Verificar que self.page no sea None antes de acceder a width
            if not hasattr(self, 'page') or self.page is None:
                logging.error("Error: self.page es None en handle_resize de PageProductForm")
                return
                
            # Detectar cambios en el tamaño del dispositivo
            new_is_mobile = self.page.width < 600
            new_is_tablet = 600 <= self.page.width < 1024
            
            logging.info(f"Resize detectado - Ancho: {self.page.width}, Mobile: {new_is_mobile}, Tablet: {new_is_tablet}")
            
            # Si cambia la categoría del dispositivo, reconstruir la UI completa
            if new_is_mobile != self.is_mobile or new_is_tablet != self.is_tablet:
                logging.info(f"Cambiando modo de dispositivo a: {'mobile' if new_is_mobile else 'tablet' if new_is_tablet else 'desktop'}")
                self.is_mobile = new_is_mobile
                self.is_tablet = new_is_tablet
                
                # Reconstruir completamente la UI
                self.controls.clear()
                self.build_ui()
                self.update()
                return
                
            # Si solo cambia el tamaño pero no la categoría, ajustar componentes específicos
            if hasattr(self, 'form_container') and self.form_container is not None:
                try:
                    # Recalcular anchos basados en el nuevo tamaño
                    form_width = min(self.page.width * 0.9, 1200) if self.is_mobile else min(self.page.width * 0.7, 1200)
                    field_width = form_width * 0.85 if self.is_mobile else 300
                    
                    logging.info(f"Ajustando anchos - Form: {form_width}, Field: {field_width}")
                    
                    # Actualizar el ancho del contenedor del formulario si existe
                    if self.form_container is not None:
                        self.form_container.width = form_width
                    
                    # Actualizar anchos de los campos si están disponibles
                    for field_name in ['name_input', 'price_input', 'stock_input', 'description_input', 
                                      'category_input', 'subcategory_input', 'supplier_input', 
                                      'barcode_input', 'code_input']:
                        if hasattr(self, field_name) and getattr(self, field_name) is not None:
                            field = getattr(self, field_name)
                            if hasattr(field, 'width'):
                                if field_name in ['price_input', 'stock_input'] and not self.is_mobile:
                                    field.width = 140
                                else:
                                    field.width = field_width
                    
                    # Actualizar texto de botones según el dispositivo
                    if hasattr(self, 'manage_categories_button') and self.manage_categories_button is not None:
                        self.manage_categories_button.text = "" if self.is_mobile else "Gestionar Categorías"
                        self.manage_categories_button.tooltip = "Gestionar Categorías" if self.is_mobile else None
                    
                    if hasattr(self, 'manage_suppliers_button') and self.manage_suppliers_button is not None:
                        self.manage_suppliers_button.text = "" if self.is_mobile else "Gestionar Proveedores"
                        self.manage_suppliers_button.tooltip = "Gestionar Proveedores" if self.is_mobile else None
                    
                    # Forzar actualización completa
                    self.update()
                except Exception as e:
                    logging.error(f"Error al ajustar campos durante resize: {str(e)}")
                    import traceback
                    logging.error(traceback.format_exc())
        except Exception as e:
            logging.error(f"Error en handle_resize: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())

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
            ], scroll=None, expand=True)  # Quitar scroll del content_column

            # Contenedor principal con scroll
            main_container = ft.Container(
                content=content_column,
                expand=True,
                padding=10 if self.is_mobile else 20
            )

            # Columna con scroll que envuelve todo
            self.controls = [
                ft.Column(
                    [main_container],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START  # Alinear al inicio para evitar espacios en blanco
                )
            ]
        except Exception as e:
            logging.error(f"Error en build_ui: {str(e)}")
            self.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=64),
                        ft.Text(
                            "Error al cargar el formulario",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        ft.Text(
                            str(e),
                            color=ft.colors.ON_SURFACE
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
    
    def create_form_layout(self):
        try:
            # Información básica del producto
            # Calcular anchos responsivos
            form_width = min(self.page.width * 0.9, 1200) if self.is_mobile else min(self.page.width * 0.7, 1200)
            field_width = form_width * 0.85 if self.is_mobile else 300
            
            logging.info(f"Creando formulario - Ancho: {self.page.width}, Form width: {form_width}, Field width: {field_width}")
            
            # Envolver en un Column sin scroll ya que el scroll está en el contenedor principal
            return ft.Column([
                self._create_form_content(form_width, field_width)
            ], expand=True, alignment=ft.MainAxisAlignment.START)
        except Exception as e:
            logging.error(f"Error creando formulario: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=48),
                        ft.Text("Error al crear el formulario", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
                        ft.Text(str(e), color=ft.colors.ERROR)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    padding=20,
                    alignment=ft.alignment.center
                )
            ], expand=True)
            
    def _create_form_content(self, form_width, field_width):
        """Método auxiliar para crear el contenido del formulario"""
        # Crear campos del formulario (código actual en create_form_layout)
        self.name_input = ft.TextField(
            label="Nombre del Producto",
            width=field_width,
        )
        self.price_input = ft.TextField(
            label="Precio",
            width=field_width if self.is_mobile else 140,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0",  # Valor por defecto para evitar errores
        )
        self.stock_input = ft.TextField(
            label="Stock",
            width=field_width if self.is_mobile else 140,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0",  # Valor por defecto para evitar errores
        )

        # Información adicional del producto
        self.description_input = ft.TextField(
            label="Descripción",
            width=field_width,
            multiline=True,
            min_lines=3,
            max_lines=5
        )

        # Dropdown para categorías
        category_options = [ft.dropdown.Option(
            "0", "Seleccione una categoría")]

        # Ordenar categorías por nombre antes de añadirlas al dropdown
        sorted_categories = sorted(self.categories, key=lambda cat: cat.name) if self.categories else []

        for category in sorted_categories:
            category_options.append(ft.dropdown.Option(
                str(category.id), category.name))

        # Implementar el manejo de eventos de dos formas para garantizar que funcione
        self.category_input = ft.Dropdown(
            label="Categoría",
            width=field_width,
            options=category_options,
            value="0",  # Valor por defecto
            on_change=self._on_category_change  # Usar directamente la función de callback
        )
        
        # Dropdown para subcategorías
        subcategory_options = [ft.dropdown.Option("0", "Seleccione una subcategoría")]
        
        self.subcategory_input = ft.Dropdown(
            label="Subcategoría",
            width=field_width,
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
            width=field_width,
            options=supplier_options,
            value="0"  # Valor por defecto
        )

        # Botón para gestionar categorías - adaptado para móvil
        button_text = "" if self.is_mobile else "Gestionar Categorías"
        self.manage_categories_button = ft.OutlinedButton(
            text=button_text,
            icon=ft.icons.CATEGORY,
            tooltip="Gestionar Categorías" if self.is_mobile else None,
            on_click=lambda _: self.show_categories()
        )

        # Botón para gestionar proveedores - adaptado para móvil
        button_text_supplier = "" if self.is_mobile else "Gestionar Proveedores"
        self.manage_suppliers_button = ft.OutlinedButton(
            text=button_text_supplier,
            icon=ft.icons.BUSINESS,
            tooltip="Gestionar Proveedores" if self.is_mobile else None,
            on_click=lambda _: self.show_suppliers()
        )

        # Otros campos
        self.barcode_input = ft.TextField(
            label="Código de Barras",
            width=field_width,
        )
        self.code_input = ft.TextField(
            label="Código Interno",
            width=field_width,
        )

        # Ajustes de inventario
        self.adjustment_input = ft.TextField(
            label="Cantidad a ajustar",
            width=field_width,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0"
        )
        self.reason_input = ft.TextField(
            label="Motivo del ajuste",
            width=field_width,
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

        # Sección de información básica
        basic_info_section = ft.Container(
            content=ft.Column([
                ft.Text("Información Básica del Producto",
                        weight=ft.FontWeight.BOLD, size=16),
                self.name_input,
                ft.Row([
                    ft.Column([self.price_input], expand=self.is_tablet),
                    ft.Column([self.stock_input], expand=self.is_tablet)
                ]) if not self.is_mobile else ft.Column([self.price_input, self.stock_input]),
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
            width=form_width
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
                    ], alignment=ft.MainAxisAlignment.START) if not self.is_mobile else ft.Container()
                ]),
                self.manage_categories_button if self.is_mobile else ft.Container(),
            ], spacing=20),
            padding=20,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
            width=form_width
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
            margin=ft.margin.only(bottom=20),
            width=form_width
        )

        # Botones de acción
        action_buttons = ft.Row([
            self.cancel_button,
            self.save_button
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)

        # Construir formulario completo
        self.form_container = ft.Container(
            content=ft.Column([
                basic_info_section,
                categories_section,
                additional_info_section,
                action_buttons
            ]),
            width=form_width,
            padding=10,
            alignment=ft.alignment.center
        )
        
        return self.form_container
    
    def _on_category_change(self, e):
        """
        Método intermediario para depurar el evento on_change del dropdown de categoría
        """
        logging.info("Evento on_change de categoría detectado")
        logging.info(f"Valor seleccionado: {self.category_input.value}")
        
        try:
            # Obtener el ID de categoría directamente sin depender del evento
            category_id = int(self.category_input.value or 0)
            logging.info(f"Forzando actualización para categoría ID: {category_id}")
            
            # Forzar la carga de subcategorías
            if category_id > 0:
                # Cargar subcategorías manualmente
                subcategories = self.subcategory_service.get_active_subcategories(category_id=category_id)
                logging.info(f"Subcategorías obtenidas manualmente: {subcategories}")
                
                # Actualizar las opciones del dropdown
                if subcategories:
                    # Crear un nuevo objeto de opciones
                    subcategory_options = [ft.dropdown.Option("0", "Seleccione una subcategoría")]
                    sorted_subcategories = sorted(subcategories, key=lambda sub: sub.name)
                    
                    for subcategory in sorted_subcategories:
                        subcategory_options.append(ft.dropdown.Option(
                            str(subcategory.id), subcategory.name))
                        logging.info(f"Añadida subcategoría: {subcategory.name} (ID: {subcategory.id})")
                    
                    # Actualizar el dropdown de subcategorías - reemplazando completamente las opciones
                    self.subcategory_input.options.clear()
                    for option in subcategory_options:
                        self.subcategory_input.options.append(option)
                    
                    # Restablecer el valor
                    self.subcategory_input.value = "0"
                    
                    # Almacenar las subcategorías
                    self.subcategories = subcategories
                else:
                    # No hay subcategorías para esta categoría
                    self.subcategory_input.options = [
                        ft.dropdown.Option("0", "Seleccione una subcategoría"),
                        ft.dropdown.Option("-1", "No hay subcategorías disponibles")
                    ]
                    self.subcategory_input.value = "0"
                    self.subcategories = []
            else:
                # Categoría inválida o no seleccionada
                self.subcategory_input.options = [ft.dropdown.Option("0", "Primero seleccione una categoría")]
                self.subcategory_input.value = "0"
                self.subcategories = []
            
            logging.info(f"Subcategorías actualizadas: {self.subcategories}")
            
            # Forzar la actualización de la UI - ESTO ES CRÍTICO
            if self.page:
                logging.info("Forzando actualización de UI después de cambio de categoría")
                
                # Forzar una actualización explícita del dropdown de subcategorías
                self.subcategory_input.update()
                
                # Actualizar toda la página
                self.page.update()
                
                # Verificar una segunda vez después de una breve pausa
                self.page.run_task(self._verify_subcategories_update)
                
            else:
                logging.error("No se puede actualizar la UI, self.page es None")
                
        except Exception as e:
            logging.error(f"Error en _on_category_change: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            if self.page:
                show_error_message(self.page, f"Error al actualizar subcategorías: {str(e)}")
        
    async def _verify_subcategories_update(self):
        """Verifica que las subcategorías se hayan actualizado correctamente después de una breve pausa"""
        import asyncio
        try:
            # Esperar un momento para que la UI se actualice
            await asyncio.sleep(0.1)
            
            # Verificar si hay subcategorías y el dropdown está actualizado
            logging.info("Verificando actualización de subcategorías...")
            if self.subcategories and len(self.subcategories) > 0:
                # Comprobar si el dropdown tiene las opciones correctas
                dropdown_options_count = len(self.subcategory_input.options)
                expected_count = len(self.subcategories) + 1  # +1 por la opción predeterminada
                
                logging.info(f"Opciones en dropdown: {dropdown_options_count}, Esperadas: {expected_count}")
                
                if dropdown_options_count != expected_count:
                    logging.warning("¡Las opciones del dropdown no coinciden con las subcategorías! Forzando actualización...")
                    
                    # Recrear las opciones
                    subcategory_options = [ft.dropdown.Option("0", "Seleccione una subcategoría")]
                    for subcategory in self.subcategories:
                        subcategory_options.append(ft.dropdown.Option(
                            str(subcategory.id), subcategory.name))
                    
                    # Actualizar manualmente
                    self.subcategory_input.options = subcategory_options
                    self.subcategory_input.value = "0"
                    
                    # Forzar actualización
                    self.subcategory_input.update()
                    self.page.update()
        except Exception as e:
            logging.error(f"Error en _verify_subcategories_update: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
    
    def add_product(self, e):
        try:
            # Verificar que todos los campos estén inicializados
            required_fields = ['name_input', 'price_input', 'stock_input', 'description_input', 
                              'category_input', 'subcategory_input', 'supplier_input',
                              'barcode_input', 'code_input']
            
            for field in required_fields:
                if not hasattr(self, field) or getattr(self, field) is None:
                    show_error_message(self.page, f"Error: El campo {field} no está inicializado")
                    return
            
            name = self.name_input.value or ""
            
            # Manejar valores numéricos con seguridad
            try:
                price = float(self.price_input.value or 0)
            except (ValueError, TypeError):
                price = 0
                
            try:
                stock = int(self.stock_input.value or 0)
            except (ValueError, TypeError):
                stock = 0
                
            description = self.description_input.value or ""
            
            try:
                subcategory_id = int(self.subcategory_input.value or 0)
            except (ValueError, TypeError):
                subcategory_id = 0
                
            try:
                category_id = int(self.category_input.value or 0)
            except (ValueError, TypeError):
                category_id = 0
                
            try:
                supplier_id = int(self.supplier_input.value or 0)
            except (ValueError, TypeError):
                supplier_id = 0
                
            barcode = self.barcode_input.value or ""
            code = self.code_input.value or ""

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
            logging.error(f"Error en add_product: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(
                self.page, f"Error al {'actualizar' if self.edit_mode else 'agregar'} el producto: {str(e)}")
    
    def go_back(self, e):
        """Vuelve a la pantalla anterior."""
        self.page.go("/ver_inventario")
    
    def clear_inputs(self):
        # Verificar que los campos estén inicializados antes de limpiarlos
        if hasattr(self, 'name_input') and self.name_input:
            self.name_input.value = ""
        if hasattr(self, 'price_input') and self.price_input:
            self.price_input.value = ""
        if hasattr(self, 'stock_input') and self.stock_input:
            self.stock_input.value = ""
        if hasattr(self, 'description_input') and self.description_input:
            self.description_input.value = ""
        if hasattr(self, 'category_input') and self.category_input:
            self.category_input.value = "0"
        if hasattr(self, 'subcategory_input') and self.subcategory_input:
            self.subcategory_input.value = "0"
        if hasattr(self, 'barcode_input') and self.barcode_input:
            self.barcode_input.value = ""
        if hasattr(self, 'supplier_input') and self.supplier_input:
            self.supplier_input.value = "0"
        if hasattr(self, 'code_input') and self.code_input:
            self.code_input.value = ""
        if hasattr(self, 'adjustment_input') and self.adjustment_input:
            self.adjustment_input.value = "0"
        if hasattr(self, 'reason_input') and self.reason_input:
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
                    
                    # Verificar que los campos estén inicializados antes de asignar valores
                    if hasattr(self, 'name_input') and self.name_input:
                        self.name_input.value = product.name or ""
                    if hasattr(self, 'price_input') and self.price_input:
                        self.price_input.value = str(product.price or 0)
                    if hasattr(self, 'stock_input') and self.stock_input:
                        self.stock_input.value = str(product.stock or 0)
                    if hasattr(self, 'description_input') and self.description_input:
                        self.description_input.value = product.description or ""

                    # Manejar la categoría - podría ser un ID o un nombre
                    if hasattr(self, 'category_input') and self.category_input:
                        if product.category_id:
                            self.category_input.value = str(product.category_id)
                            # Actualizar subcategorías después de establecer la categoría
                            self._on_category_change(None)
                        else:
                            # Si no es un ID, buscar la categoría por nombre o usar el valor por defecto
                            found = False
                            for category in self.categories:
                                if hasattr(product, 'category') and category.name == product.category:
                                    self.category_input.value = str(category.id)
                                    found = True
                                    break
                            if not found:
                                self.category_input.value = "0"  # Valor por defecto si no se encuentra
                            # Actualizar subcategorías después de establecer la categoría
                            self._on_category_change(None)
                    
                    if hasattr(self, 'subcategory_input') and self.subcategory_input:
                        if product.subcategory_id:
                            self.subcategory_input.value = str(product.subcategory_id)
                        else:
                            # Si no es un ID, buscar la subcategoría por nombre o usar el valor por defecto
                            found = False
                            for subcategory in self.subcategories:
                                if hasattr(product, 'subcategory') and subcategory.name == product.subcategory:
                                    self.subcategory_input.value = str(subcategory.id)
                                    found = True
                                    break
                            if not found:
                                self.subcategory_input.value = "0"  # Valor por defecto si no se encuentra

                    if hasattr(self, 'supplier_input') and self.supplier_input:
                        if product.supplier_id:
                            self.supplier_input.value = str(product.supplier_id)

                    if hasattr(self, 'barcode_input') and self.barcode_input:
                        self.barcode_input.value = product.barcode or ""
                    if hasattr(self, 'code_input') and self.code_input:
                        self.code_input.value = product.code or ""

                    self.page.update()
        except Exception as e:
            logging.error(f"Error al cargar datos del producto: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(
                self.page, f"Error al cargar los datos del producto: {str(e)}")

    # Métodos para navegar a categorías y proveedores
    def show_categories(self, e=None):
        """Muestra la página de categorías"""
        try:
            logging.info("Navegando a la página de categorías")
            # Crear una instancia de la página de categorías
            from pages.categories.PageCategory import PageCategory
            categories_page = PageCategory(self.page, self.session)
            
            # Limpiar los controles actuales y mostrar la página de categorías
            self.controls.clear()
            self.controls.append(categories_page)
            self.update()
        except Exception as e:
            logging.error(f"Error al mostrar la página de categorías: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al mostrar la página de categorías: {str(e)}")
    
    def show_suppliers(self, e=None):
        """Muestra la página de proveedores"""
        try:
            logging.info("Navegando a la página de proveedores")
            # Usar la factory para crear la página de proveedores
            from pages.supplier.page_factory import SupplierPageFactory
            
            # Crear una función de retorno para volver a esta página
            def go_back_to_product_form():
                self.controls.clear()
                self.build_ui()
                self.update()
            
            # Crear la página de proveedores con la función de retorno
            suppliers_page = SupplierPageFactory.create_supplier_page(
                self.page, 
                self.session,
                go_back_callback=go_back_to_product_form
            )
            
            # Limpiar los controles actuales y mostrar la página de proveedores
            self.controls.clear()
            self.controls.append(suppliers_page)
            self.update()
        except Exception as e:
            logging.error(f"Error al mostrar la página de proveedores: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al mostrar la página de proveedores: {str(e)}")

    # Implementar update_subcategories como wrapper para compatibilidad con código existente
    def update_subcategories(self, e):
        """
        Método wrapper para mantener compatibilidad con posibles llamadas existentes.
        Simplemente redirige a _on_category_change.
        """
        logging.info("Método update_subcategories llamado, redirigiendo a _on_category_change")
        self._on_category_change(e)