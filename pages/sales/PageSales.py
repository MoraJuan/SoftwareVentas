import flet as ft
from pages.sales.make_sale import MakeSaleView
from ui.components.alerts import show_error_message, show_success_message
#from ui.components.navigation import create_navigation_rail, ThemeIconButton
from services.saleService import SaleService
from services.productService import ProductService
from datetime import datetime, timedelta
import logging

class PageSales(ft.UserControl):
    def __init__(self, page: ft.Page, session):
        super().__init__()
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.product_service = ProductService(session)
        self.all_sales = []  # Lista para almacenar todas las ventas
        self.filtered_sales = []  # Lista para almacenar ventas filtradas
        self.sort_column_index = 0  # Por defecto ordenar por ID (índice 0)
        self.sort_ascending = False  # Por defecto orden descendente
        self.current_page = 1  # Página actual
        self.sales_per_page = 10  # Ventas por página
        
        # Verificar que la página sea válida antes de acceder a su ancho
        if self.page is None:
            logging.error("Error: page es None en __init__ de PageSales")
            self.is_mobile = True  # Valor por defecto
            self.is_tablet = False
        else:
            self.is_mobile = self.page.width < 600
            self.is_tablet = 600 <= self.page.width < 1024
            # Configurar evento de resize solo si la página es válida
            self.page.on_resize = self.handle_resize
            
        # Construir la interfaz
        self.build_ui()
        
        # Cargar las ventas automáticamente al inicializar
        self.load_sales()

    def handle_resize(self, e):
        """Maneja el evento de redimensionamiento de la ventana"""
        try:
            # Verificar que self.page no sea None antes de acceder a width
            if not hasattr(self, 'page') or self.page is None:
                logging.error("Error: self.page es None en handle_resize")
                return
                
            new_is_mobile = self.page.width < 600
            new_is_tablet = 600 <= self.page.width < 1024

            logging.info(f"Resize detectado en PageSales - Ancho: {self.page.width}, Mobile: {new_is_mobile}, Tablet: {new_is_tablet}")

            # Solo reconstruir la UI si cambia la clasificación del dispositivo
            if new_is_mobile != self.is_mobile or new_is_tablet != self.is_tablet:
                logging.info(f"Cambiando modo de dispositivo en PageSales a: {'mobile' if new_is_mobile else 'tablet' if new_is_tablet else 'desktop'}")
                self.is_mobile = new_is_mobile
                self.is_tablet = new_is_tablet
                
                # Reconstruir completamente la UI
                self.controls.clear()
                self.build_ui()
                self.update()
                return
                
            # Si solo cambia el tamaño pero no la clasificación, ajustar componentes específicos
            if hasattr(self, 'table_container') and self.table_container is not None:
                try:
                    # Ajustar ancho de la tabla
                    table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
                    
                    # En móvil, el contenedor exterior es el que tiene el scroll horizontal
                    if self.is_mobile and isinstance(self.table_container, ft.Container) and hasattr(self.table_container, 'content'):
                        if hasattr(self.table_container.content, 'width'):
                            self.table_container.content.width = table_width
                    else:
                        self.table_container.width = table_width
                    
                    # Ajustar campo de búsqueda
                    if hasattr(self, 'search_field') and self.search_field is not None:
                        search_width = self.page.width * 0.9 if self.is_mobile else None
                        self.search_field.width = search_width
                    
                    # Ajustar botones según el dispositivo
                    for btn_name in ['btn_new_sale', 'btn_refresh', 'btn_export']:
                        if hasattr(self, btn_name) and getattr(self, btn_name) is not None:
                            btn = getattr(self, btn_name)
                            btn.text = "" if self.is_mobile else {
                                'btn_new_sale': "Nueva Venta",
                                'btn_refresh': "Actualizar Datos",
                                'btn_export': "Exportar a Excel"
                            }.get(btn_name, "")
                            btn.tooltip = {
                                'btn_new_sale': "Nueva Venta",
                                'btn_refresh': "Actualizar Datos",
                                'btn_export': "Exportar a Excel"
                            }.get(btn_name, None) if self.is_mobile else None
                    
                    # Forzar actualización completa
                    self.update()
                except Exception as e:
                    logging.error(f"Error al ajustar componentes en resize: {str(e)}")
                    import traceback
                    logging.error(traceback.format_exc())
        except Exception as e:
            logging.error(f"Error en handle_resize: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())

    def build_ui(self):
        try:
            # Título principal con tamaño adaptado a dispositivo
            header_font_size = 20 if self.is_mobile else 24
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Gestión de Ventas", 
                        size=header_font_size, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Botones de acción adaptados al tamaño
            button_spacing = 5 if self.is_mobile else 10
            button_text = "" if self.is_mobile else "Nueva Venta"
            
            self.btn_new_sale = ft.FilledButton(
                text=button_text,
                icon=ft.icons.ADD_SHOPPING_CART,
                on_click=lambda _: self.show_make_sale(),
                tooltip="Nueva Venta" if self.is_mobile else None
            )
            
            self.btn_refresh = ft.OutlinedButton(
                text="" if self.is_mobile else "Actualizar Datos",
                icon=ft.icons.REFRESH,
                on_click=self.refresh_data,
                tooltip="Actualizar Datos" if self.is_mobile else None
            )
            
            self.btn_export = ft.FilledTonalButton(
                text="" if self.is_mobile else "Exportar a Excel",
                icon=ft.icons.DOWNLOAD,
                on_click=self.export_to_excel,
                tooltip="Exportar a Excel" if self.is_mobile else None
            )
            
            action_buttons = ft.Row([
                self.btn_new_sale,
                self.btn_refresh,
                self.btn_export
            ], spacing=button_spacing, wrap=True if self.is_mobile else False)
            
            # Crear campo de búsqueda adaptable
            search_width = self.page.width * 0.9 if self.is_mobile else None
            self.search_field = ft.TextField(
                label="Buscar ventas",
                prefix_icon=ft.icons.SEARCH,
                expand=True if not self.is_mobile else False,
                width=search_width,
                border_radius=20,
                on_change=self.filter_sales,
                hint_text="Ingrese ID, cliente o estado...",
                height=50
            )

            # Crear tabla de ventas
            self.sales_table = self.build_sales_table()
            
            # Contenedor para la tabla que se actualizará
            table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            table_inner_container = ft.Container(
                content=self.sales_table,
                width=table_width
            )
            
            # Para móviles, usar un contenedor con scroll horizontal
            if self.is_mobile:
                self.table_container = ft.Container(
                    content=table_inner_container,
                    expand=True,
                    scroll=ft.ScrollMode.HORIZONTAL
                )
            else:
                # Para tablets y desktop, no necesitamos scroll horizontal
                self.table_container = table_inner_container
                self.table_container.expand = True
            
            # Crear botones de paginación
            self.btn_first_page = ft.IconButton(
                icon=ft.icons.FIRST_PAGE,
                tooltip="Primera página",
                on_click=self.go_to_first_page,
                disabled=self.current_page == 1,
                icon_color=ft.colors.PRIMARY
            )
            
            self.btn_prev_page = ft.IconButton(
                icon=ft.icons.CHEVRON_LEFT,
                tooltip="Página anterior",
                on_click=self.go_to_prev_page,
                disabled=self.current_page == 1,
                icon_color=ft.colors.PRIMARY
            )
            
            self.page_info = ft.Text(
                f"Página {self.current_page} de 1",
                color=ft.colors.ON_SURFACE,
                size=12 if self.is_mobile else 14
            )
            
            self.btn_next_page = ft.IconButton(
                icon=ft.icons.CHEVRON_RIGHT,
                tooltip="Página siguiente",
                on_click=self.go_to_next_page,
                disabled=True,
                icon_color=ft.colors.PRIMARY
            )
            
            self.btn_last_page = ft.IconButton(
                icon=ft.icons.LAST_PAGE,
                tooltip="Última página",
                on_click=self.go_to_last_page,
                disabled=True,
                icon_color=ft.colors.PRIMARY
            )
            
            pagination = ft.Row([
                self.btn_first_page,
                self.btn_prev_page,
                self.page_info,
                self.btn_next_page,
                self.btn_last_page
            ], alignment=ft.MainAxisAlignment.CENTER)

            # Layout adaptable para título y botones de acción
            if not self.is_mobile:
                header_row = ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                "Ventas Recientes",
                                size=18 if self.is_mobile else 20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.ON_SURFACE
                            ),
                            expand=True
                        ),
                        action_buttons
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            else:
                header_row = ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                "Ventas Recientes",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.ON_SURFACE
                            ),
                            alignment=ft.alignment.center_left
                        ),
                        action_buttons
                    ],
                    spacing=10
                )
            
            # Sección de ventas recientes
            sales_section = ft.Column([
                header_row,
                self.search_field,
                self.table_container,
                pagination
            ], spacing=20, expand=True)
            
            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                sales_section,
            ], spacing=20)

            # Configurar el control principal
            padding_value = 10 if self.is_mobile else 20
            
            self.controls = [
                ft.Column(
                    [
                        ft.Container(
                            content=main_content,
                            padding=padding_value,
                            expand=True
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START
                )
            ]
            
            # Cargar datos
            self.load_recent_sales()

        except Exception as e:
            logging.error(f"Error construyendo UI: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")
            
            # UI básica en caso de error
            self.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.icons.ERROR, color=ft.colors.ERROR, size=64),
                        ft.Text(
                            "Error al cargar la interfaz",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        ft.Text(
                            str(e),
                            color=ft.colors.ON_SURFACE
                        ),
                        ft.ElevatedButton(
                            text="Reintentar",
                            on_click=lambda _: self.build_ui()
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=20
                )
            ]
    
    def show_make_sale(self):
        """Muestra la vista para realizar una nueva venta"""
        try:
            logging.info("Mostrando vista de nueva venta...")
            # Guardar el handler de resize original 
            self.original_resize_handler = self.page.on_resize
            
            # Limpiar controles actuales
            self.controls.clear()
            
            # Crear y mostrar la vista de nueva venta
            from pages.sales.make_sale import MakeSaleView
            make_sale_view = MakeSaleView(self.page, self.session)
            self.controls.append(make_sale_view)
            
            # Actualizar para mostrar la nueva vista
            self.update()
        except Exception as e:
            logging.error(f"Error al mostrar vista de nueva venta: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            show_error_message(self.page, f"Error al mostrar vista de nueva venta: {str(e)}")
            
            # Reconstruir la vista de ventas en caso de error
            self.controls.clear()
            self.build_ui()
            self.update()

    def build_sales_table(self):
        try:
            # Crear tabla de ventas
            columns = [
                ft.DataColumn(
                    ft.Text("ID", color=ft.colors.ON_SURFACE),
                    on_sort=lambda e: self.sort_column(0)
                ),
                ft.DataColumn(
                    ft.Text("Fecha", color=ft.colors.ON_SURFACE),
                    on_sort=lambda e: self.sort_column(1)
                ),
                ft.DataColumn(
                    ft.Text("Cliente", color=ft.colors.ON_SURFACE),
                    on_sort=lambda e: self.sort_column(2)
                ),
                ft.DataColumn(
                    ft.Text("Total", color=ft.colors.ON_SURFACE),
                    on_sort=lambda e: self.sort_column(3)
                ),
                ft.DataColumn(
                    ft.Text("Estado", color=ft.colors.ON_SURFACE),
                    on_sort=lambda e: self.sort_column(4)
                ),
                ft.DataColumn(ft.Text("Acciones", color=ft.colors.ON_SURFACE)),
            ]
            
            # Si existe índice de ordenación, mostrar ícono
            try:
                if hasattr(self, 'sort_column_index') and self.sort_column_index is not None:
                    sort_index = self.sort_column_index
                    if 0 <= sort_index < len(columns):  # Validar índice
                        # Modificar el label para incluir un ícono
                        original_text = columns[sort_index].label
                        icon_name = ft.icons.ARROW_UPWARD if self.sort_ascending else ft.icons.ARROW_DOWNWARD
                        
                        # Crear un Row con el texto original y el ícono
                        columns[sort_index].label = ft.Row([
                            ft.Text(original_text.value if hasattr(original_text, 'value') else "Columna", color=ft.colors.ON_SURFACE),
                            ft.Icon(icon_name, color=ft.colors.PRIMARY, size=16)
                        ], spacing=4)
            except Exception as e:
                logging.error(f"Error al añadir ícono de ordenamiento: {str(e)}")
            
            return ft.DataTable(
                columns=columns,
                rows=[],
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                heading_row_height=70,
                data_row_max_height=80,
                column_spacing=10,
                divider_thickness=1
            )
        except Exception as e:
            logging.error(f"Error construyendo tabla de ventas: {str(e)}")
            # Crear una tabla simple en caso de error
            return ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Error al cargar tabla", color=ft.colors.ERROR))],
                rows=[],
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10
            )
            
    def load_recent_sales(self):
        try:
            # Obtener ventas de los últimos 30 días
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Obtener ventas recientes
            try:
                self.all_sales = self.sale_service.get_sales_between_dates(start_date, end_date)
            except Exception as e:
                logging.error(f"Error al obtener ventas desde el servicio: {str(e)}")
                self.all_sales = []
            
            if self.all_sales is None:
                self.all_sales = []
            
            # Aplicar filtros actuales
            self.filtered_sales = self.all_sales.copy()
            
            # Ordenar ventas
            self.sort_sales()
            
            # Actualizar tabla con ventas de la página actual
            self.update_table_with_sales(self.get_current_page_sales())
            
            # Actualizar información de paginación
            self.update_pagination()
            
        except Exception as e:
            logging.error(f"Error al cargar ventas recientes: {str(e)}")
            # No mostrar mensaje de error, pero reiniciar la tabla
            self.all_sales = []
            self.filtered_sales = []
            try:
                self.update_table_with_sales([])
                self.update_pagination()
            except:
                pass
            
    def update_table_with_sales(self, sales):
        try:
            # Crear filas para la tabla
            rows = []
            
            # Verificar que sales no sea None
            if sales is None:
                logging.warning("Lista de ventas es None, usando lista vacía")
                sales = []
            
            logging.info(f"Actualizando tabla con {len(sales)} ventas")
            
            for sale in sales:
                try:
                    # Formatear fecha
                    date_str = sale.date.strftime("%d/%m/%Y %H:%M") if sale.date else "N/A"
                    
                    # Obtener nombre del cliente
                    customer_name = sale.customer.name if sale.customer and hasattr(sale.customer, 'name') else "Cliente no registrado"
                    
                    # Formatear estado
                    status_color = ft.colors.GREEN if sale.status == 'completed' else ft.colors.ERROR
                    status_text = "Completada" if sale.status == 'completed' else "Cancelada"
                    
                    # Crear fila
                    sale_id = sale.id
                    row = ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(sale_id), color=ft.colors.ON_SURFACE)),
                            ft.DataCell(ft.Text(date_str, color=ft.colors.ON_SURFACE)),
                            ft.DataCell(ft.Text(customer_name, color=ft.colors.ON_SURFACE)),
                            ft.DataCell(ft.Text(f"${sale.total_amount:.2f}", color=ft.colors.ON_SURFACE, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(status_text, color=ft.colors.WHITE),
                                    bgcolor=status_color,
                                    border_radius=15,
                                    padding=5,
                                    alignment=ft.alignment.center,
                                    width=100
                                )
                            ),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.VISIBILITY,
                                        icon_color=ft.colors.PRIMARY,
                                        tooltip="Ver detalles",
                                        on_click=self.create_view_sale_callback(sale_id)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.PRINT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Imprimir factura",
                                        on_click=lambda _, s=sale_id: self.print_invoice(s)
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ),
                        ]
                    )
                    rows.append(row)
                except Exception as e:
                    logging.error(f"Error procesando venta {getattr(sale, 'id', 'desconocido')}: {str(e)}")
                    # Continuar con la siguiente venta en lugar de fallar todo el proceso
                    continue
            
            # Verificar que la tabla exista antes de intentar actualizarla
            if hasattr(self, 'sales_table') and self.sales_table is not None:
                # Actualizar tabla
                logging.info(f"Actualizando tabla con {len(rows)} filas")
                self.sales_table.rows = rows
                
                # Si la tabla está dentro de un contenedor, asegurarse de actualizarlo también
                if hasattr(self, 'table_container') and self.table_container is not None:
                    if hasattr(self.table_container, 'content') and self.table_container.content is not None:
                        if self.table_container.content != self.sales_table:
                            logging.info("Actualizando contenedor de tabla")
                            self.table_container.content = self.sales_table
                
                # Actualizar UI
                self.update()
                
                # Forzar actualización de la página
                if hasattr(self, 'page') and self.page is not None:
                    self.page.update()
            else:
                logging.error("La tabla de ventas no está inicializada correctamente")
            
        except Exception as e:
            logging.error(f"Error al actualizar tabla de ventas: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            # Intentar crear una tabla vacía si la tabla actual falló
            try:
                if hasattr(self, 'sales_table') and self.sales_table is not None:
                    self.sales_table.rows = []
                    self.update()
            except:
                pass
    
    def get_current_page_sales(self):
        """Obtiene las ventas de la página actual"""
        try:
            # Verificar que filtered_sales exista y no sea None
            if not hasattr(self, 'filtered_sales') or self.filtered_sales is None:
                logging.warning("Lista de ventas filtradas no está inicializada, inicializando como lista vacía")
                self.filtered_sales = []
                return []
                
            start_idx = (self.current_page - 1) * self.sales_per_page
            end_idx = start_idx + self.sales_per_page
            
            # Validar índices
            if start_idx >= len(self.filtered_sales):
                start_idx = 0
                self.current_page = 1
                
            return self.filtered_sales[start_idx:end_idx]
        except Exception as e:
            logging.error(f"Error al obtener ventas de página actual: {str(e)}")
            return []
    
    def update_pagination(self):
        """Actualiza la información de paginación y habilita/deshabilita botones"""
        try:
            # Verificar que los componentes existan
            if not hasattr(self, 'page_info') or self.page_info is None:
                logging.error("El componente page_info no está inicializado")
                return
                
            if not hasattr(self, 'filtered_sales') or self.filtered_sales is None:
                self.filtered_sales = []
                
            # Calcular total de páginas
            total_sales = len(self.filtered_sales)
            total_pages = max((total_sales + self.sales_per_page - 1) // self.sales_per_page, 1)
            
            # Validar página actual
            if self.current_page > total_pages:
                self.current_page = total_pages
            
            # Actualizar información de paginación
            self.page_info.value = f"Página {self.current_page} de {total_pages} (Total: {total_sales} ventas)"
            
            # Verificar que los botones existan
            for btn_name in ['btn_first_page', 'btn_prev_page', 'btn_next_page', 'btn_last_page']:
                if not hasattr(self, btn_name) or getattr(self, btn_name) is None:
                    logging.error(f"El componente {btn_name} no está inicializado")
                    return
            
            # Habilitar/deshabilitar botones de paginación
            self.btn_first_page.disabled = self.current_page == 1
            self.btn_prev_page.disabled = self.current_page == 1
            self.btn_next_page.disabled = self.current_page >= total_pages
            self.btn_last_page.disabled = self.current_page >= total_pages
            
            # Actualizar UI
            self.update()
        except Exception as e:
            logging.error(f"Error al actualizar paginación: {str(e)}")
            # No mostrar errores al usuario para evitar interrupciones
            # Tratar de reparar el estado
            try:
                if hasattr(self, 'page_info') and self.page_info is not None:
                    self.page_info.value = "Página 1 de 1"
                    self.update()
            except:
                pass
    
    def go_to_first_page(self, e=None):
        """Va a la primera página"""
        try:
            if self.current_page != 1:
                self.current_page = 1
                self.update_table_with_sales(self.get_current_page_sales())
                self.update_pagination()
        except Exception as e:
            logging.error(f"Error al ir a la primera página: {str(e)}")
    
    def go_to_prev_page(self, e=None):
        """Va a la página anterior"""
        try:
            if self.current_page > 1:
                self.current_page -= 1
                self.update_table_with_sales(self.get_current_page_sales())
                self.update_pagination()
        except Exception as e:
            logging.error(f"Error al ir a la página anterior: {str(e)}")
    
    def go_to_next_page(self, e=None):
        """Va a la página siguiente"""
        try:
            total_pages = (len(self.filtered_sales) + self.sales_per_page - 1) // self.sales_per_page
            if self.current_page < total_pages:
                self.current_page += 1
                self.update_table_with_sales(self.get_current_page_sales())
                self.update_pagination()
        except Exception as e:
            logging.error(f"Error al ir a la página siguiente: {str(e)}")
    
    def go_to_last_page(self, e=None):
        """Va a la última página"""
        try:
            total_pages = (len(self.filtered_sales) + self.sales_per_page - 1) // self.sales_per_page
            if self.current_page != total_pages:
                self.current_page = total_pages
                self.update_table_with_sales(self.get_current_page_sales())
                self.update_pagination()
        except Exception as e:
            logging.error(f"Error al ir a la última página: {str(e)}")
    
    def sort_column(self, column_index):
        """Ordena la tabla por la columna especificada"""
        try:
            # Si ya estaba ordenada por esta columna, invertir el orden
            if self.sort_column_index == column_index:
                self.sort_ascending = not self.sort_ascending
            else:
                # Si es una nueva columna, ordenar ascendente
                self.sort_column_index = column_index
                self.sort_ascending = True
            
            # Ordenar ventas
            self.sort_sales()
            
            # Reconstruir la tabla para actualizar los iconos de ordenamiento
            self.sales_table = self.build_sales_table()
            self.table_container.content = self.sales_table
            
            # Volver a la primera página
            self.current_page = 1
            
            # Actualizar tabla con ventas ordenadas
            self.update_table_with_sales(self.get_current_page_sales())
            
            # Actualizar paginación
            self.update_pagination()
        except Exception as e:
            logging.error(f"Error al ordenar ventas: {str(e)}")
            show_error_message(self.page, f"Error al ordenar ventas: {str(e)}")
    
    def sort_sales(self):
        """Ordena las ventas según la columna seleccionada"""
        try:
            # Verificar que la lista de ventas filtradas exista
            if not hasattr(self, 'filtered_sales') or self.filtered_sales is None:
                self.filtered_sales = []
                return
                
            if len(self.filtered_sales) == 0:
                return
                
            # Definir la función de ordenamiento según el índice de columna
            if self.sort_column_index == 0:  # ID
                key_func = lambda s: getattr(s, 'id', 0)
            elif self.sort_column_index == 1:  # Fecha
                key_func = lambda s: getattr(s, 'date', datetime.min)
            elif self.sort_column_index == 2:  # Cliente
                key_func = lambda s: getattr(getattr(s, 'customer', None), 'name', '').lower() if getattr(s, 'customer', None) else ''
            elif self.sort_column_index == 3:  # Total
                key_func = lambda s: getattr(s, 'total_amount', 0) or 0
            elif self.sort_column_index == 4:  # Estado
                key_func = lambda s: getattr(s, 'status', '') or ''
            else:
                # Por defecto ordenar por fecha (más reciente primero)
                key_func = lambda s: getattr(s, 'date', datetime.min)
                self.sort_ascending = False
            
            # Ordenar la lista de ventas con manejo de errores
            def safe_sort_key(sale):
                try:
                    return key_func(sale)
                except Exception:
                    # Valor por defecto según el tipo de columna
                    if self.sort_column_index == 0:  # ID
                        return 0
                    elif self.sort_column_index == 1:  # Fecha
                        return datetime.min
                    elif self.sort_column_index == 2:  # Cliente
                        return ""
                    elif self.sort_column_index == 3:  # Total
                        return 0
                    elif self.sort_column_index == 4:  # Estado
                        return ""
                    else:
                        return datetime.min
            
            self.filtered_sales.sort(key=safe_sort_key, reverse=not self.sort_ascending)
            
        except Exception as e:
            logging.error(f"Error al ordenar ventas: {str(e)}")
            # No mostrar mensajes de error al usuario para evitar interrupciones
    
    def filter_sales(self, e=None):
        """Filtra las ventas según el texto de búsqueda"""
        try:
            if not hasattr(self, 'search_field') or self.search_field is None:
                return
                
            if not hasattr(self, 'all_sales'):
                self.all_sales = []
                
            search_text = self.search_field.value.lower() if self.search_field.value else ""
            
            if not search_text:
                # Si no hay texto de búsqueda, mostrar todas las ventas
                self.filtered_sales = self.all_sales.copy()
            else:
                # Filtrar ventas que contengan el texto de búsqueda
                self.filtered_sales = []
                for sale in self.all_sales:
                    try:
                        sale_id_str = str(getattr(sale, 'id', '')).lower()
                        customer_name = getattr(getattr(sale, 'customer', None), 'name', '').lower() if getattr(sale, 'customer', None) else ''
                        status = getattr(sale, 'status', '').lower()
                        
                        if (search_text in sale_id_str) or (search_text in customer_name) or (search_text in status):
                            self.filtered_sales.append(sale)
                    except Exception as e:
                        logging.error(f"Error al filtrar venta individual: {str(e)}")
                        continue
            
            # Aplicar ordenamiento actual a las ventas filtradas
            self.sort_sales()
            
            # Volver a la primera página cuando se filtra
            self.current_page = 1
            
            # Actualizar tabla con ventas filtradas
            self.update_table_with_sales(self.get_current_page_sales())
            
            # Actualizar paginación
            self.update_pagination()
                
        except Exception as e:
            logging.error(f"Error al filtrar ventas: {str(e)}")
            # No mostrar mensajes de error al usuario
    
    def export_to_excel(self, e=None):
        """Exporta las ventas filtradas a un archivo Excel"""
        try:
            import pandas as pd
            import os
            from datetime import datetime
            
            # Crear lista de diccionarios con datos para el dataframe
            data = []
            for sale in self.filtered_sales:
                # Formatear fecha
                date_str = sale.date.strftime("%Y-%m-%d %H:%M") if sale.date else "N/A"
                
                # Obtener nombre del cliente
                customer_name = sale.customer.name if sale.customer else "Cliente no registrado"
                
                # Formatear estado
                status_text = "Completada" if sale.status == 'completed' else "Cancelada"
                
                # Crear diccionario para la venta
                sale_dict = {
                    'ID': sale.id,
                    'Fecha': date_str,
                    'Cliente': customer_name,
                    'Total': sale.total_amount,
                    'Estado': status_text,
                    'Método de Pago': sale.payment_method
                }
                
                # Si la venta tiene items, añadir como columnas adicionales
                if hasattr(sale, 'items') and sale.items:
                    product_names = []
                    for item in sale.items:
                        if item.product:
                            product_names.append(f"{item.quantity}x {item.product.name}")
                        else:
                            product_names.append(f"{item.quantity}x Producto eliminado")
                    
                    sale_dict['Productos'] = ", ".join(product_names)
                
                data.append(sale_dict)
            
            # Crear dataframe
            df = pd.DataFrame(data)
            
            # Generar nombre de archivo con fecha y hora
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ventas_export_{now}.xlsx"
            
            # Guardar dataframe a Excel
            df.to_excel(filename, index=False)
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Datos exportados a {filename}")
            
            # Abrir el archivo
            try:
                os.startfile(filename)
            except:
                pass
            
        except Exception as e:
            logging.error(f"Error al exportar a Excel: {str(e)}")
            show_error_message(self.page, f"Error al exportar a Excel: {str(e)}")
    
    def print_invoice(self, sale_id):
        """Imprime la factura de la venta"""
        try:
            # Aquí iría el código para generar e imprimir la factura
            # Por ahora, solo mostramos un mensaje
            show_success_message(self.page, f"Imprimiendo factura para la venta #{sale_id}")
        except Exception as e:
            logging.error(f"Error al imprimir factura: {str(e)}")
            show_error_message(self.page, f"Error al imprimir factura: {str(e)}")

    def refresh_data(self, e=None):
        """Recarga los datos de ventas"""
        try:
            # Reiniciar paginación
            self.current_page = 1
            
            # Cargar ventas recientes
            self.load_recent_sales()
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, "Datos actualizados correctamente")
        except Exception as e:
            logging.error(f"Error al actualizar datos: {str(e)}")
            show_error_message(self.page, f"Error al actualizar datos: {str(e)}")
    
    def create_view_sale_callback(self, sale_id):
        """Crea una función de callback para ver detalles de venta"""
        def handle_click(e):
            try:
                sale = self.sale_service.get_sale_by_id(sale_id)
                if sale:
                    self.view_sale_details(sale)
                else:
                    show_error_message(self.page, f"No se pudo encontrar la venta con ID {sale_id}")
            except Exception as e:
                logging.error(f"Error al obtener detalles de venta: {str(e)}")
                show_error_message(self.page, f"Error al obtener detalles: {str(e)}")
        return handle_click
    
    def view_sale_details(self, sale):
        """Muestra los detalles de una venta"""
        try:
            # Obtener detalles de la venta
            sale_items = self.sale_service.get_sale_items(sale.id)
            
            # Crear filas para la tabla de detalles
            items_rows = []
            for item in sale_items:
                # Obtener producto
                product = self.product_service.get_product_by_id(item.product_id)
                product_name = product.name if product else "Producto no encontrado"
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(product_name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(str(item.quantity), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.unit_price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.quantity * item.unit_price:.2f}", color=ft.colors.ON_SURFACE)),
                    ]
                )
                items_rows.append(row)
            
            # Crear tabla de detalles
            details_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Cantidad", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Precio", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Subtotal", color=ft.colors.ON_SURFACE)),
                ],
                rows=items_rows,
                border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            )
            
            # Crear diálogo de detalles
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles de Venta #{sale.id}", color=ft.colors.ON_SURFACE),
                content=ft.Column([
                    ft.Text(f"Fecha: {sale.date.strftime('%Y-%m-%d %H:%M')}", color=ft.colors.ON_SURFACE),
                    ft.Text(f"Cliente: {sale.customer.name if sale.customer else 'Cliente no registrado'}", color=ft.colors.ON_SURFACE),
                    ft.Container(height=10),
                    ft.Text("Productos:", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    details_table,
                    ft.Container(height=10),
                    ft.Text(f"Total: ${sale.total_amount:.2f}", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ], scroll=ft.ScrollMode.AUTO, height=400),
                actions=[
                    ft.TextButton("Cerrar", on_click=self.close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.colors.SURFACE
            )
            
            # Mostrar diálogo
            self.page.dialog.open = True
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al mostrar detalles de venta: {str(e)}")
            show_error_message(self.page, f"Error al mostrar detalles de venta: {str(e)}")
    
    def close_dialog(self, e):
        """Cierra el diálogo actual"""
        try:
            self.page.dialog.open = False
            self.page.update()
        except Exception as e:
            logging.error(f"Error al cerrar diálogo: {str(e)}")
            show_error_message(self.page, f"Error al cerrar diálogo: {str(e)}")

    def load_sales(self):
        """Carga automáticamente las ventas al inicializar la página"""
        try:
            logging.info("Cargando ventas automáticamente al iniciar...")
            # Utilizar el método refresh_data existente pero sin mostrar mensaje
            self.silent_refresh_data()
            logging.info(f"Ventas cargadas correctamente. Total: {len(self.all_sales)}")
            
            # Forzar actualización visual completa
            if hasattr(self, 'sales_table') and self.sales_table is not None:
                # Verificar que la tabla esté en el DOM
                if len(self.controls) > 0 and isinstance(self.controls[0], ft.Column):
                    logging.info("Forzando actualización visual de la tabla...")
                    # Actualizar el control principal
                    self.update()
                    # Forzar actualización de la página
                    if hasattr(self, 'page') and self.page is not None:
                        self.page.update()
            
        except Exception as e:
            logging.error(f"Error al cargar ventas automáticamente: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            
    def silent_refresh_data(self):
        """Recarga los datos de ventas sin mostrar mensajes de éxito"""
        try:
            logging.info("Iniciando actualización silenciosa de datos...")
            
            # Reiniciar paginación
            self.current_page = 1
            
            # Cargar ventas recientes
            self.load_recent_sales()
            
            # Forzar actualización visual de los componentes
            # Actualizar la tabla directamente
            if hasattr(self, 'sales_table') and self.sales_table is not None:
                current_sales = self.get_current_page_sales()
                logging.info(f"Actualizando tabla con {len(current_sales)} ventas en la página actual")
                self.update_table_with_sales(current_sales)
                
                # Verificar que la tabla esté en su contenedor
                if hasattr(self, 'table_container') and self.table_container is not None:
                    if hasattr(self.table_container, 'content'):
                        logging.info("Actualizando contenedor de tabla")
                        self.table_container.content = self.sales_table
                        self.table_container.update()
            
            # Actualizar información de paginación
            self.update_pagination()
            
            # Forzar actualización del componente completo
            self.update()
            
            # Forzar actualización de toda la página
            if hasattr(self, 'page') and self.page is not None:
                logging.info("Forzando actualización de la página completa")
                self.page.update()
            
            logging.info("Actualización silenciosa completada")
            # No mostrar mensaje de éxito en esta versión silenciosa
        except Exception as e:
            logging.error(f"Error al actualizar datos silenciosamente: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            # No mostrar mensaje de error tampoco
            
    def create_view_sale_callback(self, sale_id):
        """Crea una función de callback para ver detalles de venta"""
        def handle_click(e):
            try:
                sale = self.sale_service.get_sale_by_id(sale_id)
                if sale:
                    self.view_sale_details(sale)
                else:
                    show_error_message(self.page, f"No se pudo encontrar la venta con ID {sale_id}")
            except Exception as e:
                logging.error(f"Error al obtener detalles de venta: {str(e)}")
                show_error_message(self.page, f"Error al obtener detalles: {str(e)}")
        return handle_click
    
    def view_sale_details(self, sale):
        """Muestra los detalles de una venta"""
        try:
            # Obtener detalles de la venta
            sale_items = self.sale_service.get_sale_items(sale.id)
            
            # Crear filas para la tabla de detalles
            items_rows = []
            for item in sale_items:
                # Obtener producto
                product = self.product_service.get_product_by_id(item.product_id)
                product_name = product.name if product else "Producto no encontrado"
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(product_name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(str(item.quantity), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.unit_price:.2f}", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${item.quantity * item.unit_price:.2f}", color=ft.colors.ON_SURFACE)),
                    ]
                )
                items_rows.append(row)
            
            # Crear tabla de detalles
            details_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Cantidad", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Precio", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Subtotal", color=ft.colors.ON_SURFACE)),
                ],
                rows=items_rows,
                border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            )
            
            # Crear diálogo de detalles
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Detalles de Venta #{sale.id}", color=ft.colors.ON_SURFACE),
                content=ft.Column([
                    ft.Text(f"Fecha: {sale.date.strftime('%Y-%m-%d %H:%M')}", color=ft.colors.ON_SURFACE),
                    ft.Text(f"Cliente: {sale.customer.name if sale.customer else 'Cliente no registrado'}", color=ft.colors.ON_SURFACE),
                    ft.Container(height=10),
                    ft.Text("Productos:", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    details_table,
                    ft.Container(height=10),
                    ft.Text(f"Total: ${sale.total_amount:.2f}", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ], scroll=ft.ScrollMode.AUTO, height=400),
                actions=[
                    ft.TextButton("Cerrar", on_click=self.close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.colors.SURFACE
            )
            
            # Mostrar diálogo
            self.page.dialog.open = True
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al mostrar detalles de venta: {str(e)}")
            show_error_message(self.page, f"Error al mostrar detalles de venta: {str(e)}")
    
    def close_dialog(self, e):
        """Cierra el diálogo actual"""
        try:
            self.page.dialog.open = False
            self.page.update()
        except Exception as e:
            logging.error(f"Error al cerrar diálogo: {str(e)}")
            show_error_message(self.page, f"Error al cerrar diálogo: {str(e)}") 