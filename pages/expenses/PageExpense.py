import flet as ft
from services.expenseService import ExpenseService
from services.supplierService import SupplierService
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from datetime import datetime
import logging

class PageExpense(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/ver_reportes/gastos",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.expense_service = ExpenseService(session)
        self.supplier_service = SupplierService(session)
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(3, self.page)  # Índice 3 para Reportes

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=ft.colors.ON_SURFACE,
                            tooltip="Volver a Reportes",
                            on_click=lambda _: self.page.go("/ver_reportes")
                        ),
                        ft.Text(
                            "Gestión de Gastos", 
                            size=24, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                    ]),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Formulario para agregar gastos
            self.expense_form = self.build_expense_form()

            # Tabla de gastos
            self.expense_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Fecha", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Descripción", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Categoría", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Proveedor", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Monto", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Acciones", color=ft.colors.ON_SURFACE)),
                ],
                rows=[],
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT),
                sort_column_index=0,
                sort_ascending=False,
            )

            # Cargar datos iniciales
            self.load_expenses()

            # Layout principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                self.expense_form,
                ft.Container(height=20),  # Espacio
                ft.Text(
                    "Gastos Registrados", 
                    size=18, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                self.expense_table,
            ], spacing=10, scroll=ft.ScrollMode.AUTO)

            # Contenedor principal
            self.controls = [
                ft.Container(
                    content=ft.Row([
                        self.navigation_rail,
                        ft.VerticalDivider(width=1, color=ft.colors.OUTLINE_VARIANT),
                        ft.Container(
                            padding=20,
                            content=main_content,
                            expand=True
                        )
                    ]),
                    expand=True
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI: {str(e)}")
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def build_expense_form(self):
        # Campos del formulario
        self.amount_input = ft.TextField(
            label="Monto",
            width=200,
            prefix_text="$",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Ingrese el monto",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )

        self.description_input = ft.TextField(
            label="Descripción",
            width=400,
            multiline=True,
            min_lines=2,
            max_lines=3,
            hint_text="Describa el gasto",
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )

        self.category_dropdown = ft.Dropdown(
            label="Categoría",
            width=200,
            options=[
                ft.dropdown.Option("compra_inventario", "Compra de Inventario"),
                ft.dropdown.Option("operativo", "Gastos Operativos"),
                ft.dropdown.Option("salarios", "Salarios"),
                ft.dropdown.Option("servicios", "Servicios"),
                ft.dropdown.Option("otros", "Otros Gastos"),
            ],
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )

        self.supplier_dropdown = ft.Dropdown(
            label="Proveedor (opcional)",
            width=300,
            options=self.get_supplier_options(),
            label_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            text_style=ft.TextStyle(color=ft.colors.ON_SURFACE),
            border_color=ft.colors.OUTLINE
        )

        # Botón para agregar
        self.add_button = ft.ElevatedButton(
            "Registrar Gasto",
            icon=ft.icons.ADD,
            on_click=self.add_expense,
            style=ft.ButtonStyle(
                color=ft.colors.ON_PRIMARY,
                bgcolor=ft.colors.PRIMARY
            )
        )

        # Contenedor del formulario
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Registrar Nuevo Gasto", 
                    size=18, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE
                ),
                ft.Row([
                    self.amount_input,
                    self.category_dropdown,
                    self.supplier_dropdown
                ], wrap=True, spacing=10),
                self.description_input,
                self.add_button
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10
        )

    def get_supplier_options(self):
        try:
            suppliers = self.supplier_service.get_all_suppliers()
            options = [ft.dropdown.Option("", "-- Seleccione un proveedor --")]
            options.extend([ft.dropdown.Option(str(s.id), s.name) for s in suppliers])
            return options
        except Exception as e:
            logging.error(f"Error al obtener proveedores: {str(e)}")
            return [ft.dropdown.Option("", "Error al cargar proveedores")]

    def add_expense(self, e):
        try:
            # Validar campos
            if not self.amount_input.value:
                show_error_message(self.page, "Debe ingresar un monto")
                return
                
            if not self.description_input.value:
                show_error_message(self.page, "Debe ingresar una descripción")
                return
                
            if not self.category_dropdown.value:
                show_error_message(self.page, "Debe seleccionar una categoría")
                return
                
            # Preparar datos
            expense_data = {
                "amount": float(self.amount_input.value),
                "description": self.description_input.value,
                "category": self.category_dropdown.value,
                "supplier_id": int(self.supplier_dropdown.value) if self.supplier_dropdown.value else None
            }
            
            # Crear gasto
            expense = self.expense_service.create_expense(expense_data)
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, "Gasto registrado correctamente")
            
            # Limpiar formulario
            self.amount_input.value = ""
            self.description_input.value = ""
            self.category_dropdown.value = None
            self.supplier_dropdown.value = None
            self.update()
            
            # Recargar tabla
            self.load_expenses()
            
        except Exception as e:
            logging.error(f"Error al agregar gasto: {str(e)}")
            show_error_message(self.page, f"Error al agregar gasto: {str(e)}")

    def load_expenses(self):
        try:
            # Obtener gastos
            expenses = self.expense_service.get_all_expenses()
            
            # Crear filas para la tabla
            rows = []
            for expense in expenses:
                # Obtener nombre del proveedor si existe
                supplier_name = expense.supplier.name if expense.supplier else "N/A"
                
                # Nombres legibles para las categorías
                category_names = {
                    "compra_inventario": "Compra de Inventario",
                    "operativo": "Gastos Operativos",
                    "salarios": "Salarios",
                    "servicios": "Servicios",
                    "otros": "Otros Gastos"
                }
                
                category_display = category_names.get(expense.category, expense.category)
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(expense.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(expense.date.strftime("%Y-%m-%d"), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(expense.description, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(category_display, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier_name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(f"${expense.amount:.2f}", color=ft.colors.ERROR)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.ERROR,
                                    tooltip="Eliminar",
                                    on_click=lambda e, id=expense.id: self.delete_expense(id)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.expense_table.rows = rows
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar gastos: {str(e)}")
            show_error_message(self.page, f"Error al cargar gastos: {str(e)}")

    def delete_expense(self, expense_id):
        try:
            # Confirmar eliminación
            def confirm_delete(e):
                try:
                    # Eliminar gasto
                    self.expense_service.delete_expense(expense_id)
                    
                    # Cerrar diálogo
                    self.page.dialog.open = False
                    self.page.update()
                    
                    # Mostrar mensaje de éxito
                    show_success_message(self.page, "Gasto eliminado correctamente")
                    
                    # Recargar tabla
                    self.load_expenses()
                    
                except Exception as e:
                    logging.error(f"Error al eliminar gasto: {str(e)}")
                    show_error_message(self.page, f"Error al eliminar gasto: {str(e)}")
            
            # Cancelar eliminación
            def cancel_delete(e):
                self.page.dialog.open = False
                self.page.update()
            
            # Mostrar diálogo de confirmación
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Confirmar eliminación", color=ft.colors.ON_SURFACE),
                content=ft.Text("¿Está seguro de que desea eliminar este gasto?", color=ft.colors.ON_SURFACE),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancel_delete),
                    ft.ElevatedButton(
                        "Eliminar",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color=ft.colors.ON_ERROR, bgcolor=ft.colors.ERROR)
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=ft.colors.SURFACE
            )
            self.page.dialog.open = True
            self.page.update()
            
        except Exception as e:
            logging.error(f"Error al eliminar gasto: {str(e)}")
            show_error_message(self.page, f"Error al eliminar gasto: {str(e)}") 