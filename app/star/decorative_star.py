"""
长生12神, 博士12神, 流年将前/岁前诸星
移植自 iztro star/decorativeStar.ts
"""
from __future__ import annotations
from app.core.constants import (
    EARTHLY_BRANCHES, EARTHLY_BRANCHES_INFO,
    CHANGSHENG_12, BOSHI_12, CHANGSHENG_START,
    SUIQIAN_12_DEFAULT, SUIQIAN_12_ZHONGZHOU, JIANGQIAN_12,
    JIANGQIAN_START, FiveElementsClass, FIVE_ELEMENTS_CLASS_NAMES,
)
from app.core.utils import fix_index, fix_earthly_branch_index
from app.core.calendar_utils import get_heavenly_stem_and_earthly_branch
from app.star.location import get_lu_yang_tuo_ma_index


def _get_changsheng12_start_index(five_elements_value: int) -> int:
    """长生12神起始宫位"""
    branch = CHANGSHENG_START.get(five_elements_value, "申")
    return fix_earthly_branch_index(branch)


def get_changsheng12(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    from_stem: str = "",
    from_branch: str = "",
) -> list[str]:
    """
    长生12神
    阳男阴女顺行，阴男阳女逆行
    """
    from app.astro.palace import get_soul_and_body, get_five_elements_class

    gz = get_heavenly_stem_and_earthly_branch(solar_date, 0, year_divide)
    year_branch = gz["yearly"][1]
    year_branch_yinyang = EARTHLY_BRANCHES_INFO[year_branch]["yinYang"]

    if from_stem and from_branch:
        h_stem = from_stem
        e_branch = from_branch
    else:
        soul_body = get_soul_and_body(solar_date, time_index, fix_leap, year_divide=year_divide, horoscope_divide=horoscope_divide)
        h_stem = soul_body["heavenly_stem_of_soul"]
        e_branch = soul_body["earthly_branch_of_soul"]

    five_elements_value = get_five_elements_class(h_stem, e_branch)
    start_idx = _get_changsheng12_start_index(five_elements_value)

    gender_yinyang = "阳" if gender == "男" else "阴"
    is_forward = (gender_yinyang == year_branch_yinyang)

    changsheng12: list[str] = [""] * 12
    for i, star_name in enumerate(CHANGSHENG_12):
        if is_forward:
            idx = fix_index(i + start_idx)
        else:
            idx = fix_index(start_idx - i)
        changsheng12[idx] = star_name

    return changsheng12


def get_boshi12(
    solar_date: str,
    gender: str,
    year_divide: str = "normal",
) -> list[str]:
    """
    博士12神
    从禄存起，阳男阴女顺行，阴男阳女逆行
    """
    gz = get_heavenly_stem_and_earthly_branch(solar_date, 0, year_divide)
    year_stem = gz["yearly"][0]
    year_branch = gz["yearly"][1]
    year_branch_yinyang = EARTHLY_BRANCHES_INFO[year_branch]["yinYang"]

    gender_yinyang = "阳" if gender == "男" else "阴"
    is_forward = (gender_yinyang == year_branch_yinyang)

    lu_info = get_lu_yang_tuo_ma_index(year_stem, year_branch)
    lu_index = lu_info["lu_index"]

    boshi12: list[str] = [""] * 12
    for i, star_name in enumerate(BOSHI_12):
        if is_forward:
            idx = fix_index(lu_index + i)
        else:
            idx = fix_index(lu_index - i)
        boshi12[idx] = star_name

    return boshi12


def _get_jiangqian12_start_index(earthly_branch: str) -> int:
    """将前12起始索引"""
    start = JIANGQIAN_START.get(earthly_branch, "午")
    return fix_index(fix_earthly_branch_index(start))


def get_yearly12(
    solar_date: str,
    horoscope_divide: str = "normal",
    algorithm: str = "default",
) -> dict:
    """
    流年岁前诸星 + 将前诸星
    """
    gz = get_heavenly_stem_and_earthly_branch(solar_date, 0, horoscope_divide, horoscope_divide)
    year_branch = gz["yearly"][1]

    ts12 = SUIQIAN_12_ZHONGZHOU if algorithm == "zhongzhou" else SUIQIAN_12_DEFAULT

    suiqian12: list[str] = [""] * 12
    for i, star_name in enumerate(ts12):
        idx = fix_index(fix_earthly_branch_index(year_branch) + i)
        suiqian12[idx] = star_name

    jiangqian12: list[str] = [""] * 12
    jq_start = _get_jiangqian12_start_index(year_branch)
    for i, star_name in enumerate(JIANGQIAN_12):
        idx = fix_index(jq_start + i)
        jiangqian12[idx] = star_name

    return {"suiqian12": suiqian12, "jiangqian12": jiangqian12}
