import flet as ft
from sqlalchemy.orm import Session
from services.categoryService import CategoryService
from ui.components.alerts import show_success_message, show_error_message
from ui.components.navigation import create_navigation_rail, ThemeIconButton
import logging

logger = logging.getLogger(__name__)

class PageCategory(ft.View):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__(
            route="/categorias",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.category_service = CategoryService(session)
        self.categories = []
        self.selected_category = None
        self.build_ui()

    def build_ui(self):
        try:
            # Crear navegación
            self.navigation_rail = create_navigation_rail(2, self.page)  # 2 para Inventario

            # Crear botón de tema
            self.theme_button = ThemeIconButton(self.page)

            # Título principal con botón de tema
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Gestión de Categorías", 
                        size=24, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.Container(expand=True),
                    self.theme_button
                ]),
                padding=ft.padding.only(right=20, bottom=20)
            )

            # Panel izquierdo - Lista de categorías
            self.categories_list = ft.ListView(
                expand=1,
                spacing=10,
                padding=10,
                auto_scroll=True
            )

            # Botón para agregar nueva categoría
            self.add_category_button = ft.FilledButton(
                "Nueva Categoría",
                icon=ft.icons.ADD,
                on_click=self.show_add_category_dialog
            )

            # Panel izquierdo completo
            left_panel = ft.Container(
                content=ft.Column([
                    ft.Text("Categorías disponibles", size=16, weight=ft.FontWeight.BOLD),
                    self.categories_list,
                    self.add_category_button
                ]),
                width=300,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                padding=20
            )

            # Panel derecho - Detalles de la categoría
            self.category_name = ft.TextField(
                label="Nombre de la categoría",
                width=300,
                disabled=True
            )
            
            self.category_description = ft.TextField(
                label="Descripción",
                width=300,
                multiline=True,
                min_lines=3,
                max_lines=5,
                disabled=True
            )
            
            self.category_status = ft.Checkbox(
                label="Categoría activa",
                disabled=True
            )
            
            # Botones de acción
            self.save_button = ft.FilledButton(
                "Guardar cambios",
                icon=ft.icons.SAVE,
                on_click=self.save_category,
                disabled=True
            )
            
            self.cancel_button = ft.OutlinedButton(
                "Cancelar",
                icon=ft.icons.CANCEL,
                on_click=self.cancel_edit,
                disabled=True
            )
            
            self.delete_button = ft.FilledTonalButton(
                "Eliminar",
                icon=ft.icons.DELETE,
                on_click=self.confirm_delete_category,
                disabled=True,
                color=ft.colors.ERROR
            )
            
            # Panel derecho completo
            right_panel = ft.Container(
                content=ft.Column([
                    ft.Text("Detalles de la categoría", size=16, weight=ft.FontWeight.BOLD),
                    self.category_name,
                    self.category_description,
                    self.category_status,
                    ft.Row([
                        self.save_button,
                        self.cancel_button,
                        self.delete_button
                    ], spacing=10)
                ], spacing=20),
                expand=True,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                padding=20
            )

            # Botón para volver a inventario
            back_button = ft.ElevatedButton(
                "Volver a Inventario",
                icon=ft.icons.ARROW_BACK,
                on_click=lambda _: self.page.go("/ver_inventario")
            )

            # Contenido principal
            main_content = ft.Column([
                header,
                ft.Row([
                    back_button
                ], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                ft.Row([
                    left_panel,
                    right_panel
                ], expand=True, spacing=20)
            ], spacing=20)

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

            # Cargar categorías
            self.load_categories()

        except Exception as e:
            logger.error(f"Error construyendo UI: {str(e)}")
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def load_categories(self):
        """Carga la lista de categorías"""
        try:
            self.categories = self.category_service.get_all_categories()
            self.update_categories_list()
        except Exception as e:
            logger.error(f"Error al cargar categorías: {str(e)}")
            show_error_message(self.page, f"Error al cargar categorías: {str(e)}")

    def update_categories_list(self):
        """Actualiza la lista visual de categorías"""
        try:
            self.categories_list.controls.clear()
            
            for category in self.categories:
                # Crear un indicador de estado
                status_icon = ft.Icon(
                    name=ft.icons.CHECK_CIRCLE if category.active else ft.icons.CANCEL,
                    color=ft.colors.GREEN if category.active else ft.colors.ERROR,
                    size=16
                )
                
                # Crear elemento de lista para la categoría
                item = ft.Container(
                    content=ft.Row([
                        ft.Text(category.name, expand=1),
                        status_icon
                    ]),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.PRIMARY) if self.selected_category and self.selected_category.id == category.id else None,
                    on_click=lambda _, c=category: self.select_category(c)
                )
                
                self.categories_list.controls.append(item)
            
            self.update()
        except Exception as e:
            logger.error(f"Error al actualizar lista de categorías: {str(e)}")
            show_error_message(self.page, f"Error al actualizar lista: {str(e)}")

    def select_category(self, category):
        """Selecciona una categoría para edición"""
        try:
            self.selected_category = category
            
            # Actualizar campos de formulario
            self.category_name.value = category.name
            self.category_description.value = category.description or ""
            self.category_status.value = category.active
            
            # Habilitar campos y botones
            self.category_name.disabled = False
            self.category_description.disabled = False
            self.category_status.disabled = False
            self.save_button.disabled = False
            self.cancel_button.disabled = False
            self.delete_button.disabled = False
            
            # Actualizar UI
            self.update_categories_list()
            self.update()
        except Exception as e:
            logger.error(f"Error al seleccionar categoría: {str(e)}")
            show_error_message(self.page, f"Error al seleccionar categoría: {str(e)}")

    def save_category(self, e):
        """Guarda los cambios en la categoría seleccionada"""
        try:
            if not self.selected_category:
                show_error_message(self.page, "No hay categoría seleccionada")
                return
                
            # Validar nombre
            if not self.category_name.value:
                show_error_message(self.page, "El nombre de la categoría es obligatorio")
                return
                
            # Preparar datos
            category_data = {
                "name": self.category_name.value,
                "description": self.category_description.value,
                "active": self.category_status.value
            }
            
            # Actualizar categoría
            updated_category = self.category_service.update_category(
                self.selected_category.id,
                category_data
            )
            
            if not updated_category:
                show_error_message(self.page, "No se pudo actualizar la categoría. El nombre podría estar duplicado.")
                return
                
            # Mostrar mensaje de éxito
            show_success_message(self.page, f"Categoría '{updated_category.name}' actualizada correctamente")
            
            # Recargar categorías
            self.load_categories()
            
            # Seleccionar la categoría actualizada
            for category in self.categories:
                if category.id == updated_category.id:
                    self.select_category(category)
                    break
                    
        except Exception as e:
            logger.error(f"Error al guardar categoría: {str(e)}")
            show_error_message(self.page, f"Error al guardar categoría: {str(e)}")

    def cancel_edit(self, e):
        """Cancela la edición de la categoría"""
        try:
            if self.selected_category:
                # Restablecer campos al valor original
                category = self.category_service.get_category_by_id(self.selected_category.id)
                if category:
                    self.category_name.value = category.name
                    self.category_description.value = category.description or ""
                    self.category_status.value = category.active
                    self.update()
                    show_success_message(self.page, "Cambios descartados")
                else:
                    self.clear_form()
            else:
                self.clear_form()
        except Exception as e:
            logger.error(f"Error al cancelar edición: {str(e)}")
            show_error_message(self.page, f"Error al cancelar edición: {str(e)}")

    def clear_form(self):
        """Limpia el formulario de edición"""
        try:
            self.selected_category = None
            
            # Limpiar campos
            self.category_name.value = ""
            self.category_description.value = ""
            self.category_status.value = True
            
            # Deshabilitar campos y botones
            self.category_name.disabled = True
            self.category_description.disabled = True
            self.category_status.disabled = True
            self.save_button.disabled = True
            self.cancel_button.disabled = True
            self.delete_button.disabled = True
            
            # Actualizar UI
            self.update_categories_list()
            self.update()
        except Exception as e:
            logger.error(f"Error al limpiar formulario: {str(e)}")
            show_error_message(self.page, f"Error al limpiar formulario: {str(e)}")

    def confirm_delete_category(self, e):
        """Muestra diálogo de confirmación para eliminar una categoría"""
        try:
            if not self.selected_category:
                show_error_message(self.page, "No hay categoría seleccionada")
                return
                
            # Mostrar diálogo de confirmación
            self.page.dialog = ft.AlertDialog(
                title=ft.Text(f"Eliminar categoría '{self.selected_category.name}'"),
                content=ft.Text("¿Está seguro de que desea eliminar esta categoría? Esta acción no se puede deshacer."),
                actions=[
                    ft.TextButton("Cancelar", on_click=self.close_dialog),
                    ft.TextButton("Eliminar", on_click=self.delete_category)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Error al mostrar diálogo de confirmación: {str(e)}")
            show_error_message(self.page, f"Error al mostrar diálogo: {str(e)}")

    def delete_category(self, e):
        """Elimina la categoría seleccionada"""
        try:
            if not self.selected_category:
                show_error_message(self.page, "No hay categoría seleccionada")
                return
                
            # Eliminar categoría
            success = self.category_service.delete_category(self.selected_category.id)
            
            # Cerrar diálogo
            self.close_dialog()
            
            if success:
                show_success_message(self.page, f"Categoría '{self.selected_category.name}' eliminada correctamente")
                # Limpiar formulario
                self.clear_form()
                # Recargar categorías
                self.load_categories()
            else:
                show_error_message(self.page, "No se pudo eliminar la categoría")
        except Exception as e:
            logger.error(f"Error al eliminar categoría: {str(e)}")
            show_error_message(self.page, f"Error al eliminar categoría: {str(e)}")

    def close_dialog(self, e=None):
        """Cierra el diálogo actual"""
        self.page.dialog.open = False
        self.page.update()

    def show_add_category_dialog(self, e):
        """Muestra el diálogo para agregar una nueva categoría"""
        try:
            # Campos para la nueva categoría
            self.new_category_name = ft.TextField(
                label="Nombre de la categoría",
                autofocus=True,
                width=300
            )
            
            self.new_category_description = ft.TextField(
                label="Descripción",
                width=300,
                multiline=True,
                min_lines=3,
                max_lines=5
            )
            
            # Mostrar diálogo
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Agregar nueva categoría"),
                content=ft.Column([
                    self.new_category_name,
                    self.new_category_description
                ], spacing=10, width=300),
                actions=[
                    ft.TextButton("Cancelar", on_click=self.close_dialog),
                    ft.TextButton("Guardar", on_click=self.add_category)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Error al mostrar diálogo de nueva categoría: {str(e)}")
            show_error_message(self.page, f"Error al mostrar diálogo: {str(e)}")

    def add_category(self, e):
        """Agrega una nueva categoría"""
        try:
            # Validar nombre
            if not self.new_category_name.value:
                show_error_message(self.page, "El nombre de la categoría es obligatorio")
                return
                
            # Preparar datos
            category_data = {
                "name": self.new_category_name.value,
                "description": self.new_category_description.value,
                "active": True
            }
            
            # Crear categoría
            new_category = self.category_service.create_category(category_data)
            
            # Cerrar diálogo
            self.close_dialog()
            
            if new_category:
                show_success_message(self.page, f"Categoría '{new_category.name}' creada correctamente")
                # Recargar categorías
                self.load_categories()
                # Seleccionar la nueva categoría
                for category in self.categories:
                    if category.id == new_category.id:
                        self.select_category(category)
                        break
            else:
                show_error_message(self.page, "No se pudo crear la categoría. El nombre podría estar duplicado.")
        except Exception as e:
            logger.error(f"Error al agregar categoría: {str(e)}")
            show_error_message(self.page, f"Error al agregar categoría: {str(e)}")

    def update(self):
        """Actualiza la interfaz de usuario"""
        self.page.update() 