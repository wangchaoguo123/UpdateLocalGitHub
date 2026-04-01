"""
常量定义模块

定义项目中使用的各种常量，包括错误消息、状态消息等。
"""


class ErrorMessages:
    """错误消息常量"""
    
    PATH_NOT_EXIST = "error: 路径不存在"
    NOT_DIRECTORY = "error: 路径不是目录"
    NOT_GIT_REPO = "error: 不是 Git 仓库"
    CHECK_FAILED = "error: 检查更新失败"
    PULL_FAILED = "error: 拉取更新失败"


class StatusMessages:
    """状态消息常量"""
    
    UP_TO_DATE = "Already up to date."


class CSVConfig:
    """CSV 配置常量"""
    
    HEADERS = ['仓库名称', '本地路径', '更新时间', '更新履历']
    FILENAME_PREFIX = "result_"
    FILENAME_SUFFIX = ".csv"
    DATE_FORMAT = "%Y%m%d"