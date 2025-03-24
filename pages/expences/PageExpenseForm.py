import flet as ft
from services.expenseService import ExpenseService
from services.supplierService import SupplierService
from ui.components.alerts import show_error_message, show_success_message
from datetime import datetime
import logging

class PageExpenseForm(ft.UserControl):
    def __init__(self, page: ft.Page, session, edit_mode=False, expense_id=None):
        super().__init__()
        self.page = page
        self.session = session
        
        # Verificar que la página sea válida antes de acceder a su ancho
        if self.page is None:
            logging.error("Error: page es None en __init__ de PageExpenseForm")
            self.is_mobile = True  # Valor por defecto
            self.is_tablet = False
        else:
            self.is_mobile = self.page.width < 600
            self.is_tablet = 600 <= self.page.width < 1024
        
        # Si se proporciona un expense_id, estamos en modo edición
        if expense_id:
            self.edit_mode = True
            # Guardar el ID del gasto en el almacenamiento del cliente
            self.page.client_storage.set("edit_expense_id", expense_id)
            logging.info(f"Formulario de gasto en modo edición para ID: {expense_id}")
        else:
            self.edit_mode = edit_mode
        
        # Inicializar servicios
        self.expense_service = ExpenseService(session)
        self.supplier_service = SupplierService(session)
        
        # Obtener proveedores
        try:
            self.suppliers = self.supplier_service.get_all_suppliers()
            logging.info(f"Proveedores cargados: {len(self.suppliers)}")
        except Exception as e:
            logging.error(f"Error al cargar proveedores: {str(e)}")
            self.suppliers = []
        
        # Inicializar campos que serán usados
        self.form_container = None
        self.description_input = None
        self.amount_input = None
        self.category_input = None
        self.supplier_input = None
        self.date_input = None
        
        # Construir la interfaz de usuario
        self.build_ui()
    
    def build_ui(self):
        try:
            # Crear el título según el modo
            title_text = "Editar Gasto" if self.edit_mode else "Agregar Gasto"
            form_description = "Modificar información del gasto existente" if self.edit_mode else "Agregar un nuevo gasto al sistema"
            
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
                        "Volver a Gastos",
                        icon=ft.icons.ARROW_BACK,
                        on_click=self.go_back
                    ),
                    ft.FilledButton(
                        "Guardar Gasto",
                        icon=ft.icons.SAVE,
                        on_click=self.save_expense
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
            
            # Si estamos en modo edición, cargar los datos del gasto
            if self.edit_mode:
                # Cargar datos inmediatamente
                self.load_expense_data()
                
        except Exception as e:
            logging.error(f"Error construyendo UI del formulario de gasto: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            self.controls = [ft.Text(f"Error al cargar el formulario: {str(e)}", color=ft.colors.ERROR)]
    
    def create_form_layout(self):
        try:
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
        # Crear campos del formulario
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        self.date_input = ft.TextField(
            label="Fecha",
            width=field_width if self.is_mobile else 140,
            value=current_date,
            hint_text="YYYY-MM-DD",
            helper_text="Formato YYYY-MM-DD",
        )
        
        self.description_input = ft.TextField(
            label="Descripción",
            width=field_width,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        
        self.amount_input = ft.TextField(
            label="Monto",
            width=field_width if self.is_mobile else 140,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0.00",  # Valor por defecto para evitar errores
            prefix_text="$",
        )
        
        # Categorías de gastos disponibles
        category_options = [
            ft.dropdown.Option("compra_inventario", "Compra de Inventario"),
            ft.dropdown.Option("operativo", "Gasto Operativo"),
            ft.dropdown.Option("salarios", "Salarios"),
            ft.dropdown.Option("servicios", "Servicios"),
            ft.dropdown.Option("otros", "Otros Gastos"),
        ]
        
        self.category_input = ft.Dropdown(
            label="Categoría",
            width=field_width,
            options=category_options,
            value="otros"  # Valor por defecto
        )
        
        # Dropdown para proveedores
        supplier_options = [ft.dropdown.Option("0", "Seleccione un proveedor (opcional)")]
        
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
        
        # Sección de información básica del gasto
        basic_info_section = ft.Container(
            content=ft.Column([
                ft.Text("Información Básica",
                        weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    ft.Column([self.description_input], expand=True),
                ]),
                ft.Row([
                    ft.Column([self.amount_input], expand=self.is_tablet),
                    ft.Column([self.date_input], expand=self.is_tablet)
                ]) if not self.is_mobile else ft.Column([self.amount_input, self.date_input]),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=15),
            width=form_width
        )
        
        # Sección de categoría y proveedor
        category_section = ft.Container(
            content=ft.Column([
                ft.Text("Categoría y Proveedor",
                        weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    ft.Column([self.category_input], expand=True),
                    ft.Column([self.supplier_input], expand=True)
                ]) if not self.is_mobile else ft.Column([self.category_input, self.supplier_input]),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            margin=ft.margin.only(bottom=15),
            width=form_width
        )
        
        # Construir formulario completo
        self.form_container = ft.Container(
            content=ft.Column([
                basic_info_section,
                category_section
            ], spacing=5),
            width=form_width,
            padding=5,
            alignment=ft.alignment.center
        )
        
        return self.form_container
    
    def save_expense(self, e=None):
        """Guarda un nuevo gasto o actualiza uno existente"""
        try:
            # Obtener datos del formulario
            description = self.description_input.value
            
            # Verificar que la descripción no esté vacía
            if not description:
                show_error_message(
                    self.page, "La descripción del gasto es obligatoria.")
                return
            
            # Manejar valores numéricos con seguridad
            try:
                amount_str = self.amount_input.value.replace('$', '').strip()
                amount = float(amount_str or 0)
                if amount <= 0:
                    show_error_message(
                        self.page, "El monto debe ser mayor que cero.")
                    return
            except (ValueError, TypeError):
                show_error_message(
                    self.page, "Por favor ingrese un monto válido.")
                return
            
            # Procesar la fecha
            try:
                date_str = self.date_input.value
                date_obj = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
            except ValueError:
                show_error_message(
                    self.page, "Formato de fecha inválido. Use YYYY-MM-DD.")
                return
            
            category = self.category_input.value
            
            try:
                supplier_id = int(self.supplier_input.value) if self.supplier_input.value != "0" else None
            except (ValueError, TypeError):
                supplier_id = None

            # Crear diccionario con los datos del gasto
            expense_data = {
                "description": description,
                "amount": amount,
                "date": date_obj,
                "category": category,
                "supplier_id": supplier_id
            }

            if self.edit_mode:
                logging.info(f"Actualizando gasto en modo edición")
                # Obtener el ID del gasto a editar
                expense_id = self.page.client_storage.get("edit_expense_id")
                if expense_id:
                    logging.info(f"Actualizando gasto ID {expense_id}")
                    # Actualizar el gasto existente
                    updated_expense = self.expense_service.update_expense(
                        expense_id, expense_data)
                    
                    if updated_expense:
                        logging.info(f"Gasto actualizado exitosamente: {updated_expense.description}")
                        show_success_message(
                            self.page, "Gasto actualizado exitosamente.")
                        # Regresar a la vista de gastos
                        self.page.client_storage.remove("edit_expense_id")
                        self.go_back(None)
                    else:
                        logging.error(f"Fallo al actualizar el gasto ID {expense_id}")
                        show_error_message(
                            self.page, "No se pudo actualizar el gasto.")
                else:
                    logging.error("Error: No se encontró el ID del gasto a editar")
                    show_error_message(
                        self.page, "Error: No se pudo identificar el gasto a editar.")
            else:
                # Crear un nuevo gasto
                logging.info(f"Creando nuevo gasto: {description}")
                new_expense = self.expense_service.create_expense(expense_data)
                
                if new_expense:
                    logging.info(f"Gasto creado exitosamente: {new_expense.description} (ID: {new_expense.id})")
                    show_success_message(
                        self.page, "Gasto agregado exitosamente.")
                    # Volver a la vista de gastos después de agregar
                    self.go_back(None)
                else:
                    logging.error(f"Fallo al crear el nuevo gasto: {description}")
                    show_error_message(
                        self.page, "No se pudo crear el gasto.")
                
        except ValueError as ve:
            logging.error(f"Error de valor en save_expense: {str(ve)}")
            show_error_message(
                self.page, "Por favor ingrese valores numéricos válidos para el monto.")
        except Exception as e:
            logging.error(f"Error en save_expense: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(
                self.page, f"Error al {'actualizar' if self.edit_mode else 'agregar'} el gasto: {str(e)}")
    
    def go_back(self, e):
        """Vuelve a la pantalla de gastos."""
        try:
            logging.info("Volviendo a la vista de gastos")
            from pages.expences.PageExpences import PageExpense
            # Crear una instancia de la página de gastos
            expenses_page = PageExpense(self.page, self.session, lambda: self.page.go("/reports"))
            # Limpiar controles actuales
            self.controls.clear()
            # Añadir la página de gastos a los controles
            self.controls.append(expenses_page)
            # Actualizar la UI
            self.update()
            logging.info("Vista de gastos cargada exitosamente")
        except Exception as e:
            logging.error(f"Error al volver a gastos: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al volver a gastos: {str(e)}")
    
    def clear_inputs(self):
        # Verificar que los campos estén inicializados antes de limpiarlos
        if hasattr(self, 'description_input') and self.description_input:
            self.description_input.value = ""
        if hasattr(self, 'amount_input') and self.amount_input:
            self.amount_input.value = "0.00"
        if hasattr(self, 'date_input') and self.date_input:
            self.date_input.value = datetime.now().strftime("%Y-%m-%d")
        if hasattr(self, 'category_input') and self.category_input:
            self.category_input.value = "otros"
        if hasattr(self, 'supplier_input') and self.supplier_input:
            self.supplier_input.value = "0"
        self.page.update()
    
    def load_expense_data(self):
        try:
            # Obtener el ID del gasto a editar del almacenamiento del cliente
            expense_id = self.page.client_storage.get("edit_expense_id")
            
            if not expense_id:
                logging.error("No se encontró el ID del gasto a editar en el client_storage")
                show_error_message(self.page, "No se pudo determinar qué gasto editar")
                return
                
            logging.info(f"Cargando datos para el gasto ID: {expense_id}")
            
            # Obtener los datos del gasto
            expense = self.expense_service.get_expense_by_id(expense_id)
            
            if not expense:
                logging.error(f"No se pudo obtener los datos del gasto ID {expense_id}")
                show_error_message(self.page, "No se pudo cargar los datos del gasto")
                self.go_back(None)  # Regresar a la vista de gastos
                return
                
            logging.info(f"Datos del gasto obtenidos correctamente: {expense.description}")
            
            # Verificar que los campos estén inicializados antes de asignar valores
            if hasattr(self, 'description_input') and self.description_input:
                self.description_input.value = expense.description or ""
                logging.info(f"Descripción del gasto establecida: {expense.description}")
            
            if hasattr(self, 'amount_input') and self.amount_input:
                self.amount_input.value = str(expense.amount or 0)
                logging.info(f"Monto del gasto establecido: {expense.amount}")
            
            if hasattr(self, 'date_input') and self.date_input:
                self.date_input.value = expense.date.strftime("%Y-%m-%d") if expense.date else datetime.now().strftime("%Y-%m-%d")
                logging.info(f"Fecha del gasto establecida: {self.date_input.value}")
            
            if hasattr(self, 'category_input') and self.category_input:
                self.category_input.value = expense.category or "otros"
                logging.info(f"Categoría del gasto establecida: {expense.category}")
            
            if hasattr(self, 'supplier_input') and self.supplier_input:
                self.supplier_input.value = str(expense.supplier_id) if expense.supplier_id else "0"
                logging.info(f"Proveedor del gasto establecido: {expense.supplier_id}")
            
            # Actualizar la UI después de cargar todos los datos
            self.page.update()
            logging.info("Datos del gasto cargados correctamente en el formulario")
            
        except Exception as e:
            logging.error(f"Error al cargar datos del gasto: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al cargar los datos del gasto: {str(e)}")
    
    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        new_is_tablet = 600 <= self.page.width < 1024
        if new_is_mobile != self.is_mobile or new_is_tablet != self.is_tablet:
            self.is_mobile = new_is_mobile
            self.is_tablet = new_is_tablet
            self.build_ui()
            self.update()
    
    def build(self):
        return ft.Column(self.controls, expand=True) 