import flet as ft
from ui.components.alerts import show_error_message, show_success_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from services.supplierService import SupplierService
import logging

class PageSuppliers(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/ver_proveedores",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.supplier_service = SupplierService(session)
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(4, self.page)

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Gestión de Proveedores", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Crear tabla de proveedores
            self.suppliers_table = self.build_suppliers_table()
            
            # Cargar datos iniciales
            self.load_suppliers()

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ElevatedButton(
                                "Nuevo Proveedor",
                                icon=ft.icons.PERSON_ADD,
                                on_click=lambda _: self.page.go("/agregar_proveedor"),
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_PRIMARY,
                                    bgcolor=ft.colors.PRIMARY
                                )
                            ),
                            ft.ElevatedButton(
                                "Actualizar Datos",
                                icon=ft.icons.REFRESH,
                                on_click=self.load_suppliers,
                                style=ft.ButtonStyle(
                                    color=ft.colors.ON_SURFACE,
                                    bgcolor=ft.colors.SURFACE_VARIANT
                                )
                            )
                        ], spacing=10),
                        ft.Container(height=20),
                        ft.Text(
                            "Lista de Proveedores",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.ON_SURFACE
                        ),
                        self.suppliers_table
                    ]),
                    padding=20
                )
            ], spacing=0, scroll=ft.ScrollMode.AUTO)

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

    def build_suppliers_table(self):
        try:
            # Crear tabla de proveedores
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Nombre", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Contacto", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Teléfono", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Email", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Dirección", color=ft.colors.ON_SURFACE)),
                    ft.DataColumn(ft.Text("Estado", color=ft.colors.ON_SURFACE)),
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
        except Exception as e:
            logging.error(f"Error construyendo tabla de proveedores: {str(e)}")
            return ft.Text("Error al cargar la tabla de proveedores", color=ft.colors.ERROR)
            
    def load_suppliers(self, e=None):
        """Carga los proveedores en la tabla"""
        try:
            # Obtener todos los proveedores
            suppliers = self.supplier_service.get_all_suppliers()
            
            # Crear filas para la tabla
            rows = []
            for supplier in suppliers:
                # Formatear estado
                status_color = ft.colors.GREEN if supplier.active else ft.colors.ERROR
                status_text = "Activo" if supplier.active else "Inactivo"
                
                # Crear fila
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(supplier.id), color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.name, color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.contact_name or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.phone or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.email or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(supplier.address or "N/A", color=ft.colors.ON_SURFACE)),
                        ft.DataCell(ft.Text(status_text, color=status_color)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.PRIMARY,
                                    tooltip="Editar",
                                    on_click=lambda _, s=supplier: self.edit_supplier(s)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.ERROR,
                                    tooltip="Eliminar",
                                    on_click=lambda _, s=supplier: self.delete_supplier(s)
                                )
                            ])
                        ),
                    ]
                )
                rows.append(row)
            
            # Actualizar tabla
            self.suppliers_table.rows = rows
            
            # Mostrar mensaje si no hay resultados
            if not rows:
                show_error_message(self.page, "No se encontraron proveedores")
            
            self.update()
            
        except Exception as e:
            logging.error(f"Error al cargar proveedores: {str(e)}")
            show_error_message(self.page, f"Error al cargar proveedores: {str(e)}")
            
    def edit_supplier(self, supplier):
        """Navega a la página de edición de proveedor"""
        # Aquí podrías implementar la navegación a la página de edición
        show_success_message(self.page, f"Editar proveedor {supplier.name}")
        
    def delete_supplier(self, supplier):
        """Elimina un proveedor"""
        try:
            # Confirmar eliminación
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"¿Eliminar proveedor {supplier.name}?"),
                content=ft.Text("Esta acción no se puede deshacer."),
                actions=[
                    ft.TextButton("Cancelar", on_click=self.close_dialog),
                    ft.TextButton("Eliminar", on_click=lambda _: self.confirm_delete_supplier(supplier)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logging.error(f"Error al eliminar proveedor: {str(e)}")
            show_error_message(self.page, f"Error al eliminar proveedor: {str(e)}")
            
    def confirm_delete_supplier(self, supplier):
        """Confirma la eliminación de un proveedor"""
        try:
            # Eliminar proveedor
            self.supplier_service.delete_supplier(supplier.id)
            
            # Cerrar diálogo
            self.close_dialog()
            
            # Recargar proveedores
            self.load_suppliers()
            
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Proveedor {supplier.name} eliminado correctamente")
        except Exception as e:
            logging.error(f"Error al eliminar proveedor: {str(e)}")
            show_error_message(self.page, f"Error al eliminar proveedor: {str(e)}")
            
    def close_dialog(self, e=None):
        """Cierra el diálogo actual"""
        self.page.dialog.open = False
        self.page.update() 