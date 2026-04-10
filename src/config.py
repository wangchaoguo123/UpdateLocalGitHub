"""
配置加载模块

从 config.json 读取配置，支持默认值和文件不存在时的降级处理。
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "exclude_dirs": [
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".idea",
        ".vscode",
        ".svn",
        ".hg"
    ],
    "git_timeout": 10,
    "fetch_timeout": 60,
    "pull_timeout": 60
}

_config = None


def load_config(config_path=None):
    """
    加载配置文件

    参数:
        config_path: 配置文件路径，默认为项目根目录的 config.json

    返回值:
        配置字典
    """
    global _config
    
    if _config is not None:
        return _config
    
    if config_path is None:
        # 默认查找项目根目录的 config.json
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    if not os.path.exists(config_path):
        logger.warning(f"配置文件不存在，使用默认配置: {config_path}")
        _config = DEFAULT_CONFIG.copy()
        return _config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
        
        # 合并配置，缺省项使用默认值
        _config = DEFAULT_CONFIG.copy()
        _config.update(user_config)
        
        logger.info(f"配置文件加载成功: {config_path}")
        return _config
    
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {e}，使用默认配置")
        _config = DEFAULT_CONFIG.copy()
        return _config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}，使用默认配置")
        _config = DEFAULT_CONFIG.copy()
        return _config


def get_exclude_dirs():
    """
    获取排除目录列表

    返回值:
        排除目录列表
    """
    config = load_config()
    return config.get("exclude_dirs", [])


def get_git_timeout():
    """
    获取 Git 命令超时时间（秒）

    返回值:
        超时时间（整数）
    """
    config = load_config()
    return config.get("git_timeout", 10)


def get_fetch_timeout():
    """
    获取 git fetch 超时时间（秒）

    返回值:
        超时时间（整数）
    """
    config = load_config()
    return config.get("fetch_timeout", 60)


def get_pull_timeout():
    """
    获取 git pull 超时时间（秒）

    返回值:
        超时时间（整数）
    """
    config = load_config()
    return config.get("pull_timeout", 60)


def reload_config():
    """
    重新加载配置
    
    用于测试场景或配置更新后强制刷新
    """
    global _config
    _config = None
    return load_config()