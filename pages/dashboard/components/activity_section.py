import flet as ft

def create_activity_section():
    activity_list = ft.ListView(
        expand=1,
        spacing=10,
        padding=20,
        height=200
    )
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Recent Activity", size=20, weight=ft.FontWeight.BOLD),
                activity_list
            ]),
            padding=20
        )
    )