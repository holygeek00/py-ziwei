"""
安杂耀（约38颗）
移植自 iztro star/adjectiveStar.ts
"""
from __future__ import annotations
from app.core.types import Star
from app.core.utils import init_stars
from app.core.calendar_utils import get_heavenly_stem_and_earthly_branch
from app.star.location import (
    get_yearly_star_index, get_monthly_star_index,
    get_daily_star_index, get_timely_star_index,
    get_luan_xi_index,
)
from app.star.decorative_star import get_yearly12


def get_adjective_star(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    year_divide: str = "normal",
    horoscope_divide: str = "normal",
    algorithm: str = "default",
) -> list[list[Star]]:
    """安杂耀"""
    stars = init_stars()
    gz = get_heavenly_stem_and_earthly_branch(solar_date, time_index, year_divide)
    year_branch = gz["yearly"][1]

    yearly = get_yearly_star_index(
        solar_date, time_index, gender, fix_leap,
        year_divide=year_divide, horoscope_divide=horoscope_divide,
        algorithm=algorithm,
    )
    monthly = get_monthly_star_index(solar_date, time_index, fix_leap)
    daily = get_daily_star_index(solar_date, time_index, fix_leap)
    timely = get_timely_star_index(time_index)
    luan_xi = get_luan_xi_index(year_branch)

    yearly12 = get_yearly12(solar_date, horoscope_divide=horoscope_divide, algorithm=algorithm)
    suiqian12 = yearly12["suiqian12"]

    _s = Star  # alias

    stars[luan_xi["hongluan_index"]].append(_s(name="红鸾", type="flower", scope="origin"))
    stars[luan_xi["tianxi_index"]].append(_s(name="天喜", type="flower", scope="origin"))
    stars[monthly["tianyao_index"]].append(_s(name="天姚", type="flower", scope="origin"))
    stars[yearly["xianchi_index"]].append(_s(name="咸池", type="flower", scope="origin"))
    stars[monthly["yuejie_index"]].append(_s(name="解神", type="helper", scope="origin"))
    stars[daily["santai_index"]].append(_s(name="三台", type="adjective", scope="origin"))
    stars[daily["bazuo_index"]].append(_s(name="八座", type="adjective", scope="origin"))
    stars[daily["enguang_index"]].append(_s(name="恩光", type="adjective", scope="origin"))
    stars[daily["tiangui_index"]].append(_s(name="天贵", type="adjective", scope="origin"))
    stars[yearly["longchi_index"]].append(_s(name="龙池", type="adjective", scope="origin"))
    stars[yearly["fengge_index"]].append(_s(name="凤阁", type="adjective", scope="origin"))
    stars[yearly["tiancai_index"]].append(_s(name="天才", type="adjective", scope="origin"))
    stars[yearly["tianshou_index"]].append(_s(name="天寿", type="adjective", scope="origin"))
    stars[timely["taifu_index"]].append(_s(name="台辅", type="adjective", scope="origin"))
    stars[timely["fenggao_index"]].append(_s(name="封诰", type="adjective", scope="origin"))
    stars[monthly["tianwu_index"]].append(_s(name="天巫", type="adjective", scope="origin"))
    stars[yearly["huagai_index"]].append(_s(name="华盖", type="adjective", scope="origin"))
    stars[yearly["tianguan_index"]].append(_s(name="天官", type="adjective", scope="origin"))
    stars[yearly["tianfu_index"]].append(_s(name="天福", type="adjective", scope="origin"))
    stars[yearly["tianchu_index"]].append(_s(name="天厨", type="adjective", scope="origin"))
    stars[monthly["tianyue_index"]].append(_s(name="天月", type="adjective", scope="origin"))
    stars[yearly["tiande_index"]].append(_s(name="天德", type="adjective", scope="origin"))
    stars[yearly["yuede_index"]].append(_s(name="月德", type="adjective", scope="origin"))
    stars[yearly["tiankong_index"]].append(_s(name="天空", type="adjective", scope="origin"))
    stars[yearly["xunkong_index"]].append(_s(name="旬空", type="adjective", scope="origin"))

    if algorithm != "zhongzhou":
        stars[yearly["jielu_index"]].append(_s(name="截路", type="adjective", scope="origin"))
        stars[yearly["kongwang_index"]].append(_s(name="空亡", type="adjective", scope="origin"))
    else:
        # 找龙德在岁前12神中的位置
        try:
            longde_idx = suiqian12.index("龙德")
            stars[longde_idx].append(_s(name="龙德", type="adjective", scope="origin"))
        except ValueError:
            pass
        stars[yearly["jiekong_index"]].append(_s(name="截空", type="adjective", scope="origin"))
        stars[yearly["jiesha_adj_index"]].append(_s(name="劫杀", type="adjective", scope="origin"))
        stars[yearly["dahao_adj_index"]].append(_s(name="大耗", type="adjective", scope="origin"))

    stars[yearly["guchen_index"]].append(_s(name="孤辰", type="adjective", scope="origin"))
    stars[yearly["guasu_index"]].append(_s(name="寡宿", type="adjective", scope="origin"))
    stars[yearly["feilian_index"]].append(_s(name="蜚廉", type="adjective", scope="origin"))
    stars[yearly["posui_index"]].append(_s(name="破碎", type="adjective", scope="origin"))
    stars[monthly["tianxing_index"]].append(_s(name="天刑", type="adjective", scope="origin"))
    stars[monthly["yinsha_index"]].append(_s(name="阴煞", type="adjective", scope="origin"))
    stars[yearly["tianku_index"]].append(_s(name="天哭", type="adjective", scope="origin"))
    stars[yearly["tianxu_index"]].append(_s(name="天虚", type="adjective", scope="origin"))
    stars[yearly["tianshi_index"]].append(_s(name="天使", type="adjective", scope="origin"))
    stars[yearly["tianshang_index"]].append(_s(name="天伤", type="adjective", scope="origin"))
    stars[yearly["nianjie_index"]].append(_s(name="年解", type="helper", scope="origin"))

    return stars
