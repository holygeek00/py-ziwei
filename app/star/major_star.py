"""
安主星
移植自 iztro star/majorStar.ts
"""
from __future__ import annotations
from app.core.constants import MAJOR_STARS_ZIWEI_GROUP, MAJOR_STARS_TIANFU_GROUP
from app.core.types import Star
from app.core.utils import fix_index, get_brightness, get_mutagen, init_stars
from app.core.calendar_utils import get_heavenly_stem_and_earthly_branch
from app.star.location import get_start_index


def get_major_star(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    year_divide: str = "normal",
    from_stem: str = "",
    from_branch: str = "",
    day_divide: str = "forward",
) -> list[list[Star]]:
    """
    安主星（14颗）

    安紫微诸星诀:
    紫微逆去天机星，隔一太阳武曲辰，
    连接天同空二宫，廉贞居处方是真。

    安天府诸星诀:
    天府顺行有太阴，贪狼而后巨门临，
    随来天相天梁继，七杀空三是破军。
    """
    start = get_start_index(
        solar_date, time_index, fix_leap,
        from_stem=from_stem, from_branch=from_branch,
        day_divide=day_divide,
    )
    ziwei_index = start["ziwei_index"]
    tianfu_index = start["tianfu_index"]

    gz = get_heavenly_stem_and_earthly_branch(solar_date, time_index, year_divide)
    year_stem = gz["yearly"][0]

    stars = init_stars()

    # 安紫微星系（逆时针）
    for i, name in enumerate(MAJOR_STARS_ZIWEI_GROUP):
        if name:
            idx = fix_index(ziwei_index - i)
            stars[idx].append(Star(
                name=name,
                type="major",
                scope="origin",
                brightness=get_brightness(name, idx),
                mutagen=get_mutagen(name, year_stem),
            ))

    # 安天府星系（顺时针）
    for i, name in enumerate(MAJOR_STARS_TIANFU_GROUP):
        if name:
            idx = fix_index(tianfu_index + i)
            stars[idx].append(Star(
                name=name,
                type="major",
                scope="origin",
                brightness=get_brightness(name, idx),
                mutagen=get_mutagen(name, year_stem),
            ))

    return stars
