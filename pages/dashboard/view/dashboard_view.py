import flet as ft
from ..components.navigation_container import create_navigation_container
from ..components.content_area import create_content_area
from ..components.error_boundary import create_error_boundary
from ..layouts.responsive_layout import create_responsive_layout
from ui.components.alerts import show_error_message

class DashboardView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/dashboard",
            padding=0,
            bgcolor=ft.colors.BACKGROUND
        )
        self.page = page
        self.session = session
        self._mounted = False
        self.build_ui()

    def build_ui(self):
        try:
            # Create main components
            self.nav_container = create_navigation_container(
                self.page,
                self.handle_navigation,
                self.handle_logout
            )
            self.content_area = create_content_area(self.session)
            
            # Create responsive layout
            self.scaffold = create_responsive_layout(
                self.page,
                self.nav_container,
                self.content_area
            )
            
            # Set controls
            self.controls = [self.scaffold]
            
        except Exception as e:
            self.handle_error("Error building dashboard", e)

    def did_mount(self):
        """Called when the view is mounted"""
        self._mounted = True
        self.page.on_resize = self.handle_resize
        self.update()

    def will_unmount(self):
        """Called when the view is about to be unmounted"""
        self._mounted = False
        if self.page:
            self.page.on_resize = None

    def handle_resize(self, e=None):
        """Handle window resize events"""
        if not self._mounted or not self.page:
            return
            
        try:
            # Update layout based on new window size
            self.scaffold.content = create_responsive_layout(
                self.page,
                self.nav_container,
                self.content_area
            ).content
            
            self.update()
        except Exception as e:
            self.handle_error("Error handling resize", e)

    def handle_navigation(self, e):
        """Handle navigation rail selection"""
        if not self.page:
            return
            
        try:
            from ..utils.navigation import get_route_for_index
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            self.handle_error("Navigation error", e)

    def handle_logout(self, e):
        """Handle logout button click"""
        if not self.page:
            return
            
        try:
            self.page.client_storage.remove("token")
            self.page.client_storage.remove("user_role")
            self.page.go("/login")
        except Exception as e:
            self.handle_error("Logout error", e)

    def handle_error(self, context: str, error: Exception):
        """Centralized error handler"""
        error_msg = f"{context}: {str(error)}"
        print(f"Dashboard Error: {error_msg}")  # Log error
        
        if self.page:
            try:
                show_error_message(self.page, error_msg)
            except:
                # Fallback error display if snackbar fails
                self.controls = [create_error_boundary(error_msg, self.build_ui)]
                self.update()