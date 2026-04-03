"""
星耀宫位计算
移植自 iztro star/location.ts
"""
from __future__ import annotations
from app.core.constants import (
    EARTHLY_BRANCHES, HEAVENLY_STEMS, PALACES,
    LU_INDEX_BY_STEM, KUI_YUE_BY_STEM, MA_INDEX_BY_BRANCH,
    HUO_LING_START, HUAGAI_XIANCHI, GU_GUA,
    JIANGQIAN_START, TIANCHU_BY_STEM, POSUI_BY_BRANCH,
    FEILIAN_BY_BRANCH, TIANGUAN_BY_STEM, TIANFU_ADJ_BY_STEM,
    TIANYUE_BY_MONTH, TIANWU_BY_MONTH, YINSHA_BY_MONTH,
    JIELU_BY_STEM, KONGWANG_BY_STEM, NIANJIE_BY_BRANCH,
    DAHAO_ADJ_BY_BRANCH, JIESHA_ADJ, CHANGQU_BY_STEM,
    YUEJIE_BY_MONTH, FiveElementsClass,
)
from app.core.utils import fix_index, fix_earthly_branch_index, fix_lunar_month_index, fix_lunar_day_index
from app.core.calendar_utils import solar_to_lunar, get_lunar_month_days, get_heavenly_stem_and_earthly_branch


def get_start_index(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    five_elements_value: int = 0,
    heavenly_stem_of_soul: str = "",
    earthly_branch_of_soul: str = "",
    from_stem: str = "",
    from_branch: str = "",
    day_divide: str = "forward",
) -> dict:
    """
    起紫微星诀算法

    六五四三二，酉午亥辰丑，
    局数除日数，商数宫前走；
    若见数无余，便要起虎口，
    日数小於局，还直宫中守。

    :return: {"ziwei_index": int, "tianfu_index": int}
    """
    from app.astro.palace import get_soul_and_body, get_five_elements_class

    if not five_elements_value:
        if from_stem and from_branch:
            base_stem = from_stem
            base_branch = from_branch
        else:
            soul_body = get_soul_and_body(solar_date, time_index, fix_leap)
            base_stem = soul_body["heavenly_stem_of_soul"]
            base_branch = soul_body["earthly_branch_of_soul"]
        five_elements_value = get_five_elements_class(base_stem, base_branch)

    info = solar_to_lunar(solar_date)
    lunar_day = info["lunarDay"]

    max_days = get_lunar_month_days(solar_date)

    _day = lunar_day
    if time_index == 12 and day_divide != "current":
        _day = lunar_day + 1

    if _day > max_days:
        _day -= max_days

    remainder = -1
    offset = -1

    while remainder != 0:
        offset += 1
        divisor = _day + offset
        quotient = divisor // five_elements_value
        remainder = divisor % five_elements_value

    quotient = quotient % 12
    ziwei_index = quotient - 1

    if offset % 2 == 0:
        ziwei_index += offset
    else:
        ziwei_index -= offset

    ziwei_index = fix_index(ziwei_index)
    tianfu_index = fix_index(12 - ziwei_index)

    return {"ziwei_index": ziwei_index, "tianfu_index": tianfu_index}


def get_lu_yang_tuo_ma_index(heavenly_stem: str, earthly_branch: str) -> dict:
    """
    按年干支计算禄存、擎羊、陀罗、天马的索引
    """
    lu_branch = LU_INDEX_BY_STEM.get(heavenly_stem, "寅")
    lu_index = fix_earthly_branch_index(lu_branch)
    ma_branch = MA_INDEX_BY_BRANCH.get(earthly_branch, "寅")
    ma_index = fix_earthly_branch_index(ma_branch)

    return {
        "lu_index": lu_index,
        "ma_index": ma_index,
        "yang_index": fix_index(lu_index + 1),
        "tuo_index": fix_index(lu_index - 1),
    }


def get_kui_yue_index(heavenly_stem: str) -> dict:
    """天魁天钺索引（按年干）"""
    kui_branch, yue_branch = KUI_YUE_BY_STEM.get(heavenly_stem, ("丑", "未"))
    return {
        "kui_index": fix_earthly_branch_index(kui_branch),
        "yue_index": fix_earthly_branch_index(yue_branch),
    }


