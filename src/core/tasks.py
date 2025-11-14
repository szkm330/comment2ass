from typing import Callable
from .downloader import simulate_download
from .converter import simulate_conversion

def run_full_process(settings: dict, log: Callable[[str], None]):
    """
    执行完整的下载和转换流程，并使用传入的log函数来报告每个阶段的状态。

    :param settings: 一个包含所有UI设置的字典。
    :param log: 一个简单的日志记录函数，接收一个字符串参数。
    """
    try:
        log("选择目标站点: " + settings.get("target_site").name + "\n")
        # --- 阶段 1: 下载 ---
        log("下载开始...")
        # 将settings字典传递给下载函数
        total_items = simulate_download(settings)
        log(f"下载结束，共{total_items}条")

        # --- 阶段 2: 转换 ---
        log("\n转换开始...")
        # 将settings字典传递给转换函数
        simulate_conversion(settings)
        log("转换结束")
        
        # --- 流程结束 ---
        log("\n全部任务已完成!")

    except Exception as e:
        log(f"\n处理过程中发生错误: {e}")
        raise