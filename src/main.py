import flet as ft
from typing import Dict
from ui import *


def main(page: ft.Page):
    # Basic page/window settings
    page.title = "Comment2ass"
    page.padding = 15
    page.window.width = 1100
    page.window.height = 600
    page.window.resizable = False
    page.window.maximizable = False
    page.fonts = {"LXGWWenKaiLite": "/fonts/LXGWWenKaiLite-Medium.ttf"}
    page.theme = ft.Theme(
        font_family="LXGWWenKaiLite", 
        color_scheme=ft.ColorScheme(primary=ft.Colors.BLACK)
    )

    # Initialize state that will be shared between components
    selected_index: Dict[str, TargetSite] = {"value": list(TargetSite)[0]}

    # Create UI panels by calling functions from the ui module
    log_output_field, right_log_panel = create_right_log_panel()
    left_list, _ = create_target_list(selected_index, log_output_field)
    

    center_panel = create_center_panel(page, log_output_field, selected_index)

    # Assemble the main layout
    main_layout = ft.Row(
        controls=[
            ft.Container(content=left_list, width=130, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=5, padding=5),
            ft.VerticalDivider(width=1),
            ft.Container(content=center_panel, expand=True, padding=10),
            ft.VerticalDivider(width=1),
            ft.Container(content=right_log_panel, width=300, padding=10),
        ],
        expand=True,
    )

    page.add(main_layout)


if __name__ == "__main__":
    ft.app(main)