def get_zuo_you_index(lunar_month: int) -> dict:
    """
    左辅右弼索引（按生月）
    辰上顺正寻左辅, 戌上逆正右弼当
    """
    zuo_index = fix_index(fix_earthly_branch_index("辰") + (lunar_month - 1))
    you_index = fix_index(fix_earthly_branch_index("戌") - (lunar_month - 1))
    return {"zuo_index": zuo_index, "you_index": you_index}


def get_chang_qu_index(time_index: int) -> dict:
    """
    文昌文曲索引（按时支）
    辰上顺时文曲位, 戌上逆时觅文昌
    """
    fixed_time = fix_index(time_index)
    chang_index = fix_index(fix_earthly_branch_index("戌") - fixed_time)
    qu_index = fix_index(fix_earthly_branch_index("辰") + fixed_time)
    return {"chang_index": chang_index, "qu_index": qu_index}


def get_kong_jie_index(time_index: int) -> dict:
    """
    地空地劫索引（按时支）
    亥上子时顺安劫, 逆回便是地空亡
    """
    fixed_time = fix_index(time_index)
    hai_index = fix_earthly_branch_index("亥")
    kong_index = fix_index(hai_index - fixed_time)
    jie_index = fix_index(hai_index + fixed_time)
    return {"kong_index": kong_index, "jie_index": jie_index}


def get_huo_ling_index(earthly_branch: str, time_index: int) -> dict:
    """火星铃星索引（按年支及时支）"""
    fixed_time = fix_index(time_index)
    huo_start, ling_start = HUO_LING_START.get(earthly_branch, ("寅", "戌"))
    huo_index = fix_index(fix_earthly_branch_index(huo_start) + fixed_time)
    ling_index = fix_index(fix_earthly_branch_index(ling_start) + fixed_time)
    return {"huo_index": huo_index, "ling_index": ling_index}


def get_luan_xi_index(earthly_branch: str) -> dict:
    """
    红鸾天喜索引（按年支）
    卯上起子逆数之
    """
    branch_idx = EARTHLY_BRANCHES.index(earthly_branch)
    hongluan_index = fix_index(fix_earthly_branch_index("卯") - branch_idx)
    tianxi_index = fix_index(hongluan_index + 6)
    return {"hongluan_index": hongluan_index, "tianxi_index": tianxi_index}


def get_huagai_xianchi_index(earthly_branch: str) -> dict:
    """华盖咸池索引"""
    hg, xc = HUAGAI_XIANCHI.get(earthly_branch, ("辰", "酉"))
    return {
        "huagai_index": fix_index(fix_earthly_branch_index(hg)),
        "xianchi_index": fix_index(fix_earthly_branch_index(xc)),
    }


def get_gu_gua_index(earthly_branch: str) -> dict:
    """孤辰寡宿索引"""
    gu, gua = GU_GUA.get(earthly_branch, ("巳", "丑"))
    return {
        "guchen_index": fix_index(fix_earthly_branch_index(gu)),
        "guasu_index": fix_index(fix_earthly_branch_index(gua)),
    }


def get_daily_star_index(solar_date: str, time_index: int, fix_leap: bool = True) -> dict:
    """三台、八座、恩光、天贵索引"""
    info = solar_to_lunar(solar_date)
    lunar_day = info["lunarDay"]
    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)

    zuo_you = get_zuo_you_index(month_index + 1)
    chang_qu = get_chang_qu_index(time_index)
    day_index = fix_lunar_day_index(lunar_day, time_index)

    santai_index = fix_index((zuo_you["zuo_index"] + day_index) % 12)
    bazuo_index = fix_index((zuo_you["you_index"] - day_index) % 12)
    enguang_index = fix_index(((chang_qu["chang_index"] + day_index) % 12) - 1)
    tiangui_index = fix_index(((chang_qu["qu_index"] + day_index) % 12) - 1)

    return {
        "santai_index": santai_index,
        "bazuo_index": bazuo_index,
        "enguang_index": enguang_index,
        "tiangui_index": tiangui_index,
    }


