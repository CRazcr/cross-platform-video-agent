from .base import PlatformRule
from . import PlatformAdapter
from .douyin import DouyinAdapter
from .shipinhao import ShipinhaoAdapter
from .bilibili import BilibiliAdapter

__all__ = [
    "PlatformRule",
    "PlatformAdapter",
    "DouyinAdapter",
    "ShipinhaoAdapter",
    "BilibiliAdapter",
]