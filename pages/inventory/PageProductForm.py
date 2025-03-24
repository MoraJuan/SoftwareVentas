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
    def __init__(self, page: ft.Page, session, edit_mode=False, product_id=None):
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
            
        # Si se proporciona un product_id, estamos en modo edición
        if product_id:
            self.edit_mode = True
            # Guardar el ID del producto en el almacenamiento del cliente
            self.page.client_storage.set("edit_product_id", product_id)
            logging.info(f"Formulario de producto en modo edición para ID: {product_id}")
        else:
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
            # Crear el título según el modo
            title_text = "Editar Producto" if self.edit_mode else "Agregar Producto"
            form_description = "Modificar información del producto existente" if self.edit_mode else "Agregar un nuevo producto al inventario"
            
            # Título y descripción
            title_section = ft.Column([
                ft.Text(
                    title_text,
                    size=20 if self.is_mobile else 24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                ft.Text(
                    form_description,
                    size=14 if self.is_mobile else 16,
                    color=ft.colors.ON_SURFACE_VARIANT
                ),
                ft.Container(height=10),
            ])
            
            # Crear el contenido del formulario
            form_content = self.create_form_layout()
            
            # Botón para guardar o volver
            action_buttons = ft.Container(
                content=ft.Row([
                    ft.OutlinedButton(
                        "Volver a Inventario",
                        icon=ft.icons.ARROW_BACK,
                        on_click=self.go_back
                    ),
                    ft.FilledButton(
                        "Guardar Producto",
                        icon=ft.icons.SAVE,
                        on_click=self.add_product
                    )
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.only(top=20, bottom=20),
                margin=ft.margin.only(top=10),
                width=min(self.page.width * 0.9, 1200) if self.is_mobile else min(self.page.width * 0.7, 1200)
            )

            # UI principal 
            content_column = ft.Column(
                [
                    title_section,
                    form_content,
                    action_buttons
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=10
            )
            
            # Envolvemos el Column en un Container para aplicar el padding
            self.controls = [
                ft.Container(
                    content=content_column,
                    padding=10 if self.is_mobile else 20
                )
            ]
            
            # Si estamos en modo edición, cargar los datos del producto
            if self.edit_mode:
                # Cargar datos inmediatamente
                self.load_product_data()
                
        except Exception as e:
            logging.error(f"Error construyendo UI del formulario de producto: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            self.controls = [ft.Text(f"Error al cargar el formulario: {str(e)}", color=ft.colors.ERROR)]
    
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
            min_lines=2,  # Reducimos las líneas mínimas
            max_lines=3   # Reducimos las líneas máximas
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

        # Ajustes de inventario - solo los incluimos si es necesario (los comentamos por ahora)
        # self.adjustment_input = ft.TextField(
        #     label="Cantidad a ajustar",
        #     width=field_width,
        #     keyboard_type=ft.KeyboardType.NUMBER,
        #     value="0"
        # )
        # self.reason_input = ft.TextField(
        #     label="Motivo del ajuste",
        #     width=field_width,
        #     hint_text="Razón del ajuste de inventario"
        # )

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
            ], spacing=15),  # Reducimos el espaciado
            padding=15,      # Reducimos el padding
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=15),  # Reducimos el margen
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
            ], spacing=15),  # Reducimos el espaciado
            padding=15,      # Reducimos el padding
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=15),  # Reducimos el margen
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
            ], spacing=15),  # Reducimos el espaciado
            padding=15,      # Reducimos el padding
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=15),  # Reducimos el margen
            width=form_width
        )

        # Construir formulario completo
        self.form_container = ft.Container(
            content=ft.Column([
                basic_info_section,
                categories_section,
                additional_info_section
            ], spacing=5),  # Reducimos el espaciado entre secciones
            width=form_width,
            padding=5,      # Reducimos el padding
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
    
    def add_product(self, e=None):
        """Agrega un nuevo producto o actualiza uno existente"""
        try:
            # Obtener datos del formulario
            name = self.name_input.value
            
            # Verificar que el nombre no esté vacío
            if not name:
                show_error_message(
                    self.page, "El nombre del producto es obligatorio.")
                return
            
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
                subcategory_id = int(self.subcategory_input.value or 0) if self.subcategory_input.value != "0" else 0
            except (ValueError, TypeError):
                subcategory_id = 0
                
            try:
                category_id = int(self.category_input.value or 0) if self.category_input.value != "0" else 0
            except (ValueError, TypeError):
                category_id = 0
                
            try:
                supplier_id = int(self.supplier_input.value or 0) if self.supplier_input.value != "0" else 0
            except (ValueError, TypeError):
                supplier_id = 0
                
            barcode = self.barcode_input.value or ""
            code = self.code_input.value or ""

            # Crear diccionario con los datos del producto
            product_data = {
                "name": name,
                "price": price,
                "stock": stock,
                "description": description,
                "category_id": category_id if category_id > 0 else None,
                "subcategory_id": subcategory_id if subcategory_id > 0 else None,
                "supplier_id": supplier_id if supplier_id > 0 else None,
                "barcode": barcode,
                "code": code
            }

            if self.edit_mode:
                logging.info(f"Actualizando producto en modo edición")
                # Obtener el ID del producto a editar
                product_id = self.page.client_storage.get("edit_product_id")
                if product_id:
                    logging.info(f"Actualizando producto ID {product_id}")
                    # Actualizar el producto existente
                    updated_product = self.product_service.update_product(
                        product_id, product_data)
                    
                    if updated_product:
                        logging.info(f"Producto actualizado exitosamente: {updated_product.name}")
                        show_success_message(
                            self.page, "Producto actualizado exitosamente.")
                        # Regresar a la vista de inventario
                        self.page.client_storage.remove("edit_product_id")
                        self.go_back(None)
                    else:
                        logging.error(f"Fallo al actualizar el producto ID {product_id}")
                        show_error_message(
                            self.page, "No se pudo actualizar el producto.")
                else:
                    logging.error("Error: No se encontró el ID del producto a editar")
                    show_error_message(
                        self.page, "Error: No se pudo identificar el producto a editar.")
            else:
                # Crear un nuevo producto
                logging.info(f"Creando nuevo producto: {name}")
                new_product = self.product_service.create_product(product_data)
                
                if new_product:
                    logging.info(f"Producto creado exitosamente: {new_product.name} (ID: {new_product.id})")
                    show_success_message(
                        self.page, "Producto agregado exitosamente.")
                    # Volver a la vista de inventario después de agregar
                    self.go_back(None)
                else:
                    logging.error(f"Fallo al crear el nuevo producto: {name}")
                    show_error_message(
                        self.page, "No se pudo crear el producto.")
                
        except ValueError as ve:
            logging.error(f"Error de valor en add_product: {str(ve)}")
            show_error_message(
                self.page, "Por favor ingrese valores numéricos válidos para precio y stock.")
        except Exception as e:
            logging.error(f"Error en add_product: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(
                self.page, f"Error al {'actualizar' if self.edit_mode else 'agregar'} el producto: {str(e)}")
    
    def go_back(self, e):
        """Vuelve a la pantalla de inventario."""
        try:
            logging.info("Volviendo a la vista de inventario")
            from pages.inventory.PageInventory import PageInventory
            # Crear una instancia de la página de inventario
            inventory_page = PageInventory(self.page, self.session)
            # Limpiar controles actuales
            self.controls.clear()
            # Añadir la página de inventario a los controles
            self.controls.append(inventory_page)
            # Actualizar la UI
            self.update()
            logging.info("Vista de inventario cargada exitosamente")
        except Exception as e:
            logging.error(f"Error al volver a inventario: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al volver a inventario: {str(e)}")
    
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
        # Comentamos la limpieza de los campos de ajuste que ya no estamos usando
        # if hasattr(self, 'adjustment_input') and self.adjustment_input:
        #     self.adjustment_input.value = "0"
        # if hasattr(self, 'reason_input') and self.reason_input:
        #     self.reason_input.value = ""
        self.page.update()
    
    def load_product_data(self):
        try:
            # Obtener el ID del producto a editar del almacenamiento del cliente o del parámetro
            product_id = self.page.client_storage.get("edit_product_id")
            
            if not product_id:
                logging.error("No se encontró el ID del producto a editar en el client_storage")
                show_error_message(self.page, "No se pudo determinar qué producto editar")
                return
                
            logging.info(f"Cargando datos para el producto ID: {product_id}")
            
            # Obtener los datos del producto
            product = self.product_service.get_product_by_id(product_id)
            
            if not product:
                logging.error(f"No se pudo obtener los datos del producto ID {product_id}")
                show_error_message(self.page, "No se pudo cargar los datos del producto")
                self.go_back(None)  # Regresar a la vista de inventario
                return
                
            logging.info(f"Datos del producto obtenidos correctamente: {product.name}")
            self.selected_product = product
            
            # Verificar que los campos estén inicializados antes de asignar valores
            try:
                if hasattr(self, 'name_input') and self.name_input:
                    self.name_input.value = product.name or ""
                    logging.info(f"Nombre del producto establecido: {product.name}")
                
                if hasattr(self, 'price_input') and self.price_input:
                    self.price_input.value = str(product.price or 0)
                    logging.info(f"Precio del producto establecido: {product.price}")
                
                if hasattr(self, 'stock_input') and self.stock_input:
                    self.stock_input.value = str(product.stock or 0)
                    logging.info(f"Stock del producto establecido: {product.stock}")
                
                if hasattr(self, 'description_input') and self.description_input:
                    self.description_input.value = product.description or ""
                
                # Manejar la categoría y subcategoría
                self._load_category_and_subcategory(product)
                
                # Cargar proveedor
                if hasattr(self, 'supplier_input') and self.supplier_input:
                    if hasattr(product, 'supplier_id') and product.supplier_id:
                        self.supplier_input.value = str(product.supplier_id)
                        logging.info(f"Proveedor del producto establecido: {product.supplier_id}")
                
                # Cargar otros campos
                if hasattr(self, 'barcode_input') and self.barcode_input:
                    self.barcode_input.value = product.barcode or ""
                
                if hasattr(self, 'code_input') and self.code_input:
                    self.code_input.value = product.code or ""
                
                # Actualizar la UI después de cargar todos los datos
                self.page.update()
                logging.info("Datos del producto cargados correctamente en el formulario")
            except Exception as e:
                logging.error(f"Error al establecer los valores del formulario: {str(e)}")
                import traceback
                logging.error(traceback.format_exc())
                show_error_message(self.page, f"Error al configurar el formulario: {str(e)}")
            
        except Exception as e:
            logging.error(f"Error al cargar datos del producto: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al cargar los datos del producto: {str(e)}")

    def _load_category_and_subcategory(self, product):
        """Método auxiliar para cargar categoría y subcategoría"""
        try:
            # Manejar la categoría
            if hasattr(self, 'category_input') and self.category_input:
                if hasattr(product, 'category_id') and product.category_id:
                    self.category_input.value = str(product.category_id)
                    logging.info(f"Categoría del producto establecida: {product.category_id}")
                    # Actualizar subcategorías después de establecer la categoría
                    self._on_category_change(None)
                elif hasattr(product, 'category') and product.category:
                    # Buscar la categoría por nombre
                    found = False
                    for category in self.categories:
                        if category.name == product.category:
                            self.category_input.value = str(category.id)
                            found = True
                            logging.info(f"Categoría encontrada por nombre: {category.name}")
                            break
                    
                    if not found:
                        logging.warning(f"No se encontró la categoría por nombre: {product.category}")
                        self.category_input.value = "0"
                    
                    # Actualizar subcategorías después de establecer la categoría
                    self._on_category_change(None)
            
            # Manejar la subcategoría - esperar un momento para que se carguen las subcategorías
            if hasattr(self, 'subcategory_input') and self.subcategory_input:
                if hasattr(product, 'subcategory_id') and product.subcategory_id:
                    # Esperar a que estén disponibles las subcategorías
                    # Intentamos establecer el valor directamente
                    self.subcategory_input.value = str(product.subcategory_id)
                    logging.info(f"Subcategoría del producto establecida: {product.subcategory_id}")
                elif hasattr(product, 'subcategory') and product.subcategory:
                    # Intento de búsqueda por nombre
                    found = False
                    for subcategory in self.subcategories:
                        if subcategory.name == product.subcategory:
                            self.subcategory_input.value = str(subcategory.id)
                            found = True
                            logging.info(f"Subcategoría encontrada por nombre: {subcategory.name}")
                            break
                    
                    if not found:
                        logging.warning(f"No se encontró la subcategoría por nombre: {product.subcategory}")
                        self.subcategory_input.value = "0"
        
        except Exception as e:
            logging.error(f"Error al cargar categoría y subcategoría: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())

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