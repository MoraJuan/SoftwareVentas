import flet as ft
from typing import List, Dict, Callable, Any

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
        for row in data:
            cells = [
                ft.DataCell(ft.Text(str(row.get(col, ""))))
                for col in self.columns[:-1] if col != "Acciones"  # Excluir columna de acciones
            ]
            if self.on_select or self.on_delete:
                action_cell = ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            ft.icons.EDIT,
                            on_click=lambda e, r=row: self.on_select(r) if self.on_select else None,
                            icon_color=ft.colors.PRIMARY
                        ) if self.on_select else None,
                        ft.IconButton(
                            ft.icons.DELETE,
                            on_click=lambda e, r=row: self.on_delete(r) if self.on_delete else None,
                            icon_color=ft.colors.ERROR
                        ) if self.on_delete else None,
                    ], spacing=5)
                )
                cells.append(action_cell)
            rows.append(ft.DataRow(cells=cells))
        return rows

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