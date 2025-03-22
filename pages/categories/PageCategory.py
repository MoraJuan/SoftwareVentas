import flet as ft
from sqlalchemy.orm import Session
from services.categoryService import CategoryService
from services.subcategoryService import SubcategoryService
from ui.components.alerts import show_success_message, show_error_message
from ui.components.data_table_category import DataTableCategory
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PageCategory(ft.UserControl):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__()
        self.page = page
        self.session = session
        self.category_service = CategoryService(session)
        self.subcategory_service = SubcategoryService(session)
        self.categories = []
        self.selected_category = None
        self.selected_subcategory = None
        self.is_mobile = self.page.width < 600
        self.build_ui()
        self.page.on_resize = self.handle_resize

    def build_ui(self):
        try:
            # Determinar dimensiones responsivas
            left_width = min(self.page.width * 0.25, 250) if not self.is_mobile else self.page.width * 0.9
            middle_width = min(self.page.width * 0.25, 250) if not self.is_mobile else self.page.width * 0.9
            right_width = min(self.page.width * 0.5, 400) if not self.is_mobile else self.page.width * 0.9
            field_width = right_width - 40  # Restar padding

            # Crear el componente de tabla para categorías
            self.categories_table = DataTableCategory(
                title="Categorías",
                items=self.categories,
                on_item_selected=self.select_category,
                on_add_item=self.show_add_category_dialog,
            )

            # Crear el componente de tabla para subcategorías
            self.subcategories_table = DataTableCategory(
                title="Subcategorías",
                items=[],
                on_item_selected=self.select_subcategory,
                on_add_item=self.show_add_subcategory_dialog,
            )

            # Panel de detalles de categoría y subcategoría
            self.details_panel = self.build_details_panel(field_width)

            # Layout principal
            if self.is_mobile:
                self.layout = ft.Column(
                    controls=[
                        ft.Container(
                            content=self.categories_table,
                            width=left_width,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            bgcolor=ft.colors.SURFACE,
                        ),
                        ft.Container(
                            content=self.subcategories_table,
                            width=middle_width,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            bgcolor=ft.colors.SURFACE,
                        ),
                        ft.Container(
                            content=self.details_panel,
                            width=right_width,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            bgcolor=ft.colors.SURFACE,
                        ),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                )
            else:
                self.layout = ft.Row(
                    controls=[
                        ft.Container(
                            content=self.categories_table,
                            width=left_width,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            bgcolor=ft.colors.SURFACE,
                        ),
                        ft.VerticalDivider(width=1),
                        ft.Container(
                            content=self.subcategories_table,
                            width=middle_width,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            bgcolor=ft.colors.SURFACE,
                        ),
                        ft.VerticalDivider(width=1),
                        ft.Container(
                            content=self.details_panel,
                            width=right_width,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            bgcolor=ft.colors.SURFACE,
                        ),
                    ],
                    expand=True,
                    spacing=10,
                )

            # Guardar referencia a los paneles principales
            self.left_panel = self.layout.controls[0]
            self.middle_panel = self.layout.controls[2 if not self.is_mobile else 1]
            self.right_panel = self.layout.controls[4 if not self.is_mobile else 2]

            # No cargamos categorías aquí, se hará en did_mount

        except Exception as e:
            logger.error(f"Error construyendo UI: {str(e)}")
            show_error_message(self.page, f"Error construyendo UI: {str(e)}")

    def build_details_panel(self, field_width):
        self.details_title = ft.Text(
            "Detalles de la Categoría",
            size=16 if self.is_mobile else 20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.ON_SURFACE
        )

        self.category_name = ft.TextField(
            label="Nombre de la categoría",
            width=field_width,
            disabled=True,
        )
        self.category_description = ft.TextField(
            label="Descripción",
            width=field_width,
            multiline=True,
            min_lines=2 if self.is_mobile else 3,
            max_lines=4 if self.is_mobile else 5,
            disabled=True,
        )
        self.category_status = ft.Checkbox(
            label="Categoría activa",
            disabled=True,
        )

        self.category_save_button = ft.FilledButton(
            "Guardar cambios",
            icon=ft.icons.SAVE,
            on_click=self.save_category,
            disabled=True,
            width=field_width / 3 - 10 if self.is_mobile else None
        )
        self.category_cancel_button = ft.OutlinedButton(
            "Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.cancel_category_edit,
            disabled=True,
            width=field_width / 3 - 10 if self.is_mobile else None
        )
        self.category_delete_button = ft.FilledTonalButton(
            "Eliminar",
            icon=ft.icons.DELETE,
            on_click=self.confirm_delete_category,
            disabled=True,
            color=ft.colors.ERROR,
            width=field_width / 3 - 10 if self.is_mobile else None
        )

        self.subcategory_title = ft.Text(
            "Detalles de la Subcategoría",
            size=16 if self.is_mobile else 20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.ON_SURFACE
        )
        self.subcategory_name = ft.TextField(
            label="Nombre de la subcategoría",
            width=field_width,
            disabled=True,
        )
        self.subcategory_description = ft.TextField(
            label="Descripción",
            width=field_width,
            multiline=True,
            min_lines=2 if self.is_mobile else 3,
            max_lines=4 if self.is_mobile else 5,
            disabled=True,
        )
        self.subcategory_status = ft.Checkbox(
            label="Subcategoría activa",
            disabled=True,
        )

        self.subcategory_save_button = ft.FilledButton(
            "Guardar cambios",
            icon=ft.icons.SAVE,
            on_click=self.save_subcategory,
            disabled=True,
            width=field_width / 3 - 10 if self.is_mobile else None
        )
        self.subcategory_cancel_button = ft.OutlinedButton(
            "Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.cancel_subcategory_edit,
            disabled=True,
            width=field_width / 3 - 10 if self.is_mobile else None
        )
        self.subcategory_delete_button = ft.FilledTonalButton(
            "Eliminar",
            icon=ft.icons.DELETE,
            on_click=self.confirm_delete_subcategory,
            disabled=True,
            color=ft.colors.ERROR,
            width=field_width / 3 - 10 if self.is_mobile else None
        )

        category_buttons = ft.Row([
            self.category_save_button,
            self.category_cancel_button,
            self.category_delete_button
        ], spacing=5 if self.is_mobile else 10, alignment=ft.MainAxisAlignment.CENTER)

        subcategory_buttons = ft.Row([
            self.subcategory_save_button,
            self.subcategory_cancel_button,
            self.subcategory_delete_button
        ], spacing=5 if self.is_mobile else 10, alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            self.details_title,
            self.category_name,
            self.category_description,
            self.category_status,
            category_buttons,
            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
            self.subcategory_title,
            self.subcategory_name,
            self.subcategory_description,
            self.subcategory_status,
            subcategory_buttons
        ], spacing=10 if self.is_mobile else 20, expand=True)

    def did_mount(self):
        # Cargar categorías después de que el control se haya añadido a la página
        self.load_categories()

    def load_categories(self):
        try:
            self.categories = self.category_service.get_all_categories()
            logger.info(f"Categorías cargadas: {len(self.categories)}")
            self.categories_table.items = self.categories
            self.categories_table.update_table()
        
            if self.selected_category:
                logger.info(f"Categoría seleccionada: {self.selected_category.name}")
                for category in self.categories:
                    if category.id == self.selected_category.id:
                        self.categories_table.selected_item = category
                        self.categories_table.update_table()
                        self.select_category(category)
                        if self.selected_subcategory and hasattr(category, 'subcategories'):
                            for subcategory in category.subcategories:
                                if subcategory.id == self.selected_subcategory.id:
                                    self.select_subcategory(subcategory)
                                    break
                            break
                        break
        except Exception as e:
            logger.error(f"Error al cargar categorías: {str(e)}")
            show_error_message(self.page, f"Error al cargar categorías: {str(e)}")


    def select_category(self, category):
        try:
            self.selected_category = category
            self.selected_subcategory = None
        
            logger.info(f"Seleccionada categoría: {category.name}")
            logger.info(f"Subcategorías: {len(category.subcategories)}")

            self.subcategories_table.items = category.subcategories if hasattr(category, 'subcategories') else []
            self.subcategories_table.selected_item = None
            self.subcategories_table.update_table()

            # Actualizar campos de formulario        
            self.category_name.value = category.name
            self.category_description.value = category.description or ""
            self.category_status.value = category.active
        
            # Habilitar campos de formulario        
            self.category_name.disabled = False
            self.category_description.disabled = False
            self.category_status.disabled = False
            self.category_save_button.disabled = False
            self.category_cancel_button.disabled = False
            self.category_delete_button.disabled = False
        
            # Limpiar campos de formulario de subcategoría       
            self.subcategory_name.value = ""
            self.subcategory_description.value = ""
            self.subcategory_status.value = True
            self.subcategory_name.disabled = True
            self.subcategory_description.disabled = True
            self.subcategory_status.disabled = True
            self.subcategory_save_button.disabled = True
            self.subcategory_cancel_button.disabled = True
            self.subcategory_delete_button.disabled = True
        
            self.update()
        except Exception as e:
            logger.error(f"Error al seleccionar categoría: {str(e)}")
            show_error_message(self.page, f"Error al seleccionar categoría: {str(e)}")

    def select_subcategory(self, subcategory):
        try:
            if not subcategory:
                return
            
            self.selected_subcategory = subcategory
            logger.info(f"Seleccionada subcategoría: {subcategory.name}")
        
            # Actualizar los detalles de la subcategoría
            self.subcategory_name.value = subcategory.name
            self.subcategory_description.value = subcategory.description or ""
            self.subcategory_status.value = subcategory.active
        
            # Habilitar los controles de subcategoría
            self.subcategory_name.disabled = False
            self.subcategory_description.disabled = False
            self.subcategory_status.disabled = False
            self.subcategory_save_button.disabled = False
            self.subcategory_cancel_button.disabled = False
            self.subcategory_delete_button.disabled = False

            # Depurar los valores de los controles
            logger.info(f"Nombre de subcategoría: {self.subcategory_name.value}")
            logger.info(f"Descripción de subcategoría: {self.subcategory_description.value}")
            logger.info(f"Estado de subcategoría: {self.subcategory_status.value}")

            # Actualizar la tabla de subcategorías
            self.subcategories_table.selected_item = subcategory
            self.subcategories_table.update_table()
        
            # Forzar la actualización de la interfaz
            self.update()
        except Exception as e:
            logger.error(f"Error al seleccionar subcategoría: {str(e)}")
            show_error_message(self.page, f"Error al seleccionar subcategoría: {str(e)}")

    def save_category(self, e):
        try:
            if not self.selected_category:
                show_error_message(self.page, "No hay categoría seleccionada")
                return
            if not self.category_name.value:
                show_error_message(self.page, "El nombre es obligatorio")
                return

            category_data = {
                "name": self.category_name.value,
                "description": self.category_description.value,
                "active": self.category_status.value
            }
            updated_category = self.category_service.update_category(self.selected_category.id, category_data)
            if not updated_category:
                show_error_message(self.page, "No se pudo actualizar. El nombre podría estar duplicado.")
                return

            show_success_message(self.page, f"Categoría '{updated_category.name}' actualizada")
            self.load_categories()
        except Exception as e:
            logger.error(f"Error al guardar categoría: {str(e)}")
            show_error_message(self.page, f"Error al guardar: {str(e)}")

    def save_subcategory(self, e):
        try:
            if not self.selected_subcategory:
                show_error_message(self.page, "No hay subcategoría seleccionada")
                return
            if not self.subcategory_name.value:
                show_error_message(self.page, "El nombre es obligatorio")
                return

            subcategory_data = {
                "name": self.subcategory_name.value,
                "description": self.subcategory_description.value,
                "active": self.subcategory_status.value
            }
            updated_subcategory = self.subcategory_service.update_subcategory(self.selected_subcategory.id, subcategory_data)
            if not updated_subcategory:
                show_error_message(self.page, "No se pudo actualizar la subcategoría.")
                return

            show_success_message(self.page, f"Subcategoría '{updated_subcategory.name}' actualizada")
            self.load_categories()
        except Exception as e:
            logger.error(f"Error al guardar subcategoría: {str(e)}")
            show_error_message(self.page, f"Error al guardar: {str(e)}")

    def cancel_category_edit(self, e):
        try:
            if self.selected_category:
                category = self.category_service.get_category_by_id(self.selected_category.id)
                if category:
                    self.select_category(category)
                    show_success_message(self.page, "Cambios descartados")
                else:
                    self.clear_category_form()
            else:
                self.clear_category_form()
        except Exception as e:
            logger.error(f"Error al cancelar edición: {str(e)}")
            show_error_message(self.page, f"Error al cancelar: {str(e)}")

    def cancel_subcategory_edit(self, e):
        try:
            if self.selected_subcategory:
                subcategory = self.subcategory_service.get_subcategory_by_id(self.selected_subcategory.id)
                if subcategory:
                    self.select_subcategory(subcategory)
                    show_success_message(self.page, "Cambios descartados")
                else:
                    self.clear_subcategory_form()
            else:
                self.clear_subcategory_form()
        except Exception as e:
            logger.error(f"Error al cancelar edición de subcategoría: {str(e)}")
            show_error_message(self.page, f"Error al cancelar: {str(e)}")

    def clear_category_form(self):
        self.selected_category = None
        self.category_name.value = ""
        self.category_description.value = ""
        self.category_status.value = True
        self.category_name.disabled = True
        self.category_description.disabled = True
        self.category_status.disabled = True
        self.category_save_button.disabled = True
        self.category_cancel_button.disabled = True
        self.category_delete_button.disabled = True
        self.subcategories_table.items = []
        self.subcategories_table.update_table()
        self.clear_subcategory_form()
        self.update()

    def clear_subcategory_form(self):
        self.selected_subcategory = None
        self.subcategory_name.value = ""
        self.subcategory_description.value = ""
        self.subcategory_status.value = True
        self.subcategory_name.disabled = True
        self.subcategory_description.disabled = True
        self.subcategory_status.disabled = True
        self.subcategory_save_button.disabled = True
        self.subcategory_cancel_button.disabled = True
        self.subcategory_delete_button.disabled = True
        self.update()

    def confirm_delete_category(self, e):
        if not self.selected_category:
            show_error_message(self.page, "No hay categoría seleccionada")
            return
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"Eliminar '{self.selected_category.name}'"),
            content=ft.Text("¿Seguro? Esto eliminará también todas las subcategorías asociadas."),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.TextButton("Eliminar", on_click=self.delete_category)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def confirm_delete_subcategory(self, e):
        if not self.selected_subcategory:
            show_error_message(self.page, "No hay subcategoría seleccionada")
            return
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"Eliminar '{self.selected_subcategory.name}'"),
            content=ft.Text("¿Seguro? Esto no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.TextButton("Eliminar", on_click=self.delete_subcategory)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def delete_category(self, e):
        try:
            if not self.selected_category:
                show_error_message(self.page, "No hay categoría seleccionada")
                return
            success = self.category_service.delete_category(self.selected_category.id)
            self.close_dialog()
            if success:
                show_success_message(self.page, f"Categoría '{self.selected_category.name}' eliminada")
                self.clear_category_form()
                self.load_categories()
            else:
                show_error_message(self.page, "No se pudo eliminar")
        except Exception as e:
            logger.error(f"Error al eliminar categoría: {str(e)}")
            show_error_message(self.page, f"Error al eliminar: {str(e)}")

    def delete_subcategory(self, e):
        try:
            if not self.selected_subcategory:
                show_error_message(self.page, "No hay subcategoría seleccionada")
                return
            success = self.subcategory_service.delete_subcategory(self.selected_subcategory.id)
            self.close_dialog()
            if success:
                show_success_message(self.page, f"Subcategoría '{self.selected_subcategory.name}' eliminada")
                self.clear_subcategory_form()
                self.load_categories()
            else:
                show_error_message(self.page, "No se pudo eliminar")
        except Exception as e:
            logger.error(f"Error al eliminar subcategoría: {str(e)}")
            show_error_message(self.page, f"Error al eliminar: {str(e)}")

    def close_dialog(self, e=None):
        self.page.dialog.open = False
        self.page.update()

    def show_add_category_dialog(self, e):
        self.new_category_name = ft.TextField(
            label="Nombre",
            autofocus=True,
            width=250 if self.is_mobile else 300
        )
        self.new_category_description = ft.TextField(
            label="Descripción",
            width=250 if self.is_mobile else 300,
            multiline=True,
            min_lines=2 if self.is_mobile else 3,
            max_lines=4 if self.is_mobile else 5
        )
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Nueva Categoría"),
            content=ft.Column([
                self.new_category_name,
                self.new_category_description
            ], spacing=10, width=250 if self.is_mobile else 300),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.TextButton("Guardar", on_click=self.add_category)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def show_add_subcategory_dialog(self, e):
        if not self.selected_category:
            show_error_message(self.page, "Primero seleccione una categoría")
            return
            
        self.new_subcategory_name = ft.TextField(
            label="Nombre",
            autofocus=True,
            width=250 if self.is_mobile else 300
        )
        self.new_subcategory_description = ft.TextField(
            label="Descripción",
            width=250 if self.is_mobile else 300,
            multiline=True,
            min_lines=2 if self.is_mobile else 3,
            max_lines=4 if self.is_mobile else 5
        )
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"Nueva Subcategoría en '{self.selected_category.name}'"),
            content=ft.Column([
                self.new_subcategory_name,
                self.new_subcategory_description
            ], spacing=10, width=250 if self.is_mobile else 300),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.TextButton("Guardar", on_click=self.add_subcategory)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog.open = True
        self.page.update()

    def add_category(self, e):
        try:
            if not self.new_category_name.value:
                show_error_message(self.page, "El nombre es obligatorio")
                return
            category_data = {
                "name": self.new_category_name.value,
                "description": self.new_category_description.value,
                "active": True
            }
            new_category = self.category_service.create_category(category_data)
            self.close_dialog()
            if new_category:
                show_success_message(self.page, f"Categoría '{new_category.name}' creada")
                self.load_categories()
                for category in self.categories:
                    if category.id == new_category.id:
                        self.select_category(category)
                        self.categories_table.select_item(category)
                        break
            else:
                show_error_message(self.page, "No se pudo crear. Nombre duplicado?")
        except Exception as e:
            logger.error(f"Error al agregar categoría: {str(e)}")
            show_error_message(self.page, f"Error al agregar: {str(e)}")

    def add_subcategory(self, e):
        try:
            if not self.selected_category:
                show_error_message(self.page, "No hay categoría seleccionada")
                return
            if not self.new_subcategory_name.value:
                show_error_message(self.page, "El nombre es obligatorio")
                return
                
            subcategory_data = {
                "name": self.new_subcategory_name.value,
                "description": self.new_subcategory_description.value,
                "active": True
            }
            
            new_subcategory = self.subcategory_service.create_subcategory(
                self.selected_category.id, 
                subcategory_data
            )
            
            self.close_dialog()
            
            if new_subcategory:
                show_success_message(self.page, f"Subcategoría '{new_subcategory.name}' creada")
                category_id = self.selected_category.id
                self.load_categories()
                for category in self.categories:
                    if category.id == category_id:
                        self.select_category(category)
                        self.categories_table.select_item(category)
                        for subcategory in category.subcategories:
                            if subcategory.id == new_subcategory.id:
                                self.select_subcategory(subcategory)
                                break
                        break
            else:
                show_error_message(self.page, "No se pudo crear la subcategoría")
        except Exception as e:
            logger.error(f"Error al agregar subcategoría: {str(e)}")
            show_error_message(self.page, f"Error al agregar: {str(e)}")

    def handle_resize(self, e):
        new_is_mobile = self.page.width < 600
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.build_ui()
            self.load_categories()  # Recargar categorías después de reconstruir UI
            self.update()
        else:
            new_left_width = min(self.page.width * 0.25, 250) if not self.is_mobile else self.page.width * 0.9
            new_middle_width = min(self.page.width * 0.25, 250) if not self.is_mobile else self.page.width * 0.9
            new_right_width = min(self.page.width * 0.5, 400) if not self.is_mobile else self.page.width * 0.9
            new_field_width = new_right_width - 40
            
            self.left_panel.width = new_left_width
            self.middle_panel.width = new_middle_width
            self.right_panel.width = new_right_width
            
            self.category_name.width = new_field_width
            self.category_description.width = new_field_width
            self.category_save_button.width = new_field_width / 3 - 10 if self.is_mobile else None
            self.category_cancel_button.width = new_field_width / 3 - 10 if self.is_mobile else None
            self.category_delete_button.width = new_field_width / 3 - 10 if self.is_mobile else None
            self.subcategory_name.width = new_field_width
            self.subcategory_description.width = new_field_width
            self.subcategory_save_button.width = new_field_width / 3 - 10 if self.is_mobile else None
            self.subcategory_cancel_button.width = new_field_width / 3 - 10 if self.is_mobile else None
            self.subcategory_delete_button.width = new_field_width / 3 - 10 if self.is_mobile else None
            
            self.update()

    def build(self):
        return self.layout

    def update(self):
        self.page.update()