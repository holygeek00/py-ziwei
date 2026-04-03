"""
排盘主入口
移植自 iztro astro/astro.ts
"""
from __future__ import annotations
from datetime import datetime
from app.core.constants import (
    EARTHLY_BRANCHES, HEAVENLY_STEMS, CHINESE_TIME, TIME_RANGE,
    EARTHLY_BRANCHES_INFO, TIGER_RULE,
)
from app.core.types import Star, Palace, Decadal, Astrolabe
from app.core.utils import fix_index
from app.core.calendar_utils import (
    get_heavenly_stem_and_earthly_branch, solar_to_lunar,
    lunar_to_solar, get_sign, get_zodiac_by_solar,
)
from app.astro.palace import (
    get_soul_and_body, get_palace_names, get_five_elements_class,
    get_five_elements_class_name, get_horoscope,
)
from app.star.major_star import get_major_star
from app.star.minor_star import get_minor_star
from app.star.adjective_star import get_adjective_star
from app.star.decorative_star import get_changsheng12, get_boshi12, get_yearly12


def by_solar(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    day_divide: str = "forward",
    algorithm: str = "default",
) -> Astrolabe:
    """
    通过阳历获取星盘信息

    :param solar_date: 阳历日期 YYYY-M-D
    :param time_index: 时辰索引 0~12
    :param gender: 性别 男/女
    :param fix_leap: 是否调整闰月
    :param year_divide: normal=正月初一分界, exact=立春分界
    :param horoscope_divide: 运限分界点
    :param day_divide: current=晚子时算当天, forward=算来日
    :param algorithm: default=通行, zhongzhou=中州派
    """
    t_index = time_index
    if day_divide == "current" and t_index >= 12:
        t_index = 0

    gz = get_heavenly_stem_and_earthly_branch(solar_date, t_index, year_divide, horoscope_divide)
    year_branch = gz["yearly"][1]
    year_stem = gz["yearly"][0]

    soul_body = get_soul_and_body(
        solar_date, t_index, fix_leap,
        year_divide=year_divide, horoscope_divide=horoscope_divide,
    )
    soul_index = soul_body["soul_index"]
    body_index = soul_body["body_index"]
    heavenly_stem_of_soul = soul_body["heavenly_stem_of_soul"]
    earthly_branch_of_soul = soul_body["earthly_branch_of_soul"]

    palace_names = get_palace_names(soul_index)

    major_stars = get_major_star(
        solar_date, t_index, fix_leap,
        year_divide=year_divide, day_divide=day_divide,
    )
    minor_stars = get_minor_star(solar_date, t_index, fix_leap, year_divide)
    adjective_stars = get_adjective_star(
        solar_date, t_index, gender, fix_leap,
        year_divide, horoscope_divide, algorithm,
    )
    changsheng12 = get_changsheng12(
        solar_date, t_index, gender, fix_leap,
        year_divide, horoscope_divide,
    )
    boshi12 = get_boshi12(solar_date, gender, year_divide)
    yearly12 = get_yearly12(solar_date, horoscope_divide, algorithm)
    horoscope_data = get_horoscope(
        solar_date, t_index, gender, fix_leap,
        year_divide, horoscope_divide,
    )

    # 五虎遁取寅宫天干
    start_stem = TIGER_RULE[year_stem]
    start_stem_idx = HEAVENLY_STEMS.index(start_stem)
    soul_stem_idx = HEAVENLY_STEMS.index(heavenly_stem_of_soul)

    palaces = []
    for i in range(12):
        h_stem_idx = fix_index(soul_stem_idx - soul_index + i, 10)
        e_branch_idx = fix_index(2 + i)

        h_stem = HEAVENLY_STEMS[h_stem_idx]
        e_branch = EARTHLY_BRANCHES[e_branch_idx]

        # 来因宫判断
        is_original = (
            e_branch not in ["子", "丑"]
            and h_stem == year_stem
        )

        decadal_data = horoscope_data["decadals"][i]
        ages_data = horoscope_data["ages"][i]

        palaces.append(Palace(
            index=i,
            name=palace_names[i],
            is_body_palace=(body_index == i),
            is_original_palace=is_original,
            heavenly_stem=h_stem,
            earthly_branch=e_branch,
            major_stars=major_stars[i],
            minor_stars=minor_stars[i],
            adjective_stars=adjective_stars[i],
            changsheng12=changsheng12[i],
            boshi12=boshi12[i],
            jiangqian12=yearly12["jiangqian12"][i],
            suiqian12=yearly12["suiqian12"][i],
            decadal=Decadal(
                range=decadal_data["range"],
                heavenly_stem=decadal_data["heavenly_stem"],
                earthly_branch=decadal_data["earthly_branch"],
            ) if decadal_data else Decadal(range=[0, 0], heavenly_stem="", earthly_branch=""),
            ages=ages_data if ages_data else [],
        ))

    # 命宫地支
    soul_palace_branch = EARTHLY_BRANCHES[fix_index(soul_index + 2)]
    body_palace_branch = EARTHLY_BRANCHES[fix_index(body_index + 2)]

    # 命主/身主
    if algorithm == "zhongzhou":
        soul_star = EARTHLY_BRANCHES_INFO[year_branch]["soul"]
    else:
        soul_star = EARTHLY_BRANCHES_INFO[soul_palace_branch]["soul"]
    body_star = EARTHLY_BRANCHES_INFO[year_branch]["body"]

    # 五行局
    five_elements = get_five_elements_class_name(heavenly_stem_of_soul, earthly_branch_of_soul)

    # 干支纪年字符串
    chinese_date = (
        f"{gz['yearly'][0]}{gz['yearly'][1]} "
        f"{gz['monthly'][0]}{gz['monthly'][1]} "
        f"{gz['daily'][0]}{gz['daily'][1]} "
        f"{gz['hourly'][0]}{gz['hourly'][1]}"
    )

    # 农历日期
    lunar_info = solar_to_lunar(solar_date)
    lunar_date = f"{lunar_info['lunarYear']}年{'闰' if lunar_info['isLeap'] else ''}{lunar_info['lunarMonth']}月{lunar_info['lunarDay']}日"

    return Astrolabe(
        gender=gender,
        solar_date=solar_date,
        lunar_date=lunar_date,
        chinese_date=chinese_date,
        time=CHINESE_TIME[time_index],
        time_range=TIME_RANGE[time_index],
        sign=get_sign(solar_date),
        zodiac=get_zodiac_by_solar(solar_date, year_divide),
        earthly_branch_of_soul_palace=soul_palace_branch,
        earthly_branch_of_body_palace=body_palace_branch,
        soul=soul_star,
        body=body_star,
        five_elements_class=five_elements,
        palaces=palaces,
    )


def by_lunar(
    lunar_date_str: str,
    time_index: int,
    gender: str,
    is_leap_month: bool = False,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    day_divide: str = "forward",
    algorithm: str = "default",
) -> Astrolabe:
    """通过农历获取星盘信息"""
    solar_date = lunar_to_solar(lunar_date_str, is_leap_month)
    return by_solar(
        solar_date, time_index, gender, fix_leap,
        year_divide, horoscope_divide, day_divide, algorithm,
    )
