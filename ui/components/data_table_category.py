import flet as ft
import logging

logger = logging.getLogger(__name__)

class DataTableCategory(ft.UserControl):
    def __init__(self, title: str, items: list, on_item_selected, on_add_item):
        super().__init__()
        self.title = title
        self.items = items
        self.on_item_selected = on_item_selected
        self.on_add_item = on_add_item
        self.selected_item = None
        self.build_ui()

    def build_ui(self):
        try:
            # Crear la tabla de datos
            self.data_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Estado")),
                ],
                rows=[],
                expand=True,
                divider_thickness=0.5,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
            )

            # Botón para agregar un nuevo ítem
            self.add_button = ft.FilledButton(
                "Nuevo",
                icon=ft.icons.ADD,
                on_click=self.on_add_item,
                width=200,
            )

            # Layout principal
            self.layout = ft.Column(
                controls=[
                    ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD),
                    self.data_table,
                    self.add_button,
                ],
                spacing=10,
                expand=True,
            )

        except Exception as e:
            logger.error(f"Error construyendo DataTableCategory: {str(e)}")
            raise

    def did_mount(self):
        # Actualizar la tabla después de que el control se haya agregado a la página
        self.update_table()

    def select_item(self, item):
        """Selecciona un ítem y actualiza la UI"""
        self.selected_item = item
        self.update_table()
        # Notificar al componente padre sobre la selección
        if item is not None:
            self.on_item_selected(item)

    def handle_row_select(self, e, item):
        # Manejar la selección de una fila
        if e.data == "true":  # Fila seleccionada
            self.select_item(item)
        else:
            # Si se deselecciona, no hacemos nada para mantener la selección
            # Para deseleccionar hay que elegir otro elemento
            pass

    def update_table(self):
        try:
            self.data_table.rows.clear()
            for item in self.items:
                status_icon = ft.Icon(
                    name=ft.icons.CHECK_CIRCLE if item.active else ft.icons.CANCEL,
                    color=ft.colors.GREEN if item.active else ft.colors.ERROR,
                    size=16,
                )
                
                # Verificar si este ítem está seleccionado
                is_selected = (self.selected_item and hasattr(self.selected_item, 'id') and 
                              hasattr(item, 'id') and self.selected_item.id == item.id)
                
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item.name, weight=ft.FontWeight.BOLD if is_selected else None)),
                        ft.DataCell(status_icon),
                    ],
                    selected=is_selected,
                    # bgcolor=ft.colors.with_opacity(0.1, ft.colors.PRIMARY) if is_selected else None,
                    on_select_changed=lambda e, i=item: self.handle_row_select(e, i),
                )
                self.data_table.rows.append(row)
            self.update()
        except Exception as e:
            logger.error(f"Error actualizando tabla: {str(e)}")
            raise

    def build(self):
        return self.layout