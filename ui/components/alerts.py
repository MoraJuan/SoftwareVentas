import flet as ft
from typing import Optional

def show_error_message(page: Optional[ft.Page], message: str):
    """Show error message with fallback handling"""
    if not page:
        print(f"Error (no page context): {message}")
        return
        
    try:
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.RED_600,
                duration=5000
            )
        )
    except Exception as e:
        print(f"Error showing snackbar: {str(e)}")
        # Fallback to console
        print(f"Error: {message}")

def show_success_message(page: Optional[ft.Page], message: str):
    """Show success message with fallback handling"""
    if not page:
        print(f"Success (no page context): {message}")
        return
        
    try:
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.GREEN_600,
                duration=3000
            )
        )
    except Exception as e:
        print(f"Error showing snackbar: {str(e)}")
        # Fallback to console
        print(f"Success: {message}")