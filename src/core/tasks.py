import asyncio
import os
from typing import Callable
from .downloader import asobi_download
from .json2xml import convert_json_to_xml
from .xml2ass import convert_xml_to_ass
from .utils import get_file_and_path


def run_comment2ass(settings: dict, log: Callable[[str], None]):
    """
    :param settings: 包含所有UI设置的字典
    :param log: 日志记录函数，接收一个字符串参数
    """
    try:
        log("选择目标站点: " + settings.get("target_site").name + "\n")
        
        websocket_url = settings.get("websocket_url")
        
        # file_name:无后缀文件名, file_path:目录路径
        file_name, file_path = get_file_and_path(settings.get("save_path"))
        json_temp_path = f"{file_path/file_name}_temp.json"
        xml_temp_path = f"{file_path/file_name}_temp.xml"
        ass_output_path = f"{file_path/file_name}.ass"

        # 是否保留临时文件
        keep_temp_files = settings.get("keep_temp_files", False)


        # 下载json
        log("弹幕下载中...")
        total_items = asyncio.run(asobi_download(websocket_url, json_temp_path))
        log(f"\n下载结束，共{total_items}条弹幕")

        # json转xml
        log("\n转换开始...")
        convert_json_to_xml(json_temp_path, xml_temp_path)

        # xml转ass
        convert_xml_to_ass(xml_temp_path, ass_output_path)

        # 删除临时文件
        if not keep_temp_files:
            os.remove(json_temp_path)
            os.remove(xml_temp_path)
        
        log("\n转换结束")
        
        # --- 流程结束 ---
        log("\n全部任务已完成!")

    except Exception as e:
        log(f"\n{e}")
        raise