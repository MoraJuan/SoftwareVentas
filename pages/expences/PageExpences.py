import flet as ft
from services.expenseService import ExpenseService  # Asumimos este servicio
from ui.components.data_table import DataTable
from ui.components.alerts import show_error_message, show_success_message
import logging

class PageExpense(ft.UserControl):
    def __init__(self, page: ft.Page, session, go_back_callback):
        super().__init__()
        self.page = page
        self.session = session
        self.go_back_callback = go_back_callback
        self.expense_service = ExpenseService(session)
        self.is_mobile = self.page.width < 600
        self.all_expenses = []
        self.table = None
        self.table_container = None
        self.search_field = None
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            self.load_expenses()

            self.search_field = ft.TextField(
                label="Buscar gastos",
                prefix_icon=ft.icons.SEARCH,
                width=min(self.page.width * 0.8, 500) if self.is_mobile else 500,
                border_radius=20,
                on_change=self.filter_expenses,
                hint_text="Ingrese la descripción del gasto...",
                height=50
            )

            expense_actions = ft.Row([
                ft.FilledButton(
                    text="Agregar/Editar",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self.page.go("/agregar_gasto")
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    tooltip="Volver a Reportes",
                    on_click=lambda _: self.go_back_callback(),
                    icon_color=ft.colors.PRIMARY
                )
            ], wrap=True, spacing=10)

            table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            expense_data = self.get_expense_data()
            self.table = DataTable(
                columns=["ID", "Descripción", "Monto", "Fecha", "Acciones"],
                data=expense_data,
                items_per_page=10,
                on_select=self.edit_expense,
                on_delete=self.delete_expense
            )
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

            content_column = ft.Column(
                [
                    ft.Text("Gastos", size=20 if self.is_mobile else 24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.Text("Gestión de gastos", size=14 if self.is_mobile else 16, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Container(height=10),
                    expense_actions,
                    ft.Row([
                        self.search_field,
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            on_click=self.load_expenses,
                            icon_color=ft.colors.PRIMARY
                        )
                    ]),
                    ft.Container(height=10),
                    self.table_wrapper,
                    ft.Text(f"Total: {len(self.all_expenses)} gastos", size=12, text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )

            self.controls = [
                ft.Container(
                    content=content_column,
                    padding=10 if self.is_mobile else 20
                )
            ]

        except Exception as e:
            logging.error(f"Error construyendo UI de gastos: {str(e)}")
            self.controls = [ft.Text(f"Error al cargar los gastos: {str(e)}", color=ft.colors.ERROR)]

    def load_expenses(self, e=None):
        try:
            logging.info("Iniciando carga de gastos")
            self.all_expenses = self.expense_service.get_all_expenses()
            logging.info(f"Gastos cargados: {len(self.all_expenses)}")
            if self.table:
                self.table.set_data(self.get_expense_data())
                logging.info("Datos establecidos en la tabla")
            self.update()
        except Exception as e:
            logging.error(f"Error al cargar gastos: {str(e)}")
            show_error_message(self.page, f"Error al cargar gastos: {str(e)}")

    def filter_expenses(self, e):
        search_text = self.search_field.value.lower()
        filtered = [
            e for e in self.all_expenses
            if search_text in e.description.lower()
        ] if search_text else self.all_expenses.copy()
        self.table.set_data([
            {
                "ID": str(e.id),
                "Descripción": e.description,
                "Monto": f"${e.amount:.2f}",
                "Fecha": e.date.strftime("%Y-%m-%d") if e.date else "N/A",
                "expense": e
            } for e in filtered
        ])

    def get_expense_data(self):
        return [
            {
                "ID": str(e.id),
                "Descripción": e.description,
                "Monto": f"${e.amount:.2f}",
                "Fecha": e.date.strftime("%Y-%m-%d") if e.date else "N/A",
                "expense": e
            } for e in self.all_expenses
        ]

    def edit_expense(self, row_data):
        expense = row_data["expense"]
        self.page.client_storage.set("edit_expense_id", expense.id)
        self.page.go("/editar_gasto")

    def delete_expense(self, row_data):
        expense = row_data["expense"]
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"¿Eliminar gasto {expense.description}?"),
            content=ft.Text("Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_expense(expense))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def confirm_delete_expense(self, expense):
        self.expense_service.delete_expense(expense.id)
        self.close_dialog()
        self.load_expenses()
        show_success_message(self.page, f"Gasto {expense.description} eliminado correctamente")

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.update()
        elif self.table_container:
            new_table_width = min(self.page.width * 0.95, 1000) if self.is_mobile else min(self.page.width * 0.8, 1200)
            self.table_container.width = new_table_width
            self.table_container.scroll = ft.ScrollMode.AUTO if self.is_mobile else ft.ScrollMode.MULTILINE if self.is_mobile else None
            self.search_field.width = min(self.page.width * 0.8, 500) if self.is_mobile else 500
            self.update()

    def build(self):
        return ft.Column(self.controls, expand=True)