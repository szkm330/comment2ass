import asyncio
from typing import Callable
from .downloader import asobi_download
from .converter import simulate_conversion
from .utils import get_file_and_path


def run_comment2ass(settings: dict, log: Callable[[str], None]):
    """
    执行完整的下载和转换流程，并使用传入的log函数来报告每个阶段的状态。

    :param settings: 一个包含所有UI设置的字典。
    :param log: 一个简单的日志记录函数，接收一个字符串参数。
    """
    try:
        log("选择目标站点: " + settings.get("target_site").name + "\n")
        
        # file_name:无后缀文件名, file_path:目录路径
        file_name, file_path = get_file_and_path(settings.get("save_path"))
        json_temp_path = f"{file_path/file_name}_temp.json"
        websocket_url = settings.get("websocket_url")


        # 下载json
        log("弹幕下载中...")
        #total_items = asyncio.run(asobi_download(websocket_url, json_temp_path))
        #log(f"下载结束，共{total_items}条弹幕")

        # --- 阶段 2: 转换 ---
        log("\n转换开始...")
        # 将settings字典传递给转换函数
        simulate_conversion(settings)
        log("转换结束")
        
        # --- 流程结束 ---
        log("\n全部任务已完成!")

    except Exception as e:
        log(f"\n{e}")
        raise