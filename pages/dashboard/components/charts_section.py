import flet as ft

def create_charts_section():
    return ft.ResponsiveRow([
        create_sales_chart(),
        create_products_chart()
    ])

def create_sales_chart():
    return ft.Container(
        content=ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Sales Overview", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=300)
                ]),
                padding=20
            )
        ),
        col={"sm": 12, "md": 6, "lg": 6},
        padding=10
    )

def create_products_chart():
    return ft.Container(
        content=ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Top Products", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=300)
                ]),
                padding=20
            )
        ),
        col={"sm": 12, "md": 6, "lg": 6},
        padding=10
    )