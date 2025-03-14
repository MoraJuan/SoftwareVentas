import flet as ft
from datetime import datetime, timedelta
from typing import Dict, List

class FinancialBalanceCard(ft.UserControl):
    def __init__(self, sale_service, expense_service):
        super().__init__()
        self.sale_service = sale_service
        self.expense_service = expense_service
        
        # Períodos predefinidos
        self.today = datetime.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.week_start = self.today - timedelta(days=self.today.weekday())
        self.month_start = datetime(self.today.year, self.today.month, 1).date()
        self.year_start = datetime(self.today.year, 1, 1).date()
        
        # Período seleccionado por defecto (mes actual)
        self.current_period = "month"
        
    def build(self):
        # Crear controles
        self.title = ft.Text("Balance Financiero", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE)
        
        # Selector de período
        self.period_dropdown = ft.Dropdown(
            label="Período",
            width=200,
            options=[
                ft.dropdown.Option("today", "Hoy"),
                ft.dropdown.Option("yesterday", "Ayer"),
                ft.dropdown.Option("week", "Esta semana"),
                ft.dropdown.Option("month", "Este mes"),
                ft.dropdown.Option("year", "Este año"),
            ],
            value=self.current_period,
            on_change=self.update_balance
        )
        
        # Indicadores financieros - Usar colores que contrasten bien en ambos temas
        self.income_text = ft.Text("Ingresos: $0.00", size=16, color=ft.colors.GREEN_ACCENT)
        self.expense_text = ft.Text("Gastos: $0.00", size=16, color=ft.colors.RED_ACCENT)
        self.balance_text = ft.Text("Balance: $0.00", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE)
        
        # Gráfico de distribución de gastos
        self.expense_distribution = ft.Text("Distribución de gastos:", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE)
        self.expense_categories = ft.Column(spacing=5)
        
        # Actualizar datos iniciales
        self.update_data()
        
        # Construir layout
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.title,
                    ft.Container(expand=True),
                    self.period_dropdown
                ]),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        self.income_text,
                        self.expense_text,
                        ft.Divider(),
                        self.balance_text,
                    ], spacing=10),
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=5,
                    margin=ft.margin.only(bottom=10)
                ),
                self.expense_distribution,
                self.expense_categories
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            width=400
        )
    
    def update_balance(self, e):
        self.current_period = self.period_dropdown.value
        self.update_data()
        self.update()
    
    def update_data(self):
        # Determinar fechas según el período seleccionado
        start_date, end_date = self.get_date_range()
        
        # Obtener datos financieros
        income = self.sale_service.get_total_sales_amount(start_date, end_date)
        expenses = self.expense_service.get_total_expenses_amount(start_date, end_date)
        balance = income - expenses
        
        # Actualizar textos
        self.income_text.value = f"Ingresos: ${income:.2f}"
        self.expense_text.value = f"Gastos: ${expenses:.2f}"
        
        # Actualizar balance con color según sea positivo o negativo
        self.balance_text.value = f"Balance: ${balance:.2f}"
        self.balance_text.color = ft.colors.GREEN if balance >= 0 else ft.colors.RED
        
        # Actualizar distribución de gastos
        self.update_expense_distribution(start_date, end_date)
    
    def get_date_range(self):
        if self.current_period == "today":
            return self.today, self.today
        elif self.current_period == "yesterday":
            return self.yesterday, self.yesterday
        elif self.current_period == "week":
            return self.week_start, self.today
        elif self.current_period == "month":
            return self.month_start, self.today
        elif self.current_period == "year":
            return self.year_start, self.today
        else:
            return self.month_start, self.today  # Por defecto, mes actual
    
    def update_expense_distribution(self, start_date, end_date):
        # Obtener todos los gastos en el rango de fechas
        expenses = self.expense_service.get_expenses_by_date_range(start_date, end_date)
        
        # Agrupar por categoría
        categories = {}
        for expense in expenses:
            if expense.category not in categories:
                categories[expense.category] = 0
            categories[expense.category] += expense.amount
        
        # Crear controles para mostrar la distribución
        self.expense_categories.controls = []
        
        # Colores para las categorías
        category_colors = {
            "compra_inventario": ft.colors.BLUE,
            "operativo": ft.colors.ORANGE,
            "salarios": ft.colors.PURPLE,
            "servicios": ft.colors.TEAL,
            "otros": ft.colors.GREY
        }
        
        # Nombres legibles para las categorías
        category_names = {
            "compra_inventario": "Compra de Inventario",
            "operativo": "Gastos Operativos",
            "salarios": "Salarios",
            "servicios": "Servicios",
            "otros": "Otros Gastos"
        }
        
        # Total de gastos
        total_expenses = sum(categories.values())
        
        # Mostrar cada categoría con su porcentaje
        for category, amount in categories.items():
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            color = category_colors.get(category, ft.colors.GREY)
            name = category_names.get(category, category)
            
            self.expense_categories.controls.append(
                ft.Row([
                    ft.Container(width=15, height=15, bgcolor=color, border_radius=5),
                    ft.Text(f"{name}: ${amount:.2f} ({percentage:.1f}%)"),
                ])
            )
        
        # Si no hay gastos, mostrar mensaje
        if not categories:
            self.expense_categories.controls.append(
                ft.Text("No hay gastos registrados en este período", italic=True)
            ) 