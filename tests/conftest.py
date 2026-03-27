"""pytest配置"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_novel_config():
    """示例小说配置"""
    return {
        "title": "测试小说",
        "theme": "成长与救赎",
        "genre": "现代都市",
        "style": "写实主义",
        "num_chapters": 3
    }


@pytest.fixture
def sample_outline():
    """示例大纲数据"""
    return {
        "plot_outline": "这是一个测试大纲",
        "main_conflict": "主要冲突",
        "plot_points": ["情节点1", "情节点2", "情节点3"]
    }


@pytest.fixture
def sample_characters():
    """示例角色数据"""
    return {
        "characters": [
            {"name": "主角", "description": "勇敢的年轻人"},
            {"name": "配角", "description": "主角的朋友"}
        ],
        "protagonist": {"name": "主角"},
        "antagonist": {"name": "反派"}
    }
