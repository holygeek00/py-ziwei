"""
工具函数
移植自 iztro utils/index.ts
"""
from __future__ import annotations
from .constants import (
    EARTHLY_BRANCHES, HEAVENLY_STEMS, HEAVENLY_STEMS_INFO,
    STARS_BRIGHTNESS, MUTAGEN, AGE_START,
)
from .calendar_utils import solar_to_lunar


def fix_index(index: int, max_val: int = 12) -> int:
    """
    循环索引处理，将索引锁定在 0~max-1 范围内
    """
    if index < 0:
        return fix_index(index + max_val, max_val)
    if index > max_val - 1:
        return fix_index(index - max_val, max_val)
    # 处理 -0 的情况
    return 0 if index == 0 else index


def fix_earthly_branch_index(earthly_branch: str) -> int:
    """
    地支转宫位索引
    宫位从寅宫开始排列，所以需要减去寅的索引(2)
    """
    yin_idx = EARTHLY_BRANCHES.index("寅")
    branch_idx = EARTHLY_BRANCHES.index(earthly_branch)
    return fix_index(branch_idx - yin_idx)


def fix_lunar_month_index(
    solar_date_str: str,
    time_index: int,
    fix_leap: bool = True,
) -> int:
    """
    调整农历月份索引

    正月建寅, fixLeap 为是否调整闰月情况
    若调整闰月，则闰月的前15天按上月算，后面天数按下月算
    """
    info = solar_to_lunar(solar_date_str)
    lunar_month = info["lunarMonth"]
    lunar_day = info["lunarDay"]
    is_leap = info["isLeap"]
    first_index = EARTHLY_BRANCHES.index("寅")
    need_to_add = is_leap and fix_leap and lunar_day > 15 and time_index != 12
    return fix_index(lunar_month + 1 - first_index + (1 if need_to_add else 0))


def fix_lunar_day_index(lunar_day: int, time_index: int) -> int:
    """农历日索引，晚子时加1天"""
    return lunar_day if time_index >= 12 else lunar_day - 1


def get_brightness(star_name: str, index: int) -> str:
    """获取星耀亮度"""
    brightness_list = STARS_BRIGHTNESS.get(star_name)
    if not brightness_list:
        return ""
    return brightness_list[fix_index(index)]


def get_mutagen(star_name: str, heavenly_stem: str) -> str:
    """获取四化信息"""
    stem_info = HEAVENLY_STEMS_INFO.get(heavenly_stem)
    if not stem_info:
        return ""
    mutagen_list = stem_info.get("mutagen", [])
    if star_name in mutagen_list:
        idx = mutagen_list.index(star_name)
        if idx < len(MUTAGEN):
            return MUTAGEN[idx]
    return ""


def get_mutagens_by_heavenly_stem(heavenly_stem: str) -> list[str]:
    """获取某天干的四化星耀名称列表"""
    stem_info = HEAVENLY_STEMS_INFO.get(heavenly_stem)
    if not stem_info:
        return []
    return list(stem_info.get("mutagen", []))


def get_age_index(earthly_branch: str) -> int:
    """
    小限起始宫位索引
    """
    target = AGE_START.get(earthly_branch, "辰")
    return fix_earthly_branch_index(target)


def time_to_index(hour: int) -> int:
    """将小时转化为时辰索引"""
    if hour == 0:
        return 0
    if hour == 23:
        return 12
    return (hour + 1) // 2


def init_stars() -> list[list]:
    """初始化12个空列表，用于放置星耀"""
    return [[] for _ in range(12)]
