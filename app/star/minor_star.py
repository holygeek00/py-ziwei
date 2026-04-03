"""
安辅星（14颗）
移植自 iztro star/minorStar.ts
"""
from __future__ import annotations
from app.core.types import Star
from app.core.utils import fix_lunar_month_index, get_brightness, get_mutagen, init_stars
from app.core.calendar_utils import get_heavenly_stem_and_earthly_branch
from app.star.location import (
    get_zuo_you_index, get_chang_qu_index, get_kui_yue_index,
    get_huo_ling_index, get_kong_jie_index, get_lu_yang_tuo_ma_index,
)


def get_minor_star(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    year_divide: str = "normal",
) -> list[list[Star]]:
    """
    安14辅星:
    左辅, 右弼, 文昌, 文曲, 天魁, 天钺,
    禄存, 天马, 地空, 地劫, 火星, 铃星, 擎羊, 陀罗
    """
    stars = init_stars()
    gz = get_heavenly_stem_and_earthly_branch(solar_date, time_index, year_divide)
    year_stem = gz["yearly"][0]
    year_branch = gz["yearly"][1]
    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)

    zuo_you = get_zuo_you_index(month_index + 1)
    chang_qu = get_chang_qu_index(time_index)
    kui_yue = get_kui_yue_index(year_stem)
    huo_ling = get_huo_ling_index(year_branch, time_index)
    kong_jie = get_kong_jie_index(time_index)
    lu_yang_tuo_ma = get_lu_yang_tuo_ma_index(year_stem, year_branch)

    _add = [
        (zuo_you["zuo_index"], "左辅", "soft", True),
        (zuo_you["you_index"], "右弼", "soft", True),
        (chang_qu["chang_index"], "文昌", "soft", True),
        (chang_qu["qu_index"], "文曲", "soft", True),
        (kui_yue["kui_index"], "天魁", "soft", False),
        (kui_yue["yue_index"], "天钺", "soft", False),
        (lu_yang_tuo_ma["lu_index"], "禄存", "lucun", False),
        (lu_yang_tuo_ma["ma_index"], "天马", "tianma", False),
        (kong_jie["kong_index"], "地空", "tough", False),
        (kong_jie["jie_index"], "地劫", "tough", False),
        (huo_ling["huo_index"], "火星", "tough", False),
        (huo_ling["ling_index"], "铃星", "tough", False),
        (lu_yang_tuo_ma["yang_index"], "擎羊", "tough", False),
        (lu_yang_tuo_ma["tuo_index"], "陀罗", "tough", False),
    ]

    for idx, name, star_type, has_mutagen in _add:
        stars[idx].append(Star(
            name=name,
            type=star_type,
            scope="origin",
            brightness=get_brightness(name, idx),
            mutagen=get_mutagen(name, year_stem) if has_mutagen else "",
        ))

    return stars
