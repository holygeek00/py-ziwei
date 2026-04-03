"""
运限计算 — 大限/小限/流年/流月/流日/流时
移植自 iztro FunctionalAstrolabe._getHoroscopeBySolarDate + FunctionalHoroscope
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from app.core.constants import EARTHLY_BRANCHES, MUTAGEN, PALACES
from app.core.types import Astrolabe, Palace, Star, HoroscopeItem, Horoscope
from app.core.utils import (
    fix_index, fix_earthly_branch_index, get_mutagens_by_heavenly_stem, time_to_index,
)
from app.core.calendar_utils import (
    solar_to_lunar, get_heavenly_stem_and_earthly_branch,
)
from app.astro.palace import get_palace_names
from app.star.horoscope_star import get_horoscope_star
from app.star.decorative_star import get_yearly12
from app.astro.analyzer import (
    get_palace, get_surrounded_palaces, SurroundedPalaces,
    palace_has_stars, palace_not_have_stars, palace_has_one_of_stars,
    palace_has_mutagen, mutagens_to_stars,
)


def _merge_stars(*star_lists: list[list[Star]]) -> list[list[Star]]:
    """合并多组流耀"""
    result: list[list[Star]] = [[] for _ in range(12)]
    for sl in star_lists:
        for i in range(12):
            result[i].extend(sl[i])
    return result


def get_horoscope_data(
    astrolabe: Astrolabe,
    target_date: str | None = None,
    time_index: int | None = None,
    horoscope_divide: str = "normal",
    age_divide: str = "nominal",
) -> Horoscope:
    """
    获取运限数据

    :param astrolabe: 星盘对象
    :param target_date: 目标阳历日期 YYYY-M-D，默认为当天
    :param time_index: 时辰索引，默认取当前时间
    :param horoscope_divide: 运限分界点
    :param age_divide: 年龄分界 nominal(虚岁)/birthday(生日)
    """
    if not target_date:
        now = datetime.now()
        target_date = f"{now.year}-{now.month}-{now.day}"
    if time_index is None:
        time_index = time_to_index(datetime.now().hour)

    birthday_info = solar_to_lunar(astrolabe.solar_date)
    target_info = solar_to_lunar(target_date)

    convert_time_index = time_to_index(datetime.now().hour) if time_index is None else time_index
    actual_time_index = time_index if time_index is not None else convert_time_index

    gz = get_heavenly_stem_and_earthly_branch(
        target_date, actual_time_index, horoscope_divide, horoscope_divide,
    )
    yearly = gz["yearly"]
    monthly = gz["monthly"]
    daily = gz["daily"]
    hourly = gz["hourly"]

    # 虚岁
    nominal_age = target_info["lunarYear"] - birthday_info["lunarYear"]

    if age_divide == "birthday":
        if (
            (target_info["lunarYear"] == birthday_info["lunarYear"]
             and target_info["lunarMonth"] == birthday_info["lunarMonth"]
             and target_info["lunarDay"] > birthday_info["lunarDay"])
            or (target_info["lunarYear"] == birthday_info["lunarYear"]
                and target_info["lunarMonth"] > birthday_info["lunarMonth"])
            or target_info["lunarYear"] > birthday_info["lunarYear"]
        ):
            nominal_age += 1
    else:
        nominal_age += 1

    # 大限索引
    decadal_index = -1
    heavenly_stem_of_decade = ""
    earthly_branch_of_decade = ""
    is_childhood = False

    for i, p in enumerate(astrolabe.palaces):
        r = p.decadal.range
        if nominal_age >= r[0] and nominal_age <= r[1]:
            decadal_index = i
            heavenly_stem_of_decade = p.decadal.heavenly_stem
            earthly_branch_of_decade = p.decadal.earthly_branch
            break

    if decadal_index < 0:
        # 童限
        childhood_palaces = ["命宫", "财帛", "疾厄", "夫妻", "福德", "官禄"]
        target_palace_name = childhood_palaces[nominal_age - 1] if nominal_age <= 6 else "命宫"
        target_palace = get_palace(astrolabe, target_palace_name)
        if target_palace:
            is_childhood = True
            decadal_index = target_palace.index
            heavenly_stem_of_decade = target_palace.heavenly_stem
            earthly_branch_of_decade = target_palace.earthly_branch

    # 小限索引
    age_index = -1
    heavenly_stem_of_age = ""
    earthly_branch_of_age = ""
    for i, p in enumerate(astrolabe.palaces):
        if nominal_age in p.ages:
            age_index = i
            heavenly_stem_of_age = p.heavenly_stem
            earthly_branch_of_age = p.earthly_branch
            break

    # 流年索引
    yearly_index = fix_earthly_branch_index(yearly[1])

    # 流月索引
    birthday_gz = get_heavenly_stem_and_earthly_branch(astrolabe.solar_date, 0)
    hour_branch_of_birth = EARTHLY_BRANCHES.index(birthday_gz["hourly"][1]) if len(birthday_gz["hourly"]) > 1 else 0

    leap_addition = 1 if birthday_info["isLeap"] and birthday_info["lunarDay"] > 15 else 0
    date_leap_addition = 1 if target_info["isLeap"] and target_info["lunarDay"] > 15 else 0

    monthly_index = fix_index(
        yearly_index
        - (birthday_info["lunarMonth"] + leap_addition)
        + hour_branch_of_birth
        + (target_info["lunarMonth"] + date_leap_addition)
    )

    # 流日索引
    daily_index = fix_index(monthly_index + target_info["lunarDay"] - 1)

    # 流时索引
    hourly_branch_index = EARTHLY_BRANCHES.index(hourly[1])
    hourly_index = fix_index(daily_index + hourly_branch_index)

    # 构造流耀
    decadal_stars = get_horoscope_star(heavenly_stem_of_decade, earthly_branch_of_decade, "decadal") if heavenly_stem_of_decade else None
    yearly_stars = get_horoscope_star(yearly[0], yearly[1], "yearly")
    monthly_stars = get_horoscope_star(monthly[0], monthly[1], "monthly")
    daily_stars = get_horoscope_star(daily[0], daily[1], "daily")
    hourly_stars = get_horoscope_star(hourly[0], hourly[1], "hourly")

    yearly_dec = get_yearly12(target_date, horoscope_divide)

    return Horoscope(
        solar_date=target_date,
        lunar_date=f"{target_info['lunarYear']}年{target_info['lunarMonth']}月{target_info['lunarDay']}日",
        decadal=HoroscopeItem(
            index=decadal_index,
            name="童限" if is_childhood else "大限",
            heavenly_stem=heavenly_stem_of_decade,
            earthly_branch=earthly_branch_of_decade,
            palace_names=get_palace_names(decadal_index) if decadal_index >= 0 else [],
            mutagen=get_mutagens_by_heavenly_stem(heavenly_stem_of_decade) if heavenly_stem_of_decade else [],
            stars=decadal_stars,
        ),
        age=HoroscopeItem(
            index=age_index,
            name="小限",
            heavenly_stem=heavenly_stem_of_age,
            earthly_branch=earthly_branch_of_age,
            palace_names=get_palace_names(age_index) if age_index >= 0 else [],
            mutagen=get_mutagens_by_heavenly_stem(heavenly_stem_of_age) if heavenly_stem_of_age else [],
        ),
        yearly=HoroscopeItem(
            index=yearly_index,
            name="流年",
            heavenly_stem=yearly[0],
            earthly_branch=yearly[1],
            palace_names=get_palace_names(yearly_index),
            mutagen=get_mutagens_by_heavenly_stem(yearly[0]),
            stars=yearly_stars,
        ),
        monthly=HoroscopeItem(
            index=monthly_index,
            name="流月",
            heavenly_stem=monthly[0],
            earthly_branch=monthly[1],
            palace_names=get_palace_names(monthly_index),
            mutagen=get_mutagens_by_heavenly_stem(monthly[0]),
            stars=monthly_stars,
        ),
        daily=HoroscopeItem(
            index=daily_index,
            name="流日",
            heavenly_stem=daily[0],
            earthly_branch=daily[1],
            palace_names=get_palace_names(daily_index),
            mutagen=get_mutagens_by_heavenly_stem(daily[0]),
            stars=daily_stars,
        ),
        hourly=HoroscopeItem(
            index=hourly_index,
            name="流时",
            heavenly_stem=hourly[0],
            earthly_branch=hourly[1],
            palace_names=get_palace_names(hourly_index),
            mutagen=get_mutagens_by_heavenly_stem(hourly[0]),
            stars=hourly_stars,
        ),
    )


# ============================================================
# 运限宫位查询（FunctionalHoroscope 方法）
# ============================================================

def horoscope_palace(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
) -> Optional[Palace]:
    """获取运限宫位"""
    if scope == "origin":
        return get_palace(astrolabe, palace_name)

    scope_data = getattr(horoscope, scope, None)
    if not scope_data:
        return None

    target_index = scope_data.palace_names.index(palace_name) if palace_name in scope_data.palace_names else -1
    if target_index < 0:
        return None
    return get_palace(astrolabe, target_index)


def horoscope_surrounded_palaces(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
) -> Optional[SurroundedPalaces]:
    """获取运限宫位的三方四正"""
    if scope == "origin":
        return get_surrounded_palaces(astrolabe, palace_name)

    scope_data = getattr(horoscope, scope, None)
    if not scope_data:
        return None
    target_index = scope_data.palace_names.index(palace_name) if palace_name in scope_data.palace_names else -1
    if target_index < 0:
        return None
    return get_surrounded_palaces(astrolabe, target_index)


def horoscope_has_stars(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    star_names: list[str],
) -> bool:
    """判断运限宫位内是否包含流耀"""
    if not horoscope.decadal.stars or not horoscope.yearly.stars:
        return False

    scope_data = getattr(horoscope, scope, None)
    if not scope_data:
        return False

    palace_index = scope_data.palace_names.index(palace_name) if palace_name in scope_data.palace_names else -1
    if palace_index < 0:
        return False

    merged = _merge_stars(horoscope.decadal.stars, horoscope.yearly.stars)
    stars_in_palace = [s.name for s in merged[palace_index]]
    return all(s in stars_in_palace for s in star_names)


def horoscope_not_have_stars(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    star_names: list[str],
) -> bool:
    """判断运限宫位内是否不含流耀"""
    if not horoscope.decadal.stars or not horoscope.yearly.stars:
        return False

    scope_data = getattr(horoscope, scope, None)
    if not scope_data:
        return False

    palace_index = scope_data.palace_names.index(palace_name) if palace_name in scope_data.palace_names else -1
    if palace_index < 0:
        return False

    merged = _merge_stars(horoscope.decadal.stars, horoscope.yearly.stars)
    stars_in_palace = [s.name for s in merged[palace_index]]
    return all(s not in stars_in_palace for s in star_names)


def horoscope_is_surrounded_by_stars(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    star_names: list[str],
) -> bool:
    """判断运限宫位三方四正是否包含某些流耀"""
    sp = horoscope_surrounded_palaces(astrolabe, horoscope, palace_name, scope)
    if not sp:
        return False

    merged = _merge_stars(horoscope.decadal.stars or [[]]*12, horoscope.yearly.stars or [[]]*12)
    
    all_stars = []
    for p in [sp.target, sp.opposite, sp.wealth, sp.career]:
        all_stars.extend([s.name for s in merged[p.index]])
    
    return all(s in all_stars for s in star_names)


def horoscope_is_surrounded_by_one_of_stars(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    star_names: list[str],
) -> bool:
    """判断运限宫位三方四正是否包含其中一颗流耀"""
    sp = horoscope_surrounded_palaces(astrolabe, horoscope, palace_name, scope)
    if not sp:
        return False

    merged = _merge_stars(horoscope.decadal.stars or [[]]*12, horoscope.yearly.stars or [[]]*12)
    
    all_stars = []
    for p in [sp.target, sp.opposite, sp.wealth, sp.career]:
        all_stars.extend([s.name for s in merged[p.index]])
    
    return any(s in all_stars for s in star_names)


def horoscope_has_one_of_stars(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    star_names: list[str],
) -> bool:
    """判断运限宫位内是否含有其中一颗流耀"""
    if not horoscope.decadal.stars or not horoscope.yearly.stars:
        return False

    scope_data = getattr(horoscope, scope, None)
    if not scope_data:
        return False

    palace_index = scope_data.palace_names.index(palace_name) if palace_name in scope_data.palace_names else -1
    if palace_index < 0:
        return False

    merged = _merge_stars(horoscope.decadal.stars, horoscope.yearly.stars)
    stars_in_palace = [s.name for s in merged[palace_index]]
    return any(s in stars_in_palace for s in star_names)


def horoscope_has_mutagen(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    mutagen: str,
) -> bool:
    """判断运限宫位内是否存在运限四化"""
    if scope == "origin":
        return False

    scope_data = getattr(horoscope, scope, None)
    if not scope_data:
        return False

    palace_index = scope_data.palace_names.index(palace_name) if palace_name in scope_data.palace_names else -1
    if palace_index < 0:
        return False

    p = get_palace(astrolabe, palace_index)
    if not p:
        return False

    all_star_names = [s.name for s in p.major_stars + p.minor_stars]
    return scope_data.mutagen[mutagen_index] in all_star_names


def horoscope_surrounded_has_mutagen(
    astrolabe: Astrolabe,
    horoscope: Horoscope,
    palace_name: str,
    scope: str,
    mutagen: str,
) -> bool:
    """判断运限三方四正是否存在四化"""
    sp = horoscope_surrounded_palaces(astrolabe, horoscope, palace_name, scope)
    if not sp:
        return False
    
    # 检查本宫、对宫、财帛、官禄
    for p_name in [sp.target.name, sp.opposite.name, sp.wealth.name, sp.career.name]:
        if horoscope_has_mutagen(astrolabe, horoscope, p_name, scope, mutagen):
            return True
    return False
