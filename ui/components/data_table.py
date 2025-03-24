import flet as ft
from typing import List, Dict, Callable, Any
import logging

class DataTable(ft.UserControl):
    def __init__(
        self,
        columns: List[str],
        data: List[Dict],
        items_per_page: int = 10,
        on_select: Callable[[Dict], None] = None,
        on_delete: Callable[[Dict], None] = None
    ):
        super().__init__()
        self.columns = columns
        self.full_data = data  # Todos los datos
        self.current_data = data  # Datos visibles en la página actual
        self.on_select = on_select
        self.on_delete = on_delete
        self.sort_column_index = None
        self.sort_ascending = True
        self.current_page = 1
        self.items_per_page = items_per_page
        self.table = None
        self.pagination_controls = None

    def build(self):
        # Crear columnas con soporte para ordenamiento
        table_columns = [
            ft.DataColumn(
                ft.Row([
                    ft.Text(column),
                    ft.Icon(
                        name=ft.icons.ARROW_UPWARD if self.sort_column_index == i and self.sort_ascending else
                             ft.icons.ARROW_DOWNWARD if self.sort_column_index == i and not self.sort_ascending else None,
                        size=16,
                        color=ft.colors.PRIMARY if self.sort_column_index == i else ft.colors.TRANSPARENT
                    )
                ], spacing=5),
                on_sort=lambda e, idx=i: self.sort_table(idx)
            ) for i, column in enumerate(self.columns)
        ]

        # Construir filas iniciales
        self.table = ft.DataTable(
            columns=table_columns,
            rows=self.build_rows(self.get_current_page_data()),
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
            heading_row_height=50,
            data_row_min_height=50,
            column_spacing=10,
            heading_row_color=ft.colors.with_opacity(0.05, ft.colors.PRIMARY),
            sort_column_index=self.sort_column_index,
            sort_ascending=self.sort_ascending
        )

        # Controles de paginación
        total_pages = self.get_total_pages()
        self.page_info = ft.Text(f"Página {self.current_page} de {total_pages}")
        self.pagination_controls = ft.Row([
            ft.IconButton(
                icon=ft.icons.FIRST_PAGE,
                on_click=self.go_to_first_page,
                disabled=self.current_page == 1,
                icon_color=ft.colors.PRIMARY
            ),
            ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=self.go_to_prev_page,
                disabled=self.current_page == 1,
                icon_color=ft.colors.PRIMARY
            ),
            self.page_info,
            ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                on_click=self.go_to_next_page,
                disabled=self.current_page == total_pages,
                icon_color=ft.colors.PRIMARY
            ),
            ft.IconButton(
                icon=ft.icons.LAST_PAGE,
                on_click=self.go_to_last_page,
                disabled=self.current_page == total_pages,
                icon_color=ft.colors.PRIMARY
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            self.table,
            self.pagination_controls
        ], spacing=10)

    def build_rows(self, data: List[Dict]) -> List[ft.DataRow]:
        rows = []
        for i, row in enumerate(data):
            try:
                # Crear una celda para cada columna
                cells = []
                for col in self.columns:
                    if col == "Acciones":
                        # Columna especial para acciones
                        if self.on_select or self.on_delete:
                            # Creamos los manejadores de eventos como funciones de clase
                            action_buttons = []
                            
                            # Botón de editar
                            if self.on_select:
                                edit_btn = ft.IconButton(
                                    ft.icons.EDIT,
                                    tooltip="Editar",
                                    icon_color=ft.colors.PRIMARY,
                                    data=i,  # Guardamos el índice de la fila
                                    on_click=lambda e: self._handle_edit_click(e)
                                )
                                action_buttons.append(edit_btn)
                            
                            # Botón de eliminar
                            if self.on_delete:
                                delete_btn = ft.IconButton(
                                    ft.icons.DELETE,
                                    tooltip="Eliminar",
                                    icon_color=ft.colors.ERROR,
                                    data=i,  # Guardamos el índice de la fila
                                    on_click=lambda e: self._handle_delete_click(e)
                                )
                                action_buttons.append(delete_btn)
                            
                            action_cell = ft.DataCell(
                                ft.Row(action_buttons, spacing=5)
                            )
                            cells.append(action_cell)
                        else:
                            # Si no hay acciones, aún necesitamos agregar una celda vacía
                            cells.append(ft.DataCell(ft.Text("")))
                    else:
                        # Columna normal con datos
                        cells.append(ft.DataCell(ft.Text(str(row.get(col, "")))))
                
                # Asegurarse de que el número de celdas sea igual al número de columnas
                if len(cells) != len(self.columns):
                    logging.warning(f"Número incorrecto de celdas ({len(cells)}) para las columnas ({len(self.columns)}). Ajustando...")
                    # Rellenar con celdas vacías si faltan
                    while len(cells) < len(self.columns):
                        cells.append(ft.DataCell(ft.Text("")))
                    # Truncar si hay demasiadas
                    cells = cells[:len(self.columns)]
                
                # Crear la fila y guardar los datos originales de la fila como atributo
                data_row = ft.DataRow(cells=cells)
                data_row.data = row  # Guardamos los datos originales en la fila
                rows.append(data_row)
            except Exception as e:
                logging.error(f"Error al construir fila de datos: {str(e)}")
                # Continuar con la siguiente fila
                continue
                
        return rows
    
    def _handle_edit_click(self, e):
        """Manejador para el botón de editar"""
        try:
            row_index = e.control.data  # Obtenemos el índice de la fila desde el botón
            current_data = self.get_current_page_data()
            if 0 <= row_index < len(current_data):
                row_data = current_data[row_index]
                if self.on_select:
                    logging.info(f"Editando fila: {row_data}")
                    self.on_select(row_data)
        except Exception as e:
            logging.error(f"Error al manejar clic de edición: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
    
    def _handle_delete_click(self, e):
        """Manejador para el botón de eliminar"""
        try:
            row_index = e.control.data  # Obtenemos el índice de la fila desde el botón
            current_data = self.get_current_page_data()
            if 0 <= row_index < len(current_data):
                row_data = current_data[row_index]
                if self.on_delete:
                    logging.info(f"Eliminando fila: {row_data}")
                    self.on_delete(row_data)
        except Exception as e:
            logging.error(f"Error al manejar clic de eliminación: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())

    def sort_table(self, column_index: int):
        if self.sort_column_index == column_index:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column_index = column_index
            self.sort_ascending = True

        key_func = lambda x: str(x.get(self.columns[column_index], "")).lower()
        self.full_data.sort(key=key_func, reverse=not self.sort_ascending)
        self.current_page = 1  # Resetear a la primera página al ordenar
        self.update_table()

    def get_total_pages(self) -> int:
        return max(1, (len(self.full_data) + self.items_per_page - 1) // self.items_per_page)

    def get_current_page_data(self) -> List[Dict]:
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.full_data[start:end]

    def update_table(self):
        self.table.rows = self.build_rows(self.get_current_page_data())
        total_pages = self.get_total_pages()
        self.page_info.value = f"Página {self.current_page} de {total_pages}"
        self.update_pagination_buttons(total_pages)
        self.update()

    def go_to_page(self, page_number: int):
        total_pages = self.get_total_pages()
        self.current_page = max(1, min(page_number, total_pages))
        self.update_table()

    def go_to_first_page(self, e): self.go_to_page(1)
    def go_to_prev_page(self, e): self.go_to_page(self.current_page - 1)
    def go_to_next_page(self, e): self.go_to_page(self.current_page + 1)
    def go_to_last_page(self, e): self.go_to_page(self.get_total_pages())

    def update_pagination_buttons(self, total_pages: int):
        for control in self.pagination_controls.controls:
            if isinstance(control, ft.IconButton):
                if control.icon in [ft.icons.FIRST_PAGE, ft.icons.ARROW_BACK]:
                    control.disabled = self.current_page == 1
                elif control.icon in [ft.icons.ARROW_FORWARD, ft.icons.LAST_PAGE]:
                    control.disabled = self.current_page == total_pages
        self.update()

    def set_data(self, new_data: List[Dict]):
        """Método para actualizar los datos de la tabla"""
        self.full_data = new_data
        self.current_page = 1
        self.update_table()