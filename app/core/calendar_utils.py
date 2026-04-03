"""
农历/阳历转换工具
基于 lunar_python (寿星万年历)
"""
from __future__ import annotations
from lunar_python import Lunar, Solar

from .constants import HEAVENLY_STEMS, EARTHLY_BRANCHES, ZODIAC, SIGNS


def solar_to_lunar(solar_date_str: str) -> dict:
    """
    阳历转农历
    :param solar_date_str: YYYY-M-D 格式
    :return: dict with lunarYear, lunarMonth, lunarDay, isLeap
    """
    parts = solar_date_str.split("-")
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    solar = Solar.fromYmd(y, m, d)
    lunar = solar.getLunar()
    return {
        "lunarYear": lunar.getYear(),
        "lunarMonth": abs(lunar.getMonth()),
        "lunarDay": lunar.getDay(),
        "isLeap": lunar.getMonth() < 0,
        "lunar": lunar,
    }


def lunar_to_solar(lunar_date_str: str, is_leap_month: bool = False) -> str:
    """
    农历转阳历
    :param lunar_date_str: YYYY-M-D 格式
    :param is_leap_month: 是否闰月
    :return: YYYY-M-D 格式阳历日期
    """
    parts = lunar_date_str.split("-")
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    if is_leap_month:
        m = -m
    lunar = Lunar.fromYmd(y, m, d)
    solar = lunar.getSolar()
    return f"{solar.getYear()}-{solar.getMonth()}-{solar.getDay()}"


def get_lunar_month_days(solar_date_str: str) -> int:
    """获取当月农历天数"""
    info = solar_to_lunar(solar_date_str)
    lunar: Lunar = info["lunar"]
    # 调用lunar_python获取当月总天数
    from lunar_python import LunarMonth
    lm = LunarMonth.fromYm(lunar.getYear(), lunar.getMonth())
    return lm.getDayCount() if lm else 30


def get_heavenly_stem_and_earthly_branch(
    solar_date_str: str,
    time_index: int,
    year_divide: str = "normal",
    month_divide: str = "normal",
) -> dict:
    """
    获取干支纪年信息

    :param solar_date_str: YYYY-M-D
    :param time_index: 时辰索引 0~12
    :param year_divide: normal=正月初一, exact=立春
    :param month_divide: normal=正月初一, exact=立春（影响月干支）
    :return: dict with yearly, monthly, daily, hourly tuples
    """
    parts = solar_date_str.split("-")
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    solar = Solar.fromYmd(y, m, d)
    lunar = solar.getLunar()

    # ---- 年干支 ----
    if year_divide == "exact":
        # 立春分界
        year_gz = lunar.getYearInGanZhiExact()
    else:
        year_gz = lunar.getYearInGanZhi()

    # ---- 月干支 ----
    if month_divide == "exact":
        month_gz = lunar.getMonthInGanZhiExact()
    else:
        month_gz = lunar.getMonthInGanZhi()

    # ---- 日干支 ----
    day_gz = lunar.getDayInGanZhi()

    # ---- 时干支 ----
    # time_index: 0=早子, 1=丑, ..., 12=晚子
    # 将时辰索引映射到实际的地支
    actual_branch_idx = time_index % 12
    day_stem = day_gz[0]
    day_stem_idx = HEAVENLY_STEMS.index(day_stem)

    # 五鼠遁日上起时
    RAT_RULE = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
    hour_stem_start = RAT_RULE[day_stem_idx]
    hour_stem_idx = (hour_stem_start + actual_branch_idx) % 10
    hour_stem = HEAVENLY_STEMS[hour_stem_idx]
    hour_branch = EARTHLY_BRANCHES[actual_branch_idx]

    return {
        "yearly": (year_gz[0], year_gz[1]),
        "monthly": (month_gz[0], month_gz[1]),
        "daily": (day_gz[0], day_gz[1]),
        "hourly": (hour_stem, hour_branch),
    }


def get_zodiac(earthly_branch: str) -> str:
    """通过年支获取生肖"""
    idx = EARTHLY_BRANCHES.index(earthly_branch)
    return ZODIAC[idx]


def get_sign(solar_date_str: str) -> str:
    """通过阳历日期获取星座"""
    parts = solar_date_str.split("-")
    m, d = int(parts[1]), int(parts[2])

    for sign_name, end_month, end_day in SIGNS:
        if m == end_month and d <= end_day:
            return sign_name
        if m < end_month:
            return sign_name

    return "摩羯座"


def get_zodiac_by_solar(solar_date_str: str, year_divide: str = "normal") -> str:
    """通过阳历日期获取生肖"""
    gz = get_heavenly_stem_and_earthly_branch(solar_date_str, 0, year_divide=year_divide)
    return get_zodiac(gz["yearly"][1])
