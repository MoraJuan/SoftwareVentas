import flet as ft
from datetime import datetime, date
from services.productService import ProductService
from database.connection import get_db
from utils.ui_components import create_appbar, create_sidebar
from models.Product import Product

class InventoryManagementPage(ft.View):
    def __init__(self, page: ft.Page, session=None):
        super().__init__(
            route="/gestionar_inventario",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.db = session or next(get_db())
        self.product_service = ProductService(self.db)
        
        # Estado
        self.selected_product = None
        self.products = []
        
        # Controles de búsqueda
        self.search_field = ft.TextField(
            label="Buscar productos",
            hint_text="Nombre, categoría o descripción",
            expand=True,
            on_change=self.search_products
        )
        
        # Tabla de productos
        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[],
            on_select_changed=self.on_product_select
        )
        
        # Formulario de producto
        self.product_id_field = ft.TextField(label="ID", read_only=True)
        self.name_field = ft.TextField(label="Nombre", required=True)
        self.description_field = ft.TextField(label="Descripción", multiline=True)
        self.category_field = ft.TextField(label="Categoría")
        self.price_field = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER, required=True)
        self.stock_field = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER, required=True)
        
        # Controles de ajuste de stock
        self.stock_adjustment_field = ft.TextField(
            label="Cantidad",
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0"
        )
        self.stock_reason_field = ft.TextField(
            label="Razón",
            hint_text="Motivo del ajuste de stock"
        )
        
        self.build_ui()
        
    def build_ui(self):
        # Cargar datos iniciales
        self.load_products()
        
        # Construir la interfaz
        self.controls = [
            ft.Column([
                create_appbar(self.page, "Gestión de Inventario"),
                ft.Row([
                    create_sidebar(self.page),
                    ft.Column([
                        # Panel de búsqueda
                        ft.Container(
                            content=ft.Row([
                                self.search_field,
                                ft.FilledButton(
                                    text="Buscar",
                                    on_click=self.search_products
                                ),
                                ft.OutlinedButton(
                                    text="Nuevo Producto",
                                    on_click=self.new_product
                                )
                            ]),
                            padding=10,
                            margin=10,
                            border_radius=10,
                            border=ft.border.all(1, ft.colors.OUTLINE)
                        ),
                        
                        # Tabla de productos
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Productos", size=20, weight=ft.FontWeight.BOLD),
                                self.products_table
                            ]),
                            padding=10,
                            margin=10,
                            border_radius=10,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            expand=True
                        ),
                        
                        # Panel de detalles y edición
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Detalles del Producto", size=20, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    # Columna izquierda - Datos básicos
                                    ft.Column([
                                        self.product_id_field,
                                        self.name_field,
                                        self.category_field,
                                        self.price_field,
                                        self.stock_field
                                    ], expand=True),
                                    
                                    # Columna derecha - Datos adicionales
                                    ft.Column([
                                        self.description_field
                                    ], expand=True)
                                ]),
                                
                                # Botones de acción para el producto
                                ft.Row([
                                    ft.FilledButton(
                                        text="Guardar",
                                        on_click=self.save_product
                                    ),
                                    ft.OutlinedButton(
                                        text="Cancelar",
                                        on_click=self.cancel_edit
                                    ),
                                    ft.FilledTonalButton(
                                        text="Eliminar",
                                        on_click=self.delete_product,
                                        color=ft.colors.RED
                                    )
                                ], alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=10,
                            margin=10,
                            border_radius=10,
                            border=ft.border.all(1, ft.colors.OUTLINE)
                        ),
                        
                        # Panel de ajuste de stock
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ajuste de Stock", size=20, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    self.stock_adjustment_field,
                                    self.stock_reason_field
                                ]),
                                ft.Row([
                                    ft.FilledButton(
                                        text="Añadir Stock",
                                        on_click=self.add_stock
                                    ),
                                    ft.FilledTonalButton(
                                        text="Reducir Stock",
                                        on_click=self.remove_stock
                                    ),
                                    ft.OutlinedButton(
                                        text="Ajustar a Valor",
                                        on_click=self.adjust_stock
                                    )
                                ], alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=10,
                            margin=10,
                            border_radius=10,
                            border=ft.border.all(1, ft.colors.OUTLINE)
                        )
                    ], expand=True, scroll=ft.ScrollMode.AUTO)
                ], expand=True)
            ])
        ]
    
    def load_products(self):
        """Carga todos los productos en la tabla"""
        self.products = self.product_service.get_all_products()
        self.update_products_table()
    
    def update_products_table(self):
        """Actualiza la tabla de productos con los datos actuales"""
        self.products_table.rows.clear()
        
        for product in self.products:
            self.products_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(product.id))),
                        ft.DataCell(ft.Text(product.name)),
                        ft.DataCell(ft.Text(product.category or "-")),
                        ft.DataCell(ft.Text(str(product.stock))),
                        ft.DataCell(ft.Text(f"${product.price:.2f}")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda e, id=product.id: self.edit_product(id)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Eliminar",
                                    on_click=lambda e, id=product.id: self.confirm_delete(id)
                                )
                            ])
                        )
                    ],
                    data=product.id
                )
            )
        
        self.page.update()
    
    def search_products(self, e=None):
        """Busca productos según el término de búsqueda"""
        search_term = self.search_field.value
        if not search_term:
            self.load_products()
        else:
            self.products = self.product_service.search_products(search_term)
            self.update_products_table()
    
    def on_product_select(self, e):
        """Maneja la selección de un producto en la tabla"""
        if e.data == "true" and e.row.data:
            self.edit_product(e.row.data)
    
    def edit_product(self, product_id):
        """Carga los datos de un producto para edición"""
        product = self.product_service.get_product_by_id(product_id)
        if product:
            self.selected_product = product
            
            # Cargar datos en el formulario
            self.product_id_field.value = str(product.id)
            self.name_field.value = product.name
            self.description_field.value = product.description or ""
            self.category_field.value = product.category or ""
            self.price_field.value = str(product.price)
            self.stock_field.value = str(product.stock)
            
            self.page.update()
    
    def new_product(self, e=None):
        """Prepara el formulario para un nuevo producto"""
        self.selected_product = None
        
        # Limpiar formulario
        self.product_id_field.value = ""
        self.name_field.value = ""
        self.description_field.value = ""
        self.category_field.value = ""
        self.price_field.value = ""
        self.stock_field.value = "0"
        
        self.page.update()
    
    def save_product(self, e):
        """Guarda los cambios en un producto existente o crea uno nuevo"""
        try:
            # Validar campos requeridos
            if not self.name_field.value:
                self.show_snackbar("El nombre del producto es obligatorio", ft.colors.RED)
                return
                
            if not self.price_field.value or float(self.price_field.value) <= 0:
                self.show_snackbar("El precio debe ser mayor que cero", ft.colors.RED)
                return
            
            # Preparar datos del producto
            product_data = {
                "name": self.name_field.value,
                "description": self.description_field.value,
                "category": self.category_field.value,
                "price": float(self.price_field.value),
                "stock": int(self.stock_field.value)
            }
            
            # Guardar producto
            if self.selected_product:
                # Actualizar producto existente
                self.product_service.update_product(self.selected_product.id, product_data)
                self.show_snackbar("Producto actualizado correctamente", ft.colors.GREEN)
            else:
                # Crear nuevo producto
                self.product_service.create_product(product_data)
                self.show_snackbar("Producto creado correctamente", ft.colors.GREEN)
            
            # Recargar productos
            self.load_products()
            
        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.colors.RED)
    
    def cancel_edit(self, e):
        """Cancela la edición actual"""
        self.selected_product = None
        self.new_product()
    
    def confirm_delete(self, product_id):
        """Muestra un diálogo de confirmación para eliminar un producto"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        def confirm_delete_action(e):
            close_dialog(e)
            self.delete_product_by_id(product_id)
            
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar este producto? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.TextButton("Eliminar", on_click=confirm_delete_action)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_product(self, e):
        """Elimina el producto actualmente seleccionado"""
        if self.selected_product:
            self.confirm_delete(self.selected_product.id)
    
    def delete_product_by_id(self, product_id):
        """Elimina un producto por su ID"""
        try:
            success = self.product_service.delete_product(product_id)
            if success:
                self.show_snackbar("Producto eliminado correctamente", ft.colors.GREEN)
                self.load_products()
                self.new_product()
            else:
                self.show_snackbar("No se pudo eliminar el producto", ft.colors.RED)
        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.colors.RED)
    
    def add_stock(self, e):
        """Añade stock al producto seleccionado"""
        if not self.selected_product:
            self.show_snackbar("Debe seleccionar un producto", ft.colors.RED)
            return
            
        try:
            amount = int(self.stock_adjustment_field.value)
            if amount <= 0:
                self.show_snackbar("La cantidad debe ser mayor que cero", ft.colors.RED)
                return
                
            reason = self.stock_reason_field.value or "Reposición"
            
            self.product_service.add_stock(
                product_id=self.selected_product.id,
                amount=amount,
                reason=reason
            )
            
            self.show_snackbar(f"Se añadieron {amount} unidades al stock", ft.colors.GREEN)
            self.load_products()
            self.edit_product(self.selected_product.id)
            
        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.colors.RED)
    
    def remove_stock(self, e):
        """Reduce stock del producto seleccionado"""
        if not self.selected_product:
            self.show_snackbar("Debe seleccionar un producto", ft.colors.RED)
            return
            
        try:
            amount = int(self.stock_adjustment_field.value)
            if amount <= 0:
                self.show_snackbar("La cantidad debe ser mayor que cero", ft.colors.RED)
                return
                
            reason = self.stock_reason_field.value or "Salida"
            
            self.product_service.remove_stock(
                product_id=self.selected_product.id,
                amount=amount,
                reason=reason
            )
            
            self.show_snackbar(f"Se retiraron {amount} unidades del stock", ft.colors.GREEN)
            self.load_products()
            self.edit_product(self.selected_product.id)
            
        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.colors.RED)
    
    def adjust_stock(self, e):
        """Ajusta el stock a un valor específico"""
        if not self.selected_product:
            self.show_snackbar("Debe seleccionar un producto", ft.colors.RED)
            return
            
        try:
            new_stock = int(self.stock_adjustment_field.value)
            if new_stock < 0:
                self.show_snackbar("El stock no puede ser negativo", ft.colors.RED)
                return
                
            reason = self.stock_reason_field.value or "Ajuste manual"
            
            self.product_service.adjust_stock(
                product_id=self.selected_product.id,
                new_stock=new_stock,
                reason=reason
            )
            
            self.show_snackbar(f"Stock ajustado a {new_stock} unidades", ft.colors.GREEN)
            self.load_products()
            self.edit_product(self.selected_product.id)
            
        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.colors.RED)
    
    def show_snackbar(self, message, color=None):
        """Muestra un mensaje en un snackbar"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    page.title = "Gestión de Inventario"
    inventory_management_page = InventoryManagementPage(page)
    page.add(inventory_management_page.build())

if __name__ == "__main__":
    ft.app(target=main) 