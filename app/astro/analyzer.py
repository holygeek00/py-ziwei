"""
分析器 — 宫位查询、三方四正、星耀判断、四化飞星
移植自 iztro astro/analyzer.ts, FunctionalPalace.ts, FunctionalSurpalaces.ts, FunctionalStar.ts
"""
from __future__ import annotations
from typing import Optional
from app.core.constants import MUTAGEN, HEAVENLY_STEMS_INFO
from app.core.types import Palace, Star, Astrolabe
from app.core.utils import fix_index, fix_earthly_branch_index


# ============================================================
# 宫位查询
# ============================================================

def get_palace(astrolabe: Astrolabe, index_or_name: int | str) -> Optional[Palace]:
    """获取星盘的某个宫位（按索引或名称）"""
    if isinstance(index_or_name, int):
        if 0 <= index_or_name <= 11:
            return astrolabe.palaces[index_or_name]
        return None
    # 按名称查找
    for p in astrolabe.palaces:
        if p.name == index_or_name:
            return p
        if index_or_name == "身宫" and p.is_body_palace:
            return p
        if index_or_name == "来因" and p.is_original_palace:
            return p
    return None


# ============================================================
# 三方四正
# ============================================================

class SurroundedPalaces:
    """三方四正宫位"""
    def __init__(self, target: Palace, opposite: Palace, wealth: Palace, career: Palace):
        self.target = target      # 本宫
        self.opposite = opposite  # 对宫
        self.wealth = wealth      # 财帛位
        self.career = career      # 官禄位

    def have(self, stars: list[str]) -> bool:
        """三方四正是否全部包含这些星耀"""
        all_star_names = self._all_star_names()
        return all(s in all_star_names for s in stars)

    def not_have(self, stars: list[str]) -> bool:
        """三方四正是否全部不含这些星耀"""
        all_star_names = self._all_star_names()
        return all(s not in all_star_names for s in stars)

    def have_one_of(self, stars: list[str]) -> bool:
        """三方四正是否包含其中一颗"""
        all_star_names = self._all_star_names()
        return any(s in all_star_names for s in stars)

    def have_mutagen(self, mutagen: str) -> bool:
        """三方四正是否有四化"""
        return (
            palace_has_mutagen(self.target, mutagen)
            or palace_has_mutagen(self.opposite, mutagen)
            or palace_has_mutagen(self.wealth, mutagen)
            or palace_has_mutagen(self.career, mutagen)
        )

    def not_have_mutagen(self, mutagen: str) -> bool:
        return not self.have_mutagen(mutagen)

    def _all_star_names(self) -> list[str]:
        result = []
        for p in [self.target, self.opposite, self.wealth, self.career]:
            for s in p.major_stars + p.minor_stars + p.adjective_stars:
                result.append(s.name)
        return result


def get_surrounded_palaces(astrolabe: Astrolabe, index_or_name: int | str) -> SurroundedPalaces:
    """获取三方四正宫位"""
    palace = get_palace(astrolabe, index_or_name)
    if not palace:
        raise ValueError(f"宫位 {index_or_name} 不存在")

    palace_index = fix_earthly_branch_index(palace.earthly_branch)
    opposite = get_palace(astrolabe, fix_index(palace_index + 6))
    career = get_palace(astrolabe, fix_index(palace_index + 4))
    wealth = get_palace(astrolabe, fix_index(palace_index + 8))

    if not opposite or not career or not wealth:
        raise ValueError(f"宫位 {index_or_name} 三方四正计算异常")

    return SurroundedPalaces(
        target=palace, opposite=opposite, wealth=wealth, career=career,
    )


# ============================================================
# 宫位星耀判断
# ============================================================

def _all_stars_in_palace(palace: Palace) -> list[str]:
    """获取宫位内所有星耀名称"""
    return [s.name for s in palace.major_stars + palace.minor_stars + palace.adjective_stars]


def palace_has_stars(palace: Palace, stars: list[str]) -> bool:
    """宫位是否全部包含这些星耀"""
    all_names = _all_stars_in_palace(palace)
    return all(s in all_names for s in stars)


def palace_not_have_stars(palace: Palace, stars: list[str]) -> bool:
    """宫位是否全部不含这些星耀"""
    all_names = _all_stars_in_palace(palace)
    return all(s not in all_names for s in stars)


def palace_has_one_of_stars(palace: Palace, stars: list[str]) -> bool:
    """宫位是否包含其中一颗"""
    all_names = _all_stars_in_palace(palace)
    return any(s in all_names for s in stars)


def palace_has_mutagen(palace: Palace, mutagen: str) -> bool:
    """宫位内是否有某个四化"""
    for s in palace.major_stars + palace.minor_stars:
        if s.mutagen == mutagen:
            return True
    return False


def palace_not_have_mutagen(palace: Palace, mutagen: str) -> bool:
    return not palace_has_mutagen(palace, mutagen)


def palace_is_empty(palace: Palace, exclude_stars: list[str] | None = None) -> bool:
    """判断是否为空宫（没有主星）"""
    major_count = len([s for s in palace.major_stars if s.type == "major"])
    if major_count > 0:
        return False
    if exclude_stars:
        all_names = _all_stars_in_palace(palace)
        if any(s in all_names for s in exclude_stars):
            return False
    return True


# ============================================================
# 四化飞星
# ============================================================

