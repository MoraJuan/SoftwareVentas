import flet as ft

def create_responsive_layout(page: ft.Page, nav_container, content_area):
    """Create a responsive layout based on screen width"""
    if not page:
        return ft.Container(expand=True)
        
    try:
        def get_layout_by_width():
            if page.width < 600:
                return ft.Column(
                    controls=[nav_container, content_area],
                    expand=True,
                    spacing=0
                )
            return ft.Row(
                controls=[
                    nav_container,
                    ft.VerticalDivider(width=1),
                    content_area
                ],
                expand=True,
                spacing=0
            )

        return ft.Container(
            content=get_layout_by_width(),
            expand=True
        )
    except Exception as e:
        print(f"Error creating responsive layout: {str(e)}")
        return ft.Container(
            content=ft.Text("Error loading layout", color=ft.colors.RED),
            expand=True
        )