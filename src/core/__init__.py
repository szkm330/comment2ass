"""
core 包的初始化文件，定义了包的公共 API。
现在只暴露一个高级别的任务执行函数。
"""
from .tasks import run_comment2ass

__all__ = ["run_comment2ass"]