def mutagens_to_stars(heavenly_stem: str, mutagens: str | list[str]) -> list[str]:
    """根据天干和四化名获取对应的星耀名"""
    if isinstance(mutagens, str):
        mutagens = [mutagens]
    stem_info = HEAVENLY_STEMS_INFO.get(heavenly_stem)
    if not stem_info:
        return []
    mutagen_stars = stem_info.get("mutagen", [])
    result = []
    for m in mutagens:
        if m in MUTAGEN:
            idx = MUTAGEN.index(m)
            if idx < len(mutagen_stars):
                result.append(mutagen_stars[idx])
    return result


def palace_flies_to(
    astrolabe: Astrolabe,
    from_palace: Palace,
    to_index_or_name: int | str,
    with_mutagens: str | list[str],
) -> bool:
    """判断宫位是否飞化到目标宫位"""
    to_palace = get_palace(astrolabe, to_index_or_name)
    if not to_palace:
        return False
    stars = mutagens_to_stars(from_palace.heavenly_stem, with_mutagens)
    if not stars:
        return False
    return palace_has_stars(to_palace, stars)


def palace_flies_one_of_to(
    astrolabe: Astrolabe,
    from_palace: Palace,
    to_index_or_name: int | str,
    with_mutagens: list[str],
) -> bool:
    """判断宫位飞化其中一颗到目标宫位"""
    to_palace = get_palace(astrolabe, to_index_or_name)
    if not to_palace:
        return False
    stars = mutagens_to_stars(from_palace.heavenly_stem, with_mutagens)
    if not stars:
        return True
    return palace_has_one_of_stars(to_palace, stars)


def palace_not_fly_to(
    astrolabe: Astrolabe,
    from_palace: Palace,
    to_index_or_name: int | str,
    with_mutagens: str | list[str],
) -> bool:
    """判断宫位是否没有飞化到目标宫位"""
    to_palace = get_palace(astrolabe, to_index_or_name)
    if not to_palace:
        return False
    stars = mutagens_to_stars(from_palace.heavenly_stem, with_mutagens)
    if not stars:
        return True
    return palace_not_have_stars(to_palace, stars)


def palace_self_mutaged(palace: Palace, with_mutagens: str | list[str]) -> bool:
    """判断宫位是否有自化"""
    stars = mutagens_to_stars(palace.heavenly_stem, with_mutagens)
    return palace_has_stars(palace, stars)


def palace_self_mutaged_one_of(palace: Palace, with_mutagens: list[str] | None = None) -> bool:
    """判断宫位是否有自化（任意一颗）"""
    muts = with_mutagens or ["禄", "权", "科", "忌"]
    stars = mutagens_to_stars(palace.heavenly_stem, muts)
    return palace_has_one_of_stars(palace, stars)


def palace_not_self_mutaged(palace: Palace, with_mutagens: str | list[str] | None = None) -> bool:
    """判断宫位是否没有自化"""
    muts = with_mutagens or ["禄", "权", "科", "忌"]
    stars = mutagens_to_stars(palace.heavenly_stem, muts)
    return palace_not_have_stars(palace, stars)


def palace_mutaged_places(astrolabe: Astrolabe, palace: Palace) -> list[Optional[Palace]]:
    """获取宫位产生四化的4个宫位（禄权科忌）"""
    stars = mutagens_to_stars(palace.heavenly_stem, ["禄", "权", "科", "忌"])
    result = []
    for star_name in stars:
        found = find_star_palace(astrolabe, star_name)
        result.append(found)
    return result


# ============================================================
# 星耀查询
# ============================================================

def find_star(astrolabe: Astrolabe, star_name: str) -> Optional[Star]:
    """获取指定星耀"""
    for p in astrolabe.palaces:
        for s in p.major_stars + p.minor_stars + p.adjective_stars:
            if s.name == star_name:
                return s
    return None


def find_star_palace(astrolabe: Astrolabe, star_name: str) -> Optional[Palace]:
    """获取指定星耀所在宫位"""
    for p in astrolabe.palaces:
        for s in p.major_stars + p.minor_stars + p.adjective_stars:
            if s.name == star_name:
                return p
    return None


def star_surrounded_palaces(astrolabe: Astrolabe, star_name: str) -> Optional[SurroundedPalaces]:
    """获取指定星耀三方四正宫位"""
    palace = find_star_palace(astrolabe, star_name)
    if not palace:
        return None
    return get_surrounded_palaces(astrolabe, palace.index)


def star_opposite_palace(astrolabe: Astrolabe, star_name: str) -> Optional[Palace]:
    """获取指定星耀对宫"""
    sp = star_surrounded_palaces(astrolabe, star_name)
    if not sp:
        return None
    return sp.opposite


def star_with_brightness(astrolabe: Astrolabe, star_name: str, brightness: str | list[str]) -> bool:
    """判断星耀是否是某个亮度"""
    star = find_star(astrolabe, star_name)
    if not star or not star.brightness:
        return False
    if isinstance(brightness, list):
        return star.brightness in brightness
    return star.brightness == brightness


def star_with_mutagen(astrolabe: Astrolabe, star_name: str, mutagen: str | list[str]) -> bool:
    """判断星耀是否产生了四化"""
    star = find_star(astrolabe, star_name)
    if not star or not star.mutagen:
        return False
    if isinstance(mutagen, list):
        return star.mutagen in mutagen
    return star.mutagen == mutagen


def get_mutagens_by_heavenly_stem(heavenly_stem: str) -> list[str]:
    """根据天干获取四化星耀"""
    stem_info = HEAVENLY_STEMS_INFO.get(heavenly_stem)
    if not stem_info:
        return []
    return list(stem_info.get("mutagen", []))
