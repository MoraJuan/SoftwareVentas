"""
Componente de tabla de datos reutilizable
"""
import flet as ft
from typing import List, Dict

class DataTable(ft.UserControl):
    def __init__(
        self,
        columns: List[str],
        data: List[Dict],
        on_select=None,
        on_delete=None
    ):
        super().__init__()
        self.columns = columns
        self.data = data
        self.on_select = on_select
        self.on_delete = on_delete

    def build(self):
        # Crear las columnas de la tabla
        table_columns = [
            ft.DataColumn(ft.Text(column))
            for column in self.columns
        ]

        # Crear las filas de la tabla
        table_rows = []
        for row in self.data:
            cells = [
                ft.DataCell(ft.Text(str(row.get(column, ""))))
                for column in self.columns
            ]
            
            # Añadir botones de acción si se proporcionaron callbacks
            if self.on_select or self.on_delete:
                action_cell = ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            ft.icons.EDIT,
                            on_click=lambda x, r=row: self.on_select(r)
                        ) if self.on_select else None,
                        ft.IconButton(
                            ft.icons.DELETE,
                            on_click=lambda x, r=row: self.on_delete(r)
                        ) if self.on_delete else None,
                    ])
                )
                cells.append(action_cell)

            table_rows.append(ft.DataRow(cells=cells))

        return ft.DataTable(
            columns=table_columns,
            rows=table_rows,
        )