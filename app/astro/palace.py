"""
命宫身宫、五行局、宫名、大限计算
移植自 iztro astro/palace.ts
"""
from __future__ import annotations
from app.core.constants import (
    EARTHLY_BRANCHES, HEAVENLY_STEMS, PALACES, TIGER_RULE,
    EARTHLY_BRANCHES_INFO, FIVE_ELEMENTS_TABLE,
    FIVE_ELEMENTS_CLASS_NAMES, FiveElementsClass,
)
from app.core.utils import (
    fix_index, fix_earthly_branch_index, fix_lunar_month_index, get_age_index,
)
from app.core.calendar_utils import get_heavenly_stem_and_earthly_branch


def get_soul_and_body(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    from_stem: str = "",
    from_branch: str = "",
) -> dict:
    """
    获取命宫/身宫数据

    定寅首 + 安命身宫诀:
    寅起正月，顺数至生月，逆数生时为命宫。
    寅起正月，顺数至生月，顺数生时为身宫。
    """
    gz = get_heavenly_stem_and_earthly_branch(
        solar_date, time_index, year_divide, horoscope_divide,
    )
    hour_branch = gz["hourly"][1]
    year_stem = gz["yearly"][0]

    hour_branch_idx = EARTHLY_BRANCHES.index(hour_branch)
    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)

    # 命宫索引
    soul_index = fix_index(month_index - hour_branch_idx)
    # 身宫索引
    body_index = fix_index(month_index + hour_branch_idx)

    if from_stem and from_branch:
        soul_index = fix_earthly_branch_index(from_branch)
        body_offset = [0, 2, 4, 6, 8, 10, 0, 2, 4, 6, 8, 10, 0]
        body_index = fix_index(body_offset[time_index] + soul_index)

    # 五虎遁取寅宫天干
    start_heavenly_stem = TIGER_RULE[year_stem]
    start_stem_idx = HEAVENLY_STEMS.index(start_heavenly_stem)

    # 命宫天干
    soul_stem_idx = fix_index(start_stem_idx + soul_index, 10)
    heavenly_stem_of_soul = HEAVENLY_STEMS[soul_stem_idx]

    # 命宫地支 (寅宫索引为2)
    first_index = EARTHLY_BRANCHES.index("寅")
    earthly_branch_of_soul = EARTHLY_BRANCHES[fix_index(soul_index + first_index)]

    return {
        "soul_index": soul_index,
        "body_index": body_index,
        "heavenly_stem_of_soul": heavenly_stem_of_soul,
        "earthly_branch_of_soul": earthly_branch_of_soul,
    }


def get_five_elements_class(heavenly_stem: str, earthly_branch: str) -> int:
    """
    定五行局法（纳音五行）

    干支相加多减五，五行木金水火土
    天干取数: 甲乙->1, 丙丁->2, 戊己->3, 庚辛->4, 壬癸->5
    地支取数: 子午丑未->1, 寅申卯酉->2, 辰戌巳亥->3

    :return: 五行局数值 (2/3/4/5/6)
    """
    stem_idx = HEAVENLY_STEMS.index(heavenly_stem)
    branch_idx = EARTHLY_BRANCHES.index(earthly_branch)

    stem_number = stem_idx // 2 + 1
    branch_number = fix_index(branch_idx, 6) // 2 + 1
    total = stem_number + branch_number

    while total > 5:
        total -= 5

    return FIVE_ELEMENTS_TABLE[total - 1]


def get_five_elements_class_name(heavenly_stem: str, earthly_branch: str) -> str:
    """获取五行局名称"""
    value = get_five_elements_class(heavenly_stem, earthly_branch)
    return FIVE_ELEMENTS_CLASS_NAMES.get(value, "水二局")


def get_palace_names(from_index: int) -> list[str]:
    """
    获取从寅宫开始的各个宫名

    :param from_index: 命宫索引
    """
    names = [""] * 12
    for i in range(12):
        idx = fix_index(i - from_index)
        names[i] = PALACES[idx]
    return names


def get_horoscope(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    from_stem: str = "",
    from_branch: str = "",
) -> dict:
    """
    起大限 + 小限

    大限由命宫起，阳男阴女顺行；阴男阳女逆行，每十年过一宫限。
    """
    gz = get_heavenly_stem_and_earthly_branch(solar_date, time_index, year_divide)
    year_stem = gz["yearly"][0]
    year_branch = gz["yearly"][1]

    soul_body = get_soul_and_body(
        solar_date, time_index, fix_leap,
        year_divide=year_divide, horoscope_divide=horoscope_divide,
        from_stem=from_stem, from_branch=from_branch,
    )
    soul_index = soul_body["soul_index"]

    if from_stem and from_branch:
        fe_value = get_five_elements_class(from_stem, from_branch)
    else:
        fe_value = get_five_elements_class(
            soul_body["heavenly_stem_of_soul"],
            soul_body["earthly_branch_of_soul"],
        )

    gender_yinyang = "阳" if gender == "男" else "阴"
    year_branch_yinyang = EARTHLY_BRANCHES_INFO[year_branch]["yinYang"]

    start_heavenly_stem = TIGER_RULE[year_stem]
    start_stem_idx = HEAVENLY_STEMS.index(start_heavenly_stem)
    yin_idx = EARTHLY_BRANCHES.index("寅")

    decadals = [None] * 12
    for i in range(12):
        if gender_yinyang == year_branch_yinyang:
            idx = fix_index(soul_index + i)
        else:
            idx = fix_index(soul_index - i)

        start_age = fe_value + 10 * i
        h_stem_idx = fix_index(start_stem_idx + idx, 10)
        e_branch_idx = fix_index(yin_idx + idx)

        decadals[idx] = {
            "range": [start_age, start_age + 9],
            "heavenly_stem": HEAVENLY_STEMS[h_stem_idx],
            "earthly_branch": EARTHLY_BRANCHES[e_branch_idx],
        }

    # 小限
    age_idx = get_age_index(year_branch)
    ages = [None] * 12
    for i in range(12):
        age_list = []
        for j in range(10):
            age_list.append(12 * j + i + 1)

        if gender == "男":
            target_idx = fix_index(age_idx + i)
        else:
            target_idx = fix_index(age_idx - i)
        ages[target_idx] = age_list

    return {"decadals": decadals, "ages": ages}