def get_timely_star_index(time_index: int) -> dict:
    """台辅、封诰索引"""
    fixed_time = fix_index(time_index)
    taifu_index = fix_index(fix_earthly_branch_index("午") + fixed_time)
    fenggao_index = fix_index(fix_earthly_branch_index("寅") + fixed_time)
    return {"taifu_index": taifu_index, "fenggao_index": fenggao_index}


def get_monthly_star_index(solar_date: str, time_index: int, fix_leap: bool = True) -> dict:
    """
    月系星耀索引: 月解、天姚、天刑、阴煞、天月、天巫
    """
    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)

    yuejie_index = fix_index(fix_earthly_branch_index(YUEJIE_BY_MONTH[month_index // 2]))
    tianyao_index = fix_index(fix_earthly_branch_index("丑") + month_index)
    tianxing_index = fix_index(fix_earthly_branch_index("酉") + month_index)
    yinsha_index = fix_index(fix_earthly_branch_index(YINSHA_BY_MONTH[month_index % 6]))
    tianyue_index = fix_index(fix_earthly_branch_index(TIANYUE_BY_MONTH[month_index]))
    tianwu_index = fix_index(fix_earthly_branch_index(TIANWU_BY_MONTH[month_index % 4]))

    return {
        "yuejie_index": yuejie_index,
        "tianyao_index": tianyao_index,
        "tianxing_index": tianxing_index,
        "yinsha_index": yinsha_index,
        "tianyue_index": tianyue_index,
        "tianwu_index": tianwu_index,
    }


def get_tianshi_tianshang_index(
    gender: str,
    earthly_branch: str,
    soul_index: int,
    algorithm: str = "default",
) -> dict:
    """天使天伤索引"""
    yinyang = EARTHLY_BRANCHES.index(earthly_branch) % 2
    gender_list = ["男", "女"]
    gender_idx = 0 if gender == "男" else 1
    same_yinyang = (yinyang == gender_idx)

    tianshang_index = fix_index(PALACES.index("仆役") + soul_index)
    tianshi_index = fix_index(PALACES.index("疾厄") + soul_index)

    if algorithm == "zhongzhou" and not same_yinyang:
        tianshi_index, tianshang_index = tianshang_index, tianshi_index

    return {"tianshi_index": tianshi_index, "tianshang_index": tianshang_index}


def get_jiesha_adj_index(earthly_branch: str) -> int:
    """劫杀（杂耀）索引"""
    return JIESHA_ADJ.get(earthly_branch, 0)


def get_dahao_index(earthly_branch: str) -> int:
    """大耗（杂耀）索引"""
    branch_idx = EARTHLY_BRANCHES.index(earthly_branch)
    matched = DAHAO_ADJ_BY_BRANCH[branch_idx]
    return fix_index(EARTHLY_BRANCHES.index(matched) - 2)


def get_nianjie_index(earthly_branch: str) -> int:
    """年解索引"""
    branch_idx = EARTHLY_BRANCHES.index(earthly_branch)
    target = NIANJIE_BY_BRANCH[branch_idx]
    return fix_index(fix_earthly_branch_index(target))


def get_yearly_star_index(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    algorithm: str = "default",
) -> dict:
    """
    年系星耀索引
    包括: 咸池, 华盖, 孤辰, 寡宿, 天才, 天寿, 天厨, 破碎, 蜚廉,
          龙池, 凤阁, 天哭, 天虚, 天官, 天福, 天德, 月德,
          天空, 截路, 空亡, 旬空, 天使, 天伤, 截空, 劫杀, 年解, 大耗
    """
    from app.astro.palace import get_soul_and_body

    gz = get_heavenly_stem_and_earthly_branch(solar_date, time_index, horoscope_divide, horoscope_divide)
    soul_body = get_soul_and_body(solar_date, time_index, fix_leap, year_divide=year_divide, horoscope_divide=horoscope_divide)
    soul_index = soul_body["soul_index"]
    body_index = soul_body["body_index"]

    heavenly_stem = gz["yearly"][0]
    earthly_branch = gz["yearly"][1]
    stem_idx = HEAVENLY_STEMS.index(heavenly_stem)
    branch_idx = EARTHLY_BRANCHES.index(earthly_branch)

    hg_xc = get_huagai_xianchi_index(earthly_branch)
    gu_gua = get_gu_gua_index(earthly_branch)

    tiancai_index = fix_index(soul_index + branch_idx)
    tianshou_index = fix_index(body_index + branch_idx)

    tianchu_index = fix_index(fix_earthly_branch_index(TIANCHU_BY_STEM[stem_idx]))
    posui_index = fix_index(fix_earthly_branch_index(POSUI_BY_BRANCH[branch_idx % 3]))
    feilian_index = fix_index(fix_earthly_branch_index(FEILIAN_BY_BRANCH[branch_idx]))

    longchi_index = fix_index(fix_earthly_branch_index("辰") + branch_idx)
    fengge_index = fix_index(fix_earthly_branch_index("戌") - branch_idx)
    tianku_index = fix_index(fix_earthly_branch_index("午") - branch_idx)
    tianxu_index = fix_index(fix_earthly_branch_index("午") + branch_idx)

    tianguan_index = fix_index(fix_earthly_branch_index(TIANGUAN_BY_STEM[stem_idx]))
    tianfu_index = fix_index(fix_earthly_branch_index(TIANFU_ADJ_BY_STEM[stem_idx]))

    tiande_index = fix_index(fix_earthly_branch_index("酉") + branch_idx)
    yuede_index = fix_index(fix_earthly_branch_index("巳") + branch_idx)

    tiankong_index = fix_index(fix_earthly_branch_index(earthly_branch) + 1)

    jielu_index = fix_index(fix_earthly_branch_index(JIELU_BY_STEM[stem_idx % 5]))
    kongwang_index = fix_index(fix_earthly_branch_index(KONGWANG_BY_STEM[stem_idx % 5]))

    gui_idx = HEAVENLY_STEMS.index("癸")
    xunkong_index = fix_index(
        fix_earthly_branch_index(earthly_branch) + gui_idx - stem_idx + 1
    )
    # 旬空需判断阴阳
    yinyang = branch_idx % 2
    if yinyang != xunkong_index % 2:
        xunkong_index = fix_index(xunkong_index + 1)

    # 中州派截空
    jiekong_index = jielu_index if yinyang == 0 else kongwang_index

    jiesha_adj_index = get_jiesha_adj_index(earthly_branch)
    nianjie_index_val = get_nianjie_index(earthly_branch)
    dahao_adj_index = get_dahao_index(earthly_branch)

    ts = get_tianshi_tianshang_index(gender, earthly_branch, soul_index, algorithm)

    return {
        "xianchi_index": hg_xc["xianchi_index"],
        "huagai_index": hg_xc["huagai_index"],
        "guchen_index": gu_gua["guchen_index"],
        "guasu_index": gu_gua["guasu_index"],
        "tiancai_index": tiancai_index,
        "tianshou_index": tianshou_index,
        "tianchu_index": tianchu_index,
        "posui_index": posui_index,
        "feilian_index": feilian_index,
        "longchi_index": longchi_index,
        "fengge_index": fengge_index,
        "tianku_index": tianku_index,
        "tianxu_index": tianxu_index,
        "tianguan_index": tianguan_index,
        "tianfu_index": tianfu_index,
        "tiande_index": tiande_index,
        "yuede_index": yuede_index,
        "tiankong_index": tiankong_index,
        "jielu_index": jielu_index,
        "kongwang_index": kongwang_index,
        "xunkong_index": xunkong_index,
        "tianshang_index": ts["tianshang_index"],
        "tianshi_index": ts["tianshi_index"],
        "jiekong_index": jiekong_index,
        "jiesha_adj_index": jiesha_adj_index,
        "nianjie_index": nianjie_index_val,
        "dahao_adj_index": dahao_adj_index,
    }


def get_chang_qu_index_by_heavenly_stem(heavenly_stem: str) -> dict:
    """
    流昌流曲（按天干，用于大限/流年流耀）
    """
    chang_branch, qu_branch = CHANGQU_BY_STEM.get(heavenly_stem, ("巳", "酉"))
    return {
        "chang_index": fix_index(fix_earthly_branch_index(chang_branch)),
        "qu_index": fix_index(fix_earthly_branch_index(qu_branch)),
    }
