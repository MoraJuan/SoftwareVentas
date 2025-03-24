import flet as ft
from services.inventoryHistoryService import InventoryHistoryService
from services.productService import ProductService
from ui.components.data_table import DataTable
from ui.components.alerts import show_error_message, show_success_message
import logging
from datetime import datetime, timedelta

class PageInventoryHistory(ft.UserControl):
    def __init__(self, page: ft.Page, session, product_id=None):
        super().__init__()
        self.page = page
        self.session = session
        self.inventory_history_service = InventoryHistoryService(session)
        self.product_service = ProductService(session)
        self.is_mobile = self.page.width < 600
        self.product_id = product_id  # Si se proporciona, filtra por este producto
        self.history_data = []
        self.table = None
        self.table_container = None
        self.product_dropdown = None
        self.start_date_picker = None
        self.end_date_picker = None
        self.filter_type_dropdown = None
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            # Configurar fechas por defecto (último mes)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Formato de fechas para mostrar
            end_date_str = end_date.strftime('%d/%m/%Y')
            start_date_str = start_date.strftime('%d/%m/%Y')
            
            logging.info(f"Fechas por defecto: {start_date_str} - {end_date_str}")
            
            # Cargar datos iniciales con las fechas establecidas
            self.load_history(start_date=start_date, end_date=end_date)

            # Título y descripción
            title_section = ft.Column([
                ft.Text(
                    "Inventario",
                    size=20 if self.is_mobile else 24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                ft.Text(
                    "Registro de movimientos de productos",
                    size=14 if self.is_mobile else 16,
                    color=ft.colors.ON_SURFACE_VARIANT
                ),
                ft.Container(height=10),
            ])

            # Obtener lista de productos para el dropdown
            products = self.product_service.get_all_products()
            product_options = [
                ft.dropdown.Option(text=p.name, key=str(p.id))
                for p in products
            ]
            product_options.insert(0, ft.dropdown.Option(text="Todos los productos", key="all"))

            # Tipos de cambio para el dropdown
            change_types = [
                ft.dropdown.Option(text="Todos los tipos", key="all"),
                ft.dropdown.Option(text="Entrada", key="entrada"),
                ft.dropdown.Option(text="Salida", key="salida"),
                ft.dropdown.Option(text="Ajuste", key="ajuste"),
                ft.dropdown.Option(text="Venta", key="venta"),
                ft.dropdown.Option(text="Compra", key="compra"),
            ]

            # Filtros
            self.product_dropdown = ft.Dropdown(
                label="Producto",
                width=300,
                options=product_options,
                value="all" if not self.product_id else str(self.product_id),
                on_change=self.filter_history
            )

            self.filter_type_dropdown = ft.Dropdown(
                label="Tipo de movimiento",
                width=200,
                options=change_types,
                value="all",
                on_change=self.filter_history
            )

            self.start_date_picker = ft.DatePicker(
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2030, 12, 31),
                current_date=start_date,
                on_change=self.on_start_date_change,
            )

            self.end_date_picker = ft.DatePicker(
                first_date=datetime(2020, 1, 1),
                last_date=datetime(2030, 12, 31),
                current_date=end_date,
                on_change=self.on_end_date_change,
            )

            # Botones de fechas
            start_date_btn = ft.ElevatedButton(
                "Fecha inicial",
                icon=ft.icons.CALENDAR_TODAY,
                on_click=lambda _: self.start_date_picker.pick_date()
            )

            end_date_btn = ft.ElevatedButton(
                "Fecha final",
                icon=ft.icons.CALENDAR_TODAY,
                on_click=lambda _: self.end_date_picker.pick_date()
            )

            # Mostrar fechas seleccionadas
            self.start_date_text = ft.Text(
                f"Desde: {start_date.strftime('%d/%m/%Y')}",
                size=14,
                color=ft.colors.ON_SURFACE
            )

            self.end_date_text = ft.Text(
                f"Hasta: {end_date.strftime('%d/%m/%Y')}",
                size=14,
                color=ft.colors.ON_SURFACE
            )

            # Botón de búsqueda
            search_btn = ft.FilledButton(
                "Buscar",
                icon=ft.icons.SEARCH,
                on_click=self.filter_history
            )

            # Botón para volver a inventario
            back_btn = ft.OutlinedButton(
                "Volver a Inventario",
                icon=ft.icons.ARROW_BACK,
                on_click=lambda _: self.back_to_inventory()
            )

            # Fila de filtros (responsive)
            filters_row = ft.Column([
                ft.Row([
                    self.product_dropdown,
                    self.filter_type_dropdown,
                ], wrap=True, spacing=10),
                ft.Row([
                    ft.Column([
                        start_date_btn,
                        self.start_date_text,
                    ], spacing=5),
                    ft.Column([
                        end_date_btn,
                        self.end_date_text,
                    ], spacing=5),
                    search_btn,
                ], wrap=True, spacing=10),
                back_btn,
            ]) if self.is_mobile else ft.Column([
                ft.Row([
                    self.product_dropdown,
                    self.filter_type_dropdown,
                    ft.Column([
                        start_date_btn,
                        self.start_date_text,
                    ], spacing=5),
                    ft.Column([
                        end_date_btn,
                        self.end_date_text,
                    ], spacing=5),
                    search_btn,
                ], wrap=True, spacing=10),
                back_btn,
            ])

            # Tabla de historial
            table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)

            # Definir las columnas que vamos a mostrar
            self.table_columns = ["ID", "Fecha", "Producto", "Tipo", "Cantidad", "Stock Anterior", "Stock Nuevo", "Motivo"]
            
            # Preparar datos para la tabla
            self.table = DataTable(
                columns=self.table_columns,
                data=self.get_history_data(),
                items_per_page=15,
                on_select=None,  # Solo visualización
            )

            # Usar Column para scroll y Container para estilo
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

            # UI principal 
            content_column = ft.Column(
                [
                    title_section,
                    filters_row,
                    ft.Container(height=10),
                    self.table_wrapper,
                    ft.Text(
                        f"Total: {len(self.history_data)} movimientos", 
                        size=12, 
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
            
            # Envolvemos el Column en un Container para aplicar el padding
            self.controls = [
                ft.Container(
                    content=content_column,
                    padding=10 if self.is_mobile else 20
                ),
                self.start_date_picker,
                self.end_date_picker,
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de historial de inventario: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            self.controls = [ft.Text(f"Error al cargar el historial: {str(e)}", color=ft.colors.ERROR)]

    def on_start_date_change(self, e):
        try:
            if e.control.current_date:
                selected_date = e.control.current_date
                # La fecha proviene como una cadena ISO, necesitamos convertirla a objeto datetime
                if isinstance(selected_date, str):
                    selected_date = datetime.fromisoformat(selected_date.replace('Z', '+00:00'))
                formatted_date = selected_date.strftime('%d/%m/%Y')
                logging.info(f"Fecha inicial seleccionada: {formatted_date}")
                self.start_date_text.value = f"Desde: {formatted_date}"
                self.update()
                # Aplicar el filtro automáticamente al cambiar la fecha
                self.filter_history()
        except Exception as ex:
            logging.error(f"Error al cambiar fecha inicial: {str(ex)}")
            import traceback
            logging.error(traceback.format_exc())

    def on_end_date_change(self, e):
        try:
            if e.control.current_date:
                selected_date = e.control.current_date
                # La fecha proviene como una cadena ISO, necesitamos convertirla a objeto datetime
                if isinstance(selected_date, str):
                    selected_date = datetime.fromisoformat(selected_date.replace('Z', '+00:00'))
                formatted_date = selected_date.strftime('%d/%m/%Y')
                logging.info(f"Fecha final seleccionada: {formatted_date}")
                self.end_date_text.value = f"Hasta: {formatted_date}"
                self.update()
                # Aplicar el filtro automáticamente al cambiar la fecha
                self.filter_history()
        except Exception as ex:
            logging.error(f"Error al cambiar fecha final: {str(ex)}")
            import traceback
            logging.error(traceback.format_exc())

    def build(self):
        return ft.Column(self.controls, expand=True)

    def load_history(self, e=None, start_date=None, end_date=None):
        try:
            logging.info("Cargando historial de inventario")
            
            # Si hay un producto específico, filtrar por él
            if self.product_id:
                all_history = self.inventory_history_service.get_history_by_product(self.product_id)
            else:
                # Por defecto, cargar los movimientos más recientes
                all_history = self.inventory_history_service.get_recent_history(limit=500)
            
            logging.info(f"Total de movimientos disponibles: {len(all_history)}")
            
            # Aplicar filtro de fechas si se proporcionan
            if start_date and end_date:
                logging.info(f"Filtrando por fechas: {start_date} - {end_date}")
                self.history_data = [h for h in all_history if start_date <= h.date <= end_date]
            else:
                self.history_data = all_history
            
            logging.info(f"Movimientos a mostrar después del filtrado: {len(self.history_data)}")
            
            if self.table:
                filtered_data = self.get_history_data()
                self.table.set_data(filtered_data)
                logging.info("Datos establecidos en la tabla")
            
            self.update()
        
        except Exception as e:
            logging.error(f"Error al cargar historial: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al cargar historial: {str(e)}")

    def filter_history(self, e=None):
        try:
            logging.info("Aplicando filtros al historial")
            
            # Obtener valores de los filtros
            product_id = self.product_dropdown.value
            change_type = self.filter_type_dropdown.value
            
            # Convertir las fechas de texto a objetos datetime
            start_date_str = self.start_date_text.value.replace("Desde: ", "")
            end_date_str = self.end_date_text.value.replace("Hasta: ", "")
            
            try:
                # Formatear correctamente las fechas
                logging.info(f"Convirtiendo fechas para filtrado: {start_date_str} - {end_date_str}")
                
                # Utilizar el formato día/mes/año
                day_start, month_start, year_start = map(int, start_date_str.split('/'))
                start_date = datetime(year_start, month_start, day_start, 0, 0, 0)
                
                day_end, month_end, year_end = map(int, end_date_str.split('/'))
                end_date = datetime(year_end, month_end, day_end, 23, 59, 59, 999999)
                
                logging.info(f"Fechas convertidas correctamente: {start_date} - {end_date}")
            except Exception as date_error:
                # Si hay error en el formato de fecha, usar fechas por defecto
                logging.error(f"Error al convertir fechas: {str(date_error)}")
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                logging.info(f"Usando fechas por defecto: {start_date} - {end_date}")
            
            # Aplicar filtros - primero conseguir todos los datos
            if product_id != "all":
                logging.info(f"Filtrando por producto ID: {product_id}")
                all_history = self.inventory_history_service.get_history_by_product(int(product_id))
            else:
                logging.info("Obteniendo todo el historial reciente")
                all_history = self.inventory_history_service.get_recent_history(limit=500)
            
            logging.info(f"Total de registros obtenidos: {len(all_history)}")
            
            # Filtrar por fechas explícitamente
            filtered_history = []
            for item in all_history:
                try:
                    item_date = item.date
                    # Verificar si la fecha está en el rango
                    if start_date <= item_date <= end_date:
                        # Si hay filtro de tipo, verificar también
                        if change_type == "all" or (hasattr(item, 'change_type') and item.change_type.lower() == change_type.lower()):
                            filtered_history.append(item)
                    else:
                        logging.debug(f"Fecha fuera de rango: {item_date}, rango: {start_date} - {end_date}")
                except Exception as item_error:
                    logging.error(f"Error al procesar item para filtro: {str(item_error)}")
                    continue
            
            # Actualizar los datos filtrados
            self.history_data = filtered_history
            logging.info(f"Total de registros después de filtrar: {len(self.history_data)}")
            
            # Actualizar la tabla
            if self.table:
                filtered_data = self.get_history_data()
                logging.info(f"Registros procesados para mostrar: {len(filtered_data)}")
                self.table.set_data(filtered_data)
                
                # Actualizar el texto de resumen
                for control in self.controls:
                    if isinstance(control, ft.Container) and control.content:
                        content_column = control.content
                        if isinstance(content_column, ft.Column) and len(content_column.controls) > 4:
                            result_text = content_column.controls[4]
                            if isinstance(result_text, ft.Text):
                                result_text.value = f"Total: {len(filtered_data)} movimientos"
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al filtrar historial: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al aplicar filtros: {str(e)}")

    def get_history_data(self):
        data = []
        for h in self.history_data:
            try:
                # Verificar que el objeto h tenga los atributos necesarios
                if not hasattr(h, 'id') or not hasattr(h, 'date') or not hasattr(h, 'change_amount'):
                    logging.warning(f"Registro de historial incompleto: {h}")
                    continue
                
                # Formatear el signo de la cantidad según el tipo de cambio
                if h.change_amount > 0:
                    amount_str = f"+{h.change_amount}"
                else:
                    amount_str = f"{h.change_amount}"
                    
                # Formatear la fecha
                try:
                    date_str = h.date.strftime("%d/%m/%Y %H:%M")
                except Exception as date_error:
                    logging.error(f"Error al formatear fecha: {str(date_error)}")
                    date_str = "Fecha desconocida"
                
                # Verificar si el producto existe
                product_name = "Producto eliminado"
                if hasattr(h, 'product') and h.product is not None:
                    product_name = h.product.name
                
                # Asegurarse de que todas las claves requeridas estén presentes
                row_data = {
                    "ID": str(h.id),
                    "Fecha": date_str,
                    "Producto": product_name,
                    "Tipo": h.change_type.capitalize() if hasattr(h, 'change_type') else "Desconocido",
                    "Cantidad": amount_str,
                    "Stock Anterior": str(h.previous_stock) if hasattr(h, 'previous_stock') else "0",
                    "Stock Nuevo": str(h.new_stock) if hasattr(h, 'new_stock') else "0",
                    "Motivo": h.change_reason if hasattr(h, 'change_reason') and h.change_reason else "No especificado",
                    "history_item": h
                }
                data.append(row_data)
            except Exception as e:
                logging.error(f"Error procesando registro de historial: {str(e)}")
                # Continuar con el siguiente registro si hay un error
                continue
                
        return data

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
            self.update()

    def back_to_inventory(self):
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