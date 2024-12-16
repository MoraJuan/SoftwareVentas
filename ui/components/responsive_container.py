import flet as ft

class ResponsiveContainer(ft.UserControl):
    def __init__(
        self,
        mobile_content,
        desktop_content,
        breakpoint: int = 600,
        **kwargs
    ):
        super().__init__()
        self.mobile_content = mobile_content
        self.desktop_content = desktop_content
        self.breakpoint = breakpoint
        self.container_kwargs = kwargs

    def build(self):
        def get_content():
            if self.page.width < self.breakpoint:
                return self.mobile_content
            return self.desktop_content

        return ft.Container(
            content=get_content(),
            **self.container_kwargs
        )

    def did_mount(self):
        self.page.on_resize = lambda _: self.update()