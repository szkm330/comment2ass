import flet as ft
import os
from enum import Enum, auto
import threading
import time
from typing import Dict, List, Tuple
from core import run_comment2ass

class TargetSite(Enum):
    ASOBI = auto()

# Type alias for the log writer TextField
LogWriter = ft.TextField

def create_target_list(selected_index: Dict[str, TargetSite], log_writer: LogWriter) -> Tuple[ft.ListView, List[ft.Control]]:
    """Create the left-hand list view and its items."""
    list_items: List[ft.Control] = []

    def _on_click(e):
        selected_index["value"] = e.control.data
        
        for item in list_items:
            item.bgcolor = ft.Colors.GREY_300 if item.data == selected_index["value"] else None
            item.update()

    for site_enum in TargetSite:
        item = ft.ListTile(
            title=ft.Text(site_enum.name),
            data=site_enum,
            on_click=_on_click,
            bgcolor=ft.Colors.GREY_300 if site_enum == selected_index["value"] else None,
        )
        list_items.append(item)

    return ft.ListView(controls=list_items, expand=True), list_items


def create_input_field(label_text: str, value: str = "", expand: bool = True) -> ft.Column:
    """Creates a labeled text input field."""
    return ft.Column(
        controls=[
            ft.Text(label_text, size=14),
            ft.TextField(
                value=value,
                border=ft.InputBorder.OUTLINE,
                dense=True
            ),
        ],
        spacing=5,
        expand=expand,
    )


def create_input_grid() -> Tuple[ft.Column, Dict[str, ft.TextField]]:
    
    # 创建Column
    line_count_col = create_input_field("弹幕行数", "11")
    prefix_col = create_input_field("ASS代码前缀", r"\fnMS PGothic\b1\bord2\blur0")
    font_size_col = create_input_field("弹幕大小", "46")
    density_col = create_input_field("弹幕密度", "10")
    offset_col = create_input_field("时间轴偏移(提前←0→延后)", "0")
    speed_col = create_input_field("滚动速度(加快←0→减慢)", "1")

    # 从Column提取TextField，存入字典
    input_fields = {
        "line_count": line_count_col.controls[1],
        "prefix": prefix_col.controls[1],
        "font_size": font_size_col.controls[1],
        "density": density_col.controls[1],
        "offset": offset_col.controls[1],
        "speed": speed_col.controls[1],
    }

    # 构建UI布局
    grid_layout = ft.Column(
        controls=[
            ft.Row([line_count_col, prefix_col]),
            ft.Row([font_size_col, density_col]),
            ft.Row([offset_col, speed_col]),
        ],
        spacing=10,
    )
    
    return grid_layout, input_fields


def create_file_picker(page: ft.Page) -> Tuple[ft.TextField, ft.Column]:

    path_input = ft.TextField(read_only=True, expand=True)
    
    file_picker = ft.FilePicker(
        on_result=lambda e: on_dir_picked(e)
    )
    
    page.overlay.append(file_picker)
    
    def on_dir_picked(e: ft.FilePickerResultEvent):
        if e.path:
            path_input.value = e.path
            path_input.update()
    
    def pick_directory(e):
        file_picker.save_file(
            dialog_title = "保存",
            file_name = "output.ass",
            allowed_extensions = ["ass"],
            initial_directory = os.getcwd()
        )
    
    picker_widget = ft.Column(
        controls=[
            ft.Text("保存目录", size=14),
            ft.Row(
                controls=[
                    path_input,
                    ft.OutlinedButton("浏览", on_click=pick_directory)
                ],
                spacing=10
            )
        ],
        spacing=5,
    )
    
    return path_input, picker_widget


def create_main_button(
    page: ft.Page, 
    log_writer: LogWriter,
    selected_index: Dict[str, TargetSite],
    grid_inputs: Dict[str, ft.TextField],
    path_input: ft.TextField,
    checkbox: ft.Checkbox,
    websocket_input: ft.TextField
) -> ft.Control:

    # 创建按钮内容组件
    progress_ring = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
    button_text = ft.Text("开始处理")

    main_button = ft.OutlinedButton(
        content=ft.Row(
            controls=[
                progress_ring,
                button_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        width=200,
    )

    def _background_task():
        
        def log_callback(message: str):
            # Append message to log_writer
            log_writer.value += message + "\n"
            log_writer.update()

        # 输入参数字典
        settings = {
            "target_site": selected_index['value'],
            "line_count": grid_inputs['line_count'].value,
            "prefix": grid_inputs['prefix'].value,
            "font_size": grid_inputs['font_size'].value,
            "density": grid_inputs['density'].value,
            "offset": grid_inputs['offset'].value,
            "speed": grid_inputs['speed'].value,
            "save_path": path_input.value or "output.ass",
            "keep_temp_files": checkbox.value,
            "websocket_url": websocket_input.value,
        }
        
        try:
            # 传入settings和log函数
            run_comment2ass(settings=settings, log=log_callback)
        except Exception as e:
            log_callback(f"{e}")
        finally:
            # 任务完成后，恢复按钮状态
            main_button.disabled = False
            progress_ring.visible = False
            button_text.value = "开始处理"
            main_button.update()

    def on_click(e):
        # 点击时，改变按钮状态，显示正在处理
        main_button.disabled = True
        progress_ring.visible = True
        button_text.value = "处理中..."
        log_writer.value = "" # 点击时清空日志
        main_button.update()
        log_writer.update()
        threading.Thread(target=_background_task, daemon=True).start()

    main_button.on_click = on_click
    return main_button

def create_center_panel(page: ft.Page, log_writer: LogWriter, selected_index: Dict[str, TargetSite]) -> ft.Column:

    input_grid_ui, grid_inputs = create_input_grid()
    
    path_input, picker_widget = create_file_picker(page)
    checkbox = ft.Checkbox(label="保留临时文件 (json, xml)", value=False)
    
    websocket_field_col = create_input_field(label_text="WebSocket", value="wss://")
    # 从Column提取TextField
    websocket_input = websocket_field_col.controls[1]
    
    # 创建主按钮
    main_button = create_main_button(
        page, 
        log_writer, 
        selected_index, 
        grid_inputs, 
        path_input, 
        checkbox, 
        websocket_input
    )

    return ft.Column(
        controls=[
            input_grid_ui,
            ft.Divider(height=20),
            picker_widget,
            checkbox,
            websocket_field_col,
            ft.Container(content=main_button, alignment=ft.alignment.center, padding=10),
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )


def create_right_log_panel() -> Tuple[ft.TextField, ft.Column]:
    # 创建右侧日志输出面板
    log_output_field = ft.TextField(
        read_only=True,
        multiline=True,
        expand=True,
        min_lines=20,
        border=ft.InputBorder.OUTLINE,
    )

    log_panel = ft.Column(
        controls=[
            ft.Text("日志输出"),
            log_output_field,
        ],
        expand=True,
        spacing=10,
    )
    return log_output_field, log_panel