"""
流耀计算
移植自 iztro star/horoscopeStar.ts
"""
from __future__ import annotations
from app.core.constants import HOROSCOPE_STAR_PREFIXES
from app.core.types import Star
from app.core.utils import init_stars
from app.star.location import (
    get_kui_yue_index, get_chang_qu_index_by_heavenly_stem,
    get_lu_yang_tuo_ma_index, get_luan_xi_index, get_nianjie_index,
)


def get_horoscope_star(
    heavenly_stem: str,
    earthly_branch: str,
    scope: str,
) -> list[list[Star]]:
    """
    获取流耀
    魁钺昌曲禄羊陀马鸾喜
    """
    kui_yue = get_kui_yue_index(heavenly_stem)
    chang_qu = get_chang_qu_index_by_heavenly_stem(heavenly_stem)
    lu_yang_tuo_ma = get_lu_yang_tuo_ma_index(heavenly_stem, earthly_branch)
    luan_xi = get_luan_xi_index(earthly_branch)
    stars = init_stars()

    prefix = HOROSCOPE_STAR_PREFIXES.get(scope, HOROSCOPE_STAR_PREFIXES["yearly"])

    if scope == "yearly":
        nj_index = get_nianjie_index(earthly_branch)
        stars[nj_index].append(Star(name="年解", type="helper", scope="yearly"))

    _entries = [
        (kui_yue["kui_index"], prefix["tiankui"], "soft"),
        (kui_yue["yue_index"], prefix["tianyue"], "soft"),
        (chang_qu["chang_index"], prefix["wenchang"], "soft"),
        (chang_qu["qu_index"], prefix["wenqu"], "soft"),
        (lu_yang_tuo_ma["lu_index"], prefix["lucun"], "lucun"),
        (lu_yang_tuo_ma["yang_index"], prefix["qingyang"], "tough"),
        (lu_yang_tuo_ma["tuo_index"], prefix["tuoluo"], "tough"),
        (lu_yang_tuo_ma["ma_index"], prefix["tianma"], "tianma"),
        (luan_xi["hongluan_index"], prefix["hongluan"], "flower"),
        (luan_xi["tianxi_index"], prefix["tianxi"], "flower"),
    ]

    for idx, name, star_type in _entries:
        stars[idx].append(Star(name=name, type=star_type, scope=scope))

    return stars
