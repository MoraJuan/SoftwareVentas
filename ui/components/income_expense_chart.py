import flet as ft
from datetime import datetime, timedelta
from typing import Dict, List
from calendar import monthrange

class IncomeExpenseChart(ft.UserControl):
    def __init__(self, sale_service, expense_service):
        super().__init__()
        self.sale_service = sale_service
        self.expense_service = expense_service
        
        # Período seleccionado por defecto (mes actual)
        self.current_period = "month"
        self.today = datetime.now().date()
        
    def build(self):
        # Crear controles
        self.title = ft.Text("Ingresos vs Gastos", size=18, weight=ft.FontWeight.BOLD)
        
        # Selector de período
        self.period_dropdown = ft.Dropdown(
            label="Período",
            width=200,
            options=[
                ft.dropdown.Option("week", "Últimos 7 días"),
                ft.dropdown.Option("month", "Este mes"),
                ft.dropdown.Option("year", "Este año"),
            ],
            value=self.current_period,
            on_change=self.update_chart
        )
        
        # Contenedor para el gráfico
        self.chart_container = ft.Column(spacing=5)
        
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
                self.chart_container
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            width=600,
            height=400
        )
    
    def update_chart(self, e):
        self.current_period = self.period_dropdown.value
        self.update_data()
        self.update()
    
    def update_data(self):
        # Determinar fechas y etiquetas según el período seleccionado
        dates, labels = self.get_date_ranges()
        
        # Obtener datos financieros para cada período
        incomes = []
        expenses = []
        
        for start_date, end_date in dates:
            income = self.sale_service.get_total_sales_amount(start_date, end_date)
            expense = self.expense_service.get_total_expenses_amount(start_date, end_date)
            incomes.append(income)
            expenses.append(expense)
        
        # Encontrar el valor máximo para escalar el gráfico
        max_value = max(max(incomes, default=0), max(expenses, default=0))
        if max_value == 0:
            max_value = 1  # Evitar división por cero
        
        # Crear el gráfico
        self.create_chart(incomes, expenses, labels, max_value)
    
    def get_date_ranges(self):
        dates = []
        labels = []
        
        if self.current_period == "week":
            # Últimos 7 días
            for i in range(6, -1, -1):
                date = self.today - timedelta(days=i)
                dates.append((date, date))
                labels.append(date.strftime("%a"))
                
        elif self.current_period == "month":
            # Este mes por semanas
            month_start = datetime(self.today.year, self.today.month, 1).date()
            days_in_month = monthrange(self.today.year, self.today.month)[1]
            month_end = datetime(self.today.year, self.today.month, days_in_month).date()
            
            # Dividir el mes en 4 semanas aproximadamente
            week_count = 4
            days_per_week = days_in_month // week_count
            
            for i in range(week_count):
                start_day = i * days_per_week + 1
                end_day = (i + 1) * days_per_week if i < week_count - 1 else days_in_month
                
                start_date = datetime(self.today.year, self.today.month, start_day).date()
                end_date = datetime(self.today.year, self.today.month, end_day).date()
                
                dates.append((start_date, end_date))
                labels.append(f"Sem {i+1}")
                
        elif self.current_period == "year":
            # Este año por meses
            for month in range(1, 13):
                start_date = datetime(self.today.year, month, 1).date()
                days_in_month = monthrange(self.today.year, month)[1]
                end_date = datetime(self.today.year, month, days_in_month).date()
                
                dates.append((start_date, end_date))
                labels.append(start_date.strftime("%b"))
        
        return dates, labels
    
    def create_chart(self, incomes, expenses, labels, max_value):
        # Limpiar contenedor
        self.chart_container.controls = []
        
        # Altura del gráfico
        chart_height = 300
        
        # Crear filas para cada período
        chart_rows = []
        
        for i in range(len(labels)):
            # Calcular altura de las barras
            income_height = (incomes[i] / max_value) * chart_height if incomes[i] > 0 else 1
            expense_height = (expenses[i] / max_value) * chart_height if expenses[i] > 0 else 1
            
            # Crear barras
            income_bar = ft.Container(
                width=30,
                height=income_height,
                bgcolor=ft.colors.GREEN,
                border_radius=ft.border_radius.vertical(top=5)
            )
            
            expense_bar = ft.Container(
                width=30,
                height=expense_height,
                bgcolor=ft.colors.RED,
                border_radius=ft.border_radius.vertical(top=5)
            )
            
            # Crear columna para el período
            period_column = ft.Column([
                ft.Container(
                    content=ft.Column([
                        income_bar,
                        ft.Container(height=5),  # Espacio entre barras
                        expense_bar
                    ], alignment=ft.MainAxisAlignment.END),
                    height=chart_height,
                    alignment=ft.alignment.bottom_center
                ),
                ft.Text(labels[i], size=12)  # Etiqueta del período
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            chart_rows.append(period_column)
        
        # Crear leyenda
        legend = ft.Row([
            ft.Row([
                ft.Container(width=15, height=15, bgcolor=ft.colors.GREEN, border_radius=5),
                ft.Text("Ingresos")
            ]),
            ft.Container(width=20),  # Espacio
            ft.Row([
                ft.Container(width=15, height=15, bgcolor=ft.colors.RED, border_radius=5),
                ft.Text("Gastos")
            ])
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Agregar leyenda y gráfico al contenedor
        self.chart_container.controls.append(legend)
        self.chart_container.controls.append(ft.Divider())
        
        # Si no hay datos, mostrar mensaje
        if not chart_rows:
            self.chart_container.controls.append(
                ft.Container(
                    content=ft.Text("No hay datos para mostrar en este período", italic=True),
                    alignment=ft.alignment.center,
                    height=chart_height
                )
            )
        else:
            # Agregar gráfico
            self.chart_container.controls.append(
                ft.Container(
                    content=ft.Row(chart_rows, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    height=chart_height + 30  # Altura + espacio para etiquetas
                )
            ) 