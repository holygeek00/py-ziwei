"""
API 路由 — 全部排盘和分析接口
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from app.core.types import PaipanRequest, PaipanResponse, Astrolabe, Horoscope
from app.astro.astro import by_solar, by_lunar
from app.astro.horoscope import (
    get_horoscope_data, horoscope_palace, horoscope_surrounded_palaces,
    horoscope_has_stars, horoscope_not_have_stars, horoscope_has_one_of_stars,
    horoscope_has_mutagen,
)
from app.astro.analyzer import (
    get_palace, get_surrounded_palaces,
    palace_has_stars, palace_not_have_stars, palace_has_one_of_stars,
    palace_has_mutagen, palace_not_have_mutagen, palace_is_empty,
    palace_flies_to, palace_flies_one_of_to, palace_not_fly_to,
    palace_self_mutaged, palace_self_mutaged_one_of, palace_not_self_mutaged,
    palace_mutaged_places,
    find_star, find_star_palace, star_surrounded_palaces, star_opposite_palace,
    star_with_brightness, star_with_mutagen,
    get_mutagens_by_heavenly_stem,
)
from app.astro.formatter import ReportFormatter

router = APIRouter()

# ============================================================
# 缓存当前排盘结果（简单 in-memory）
# ============================================================
_cache: dict[str, Astrolabe] = {}


def _get_or_create_astrolabe(req: PaipanRequest) -> Astrolabe:
    key = f"{req.date_str}_{req.time_index}_{req.gender}_{req.date_type}_{req.algorithm}"
    if key not in _cache:
        if req.date_type == "lunar":
            _cache[key] = by_lunar(
                req.date_str, req.time_index, req.gender,
                req.is_leap_month, req.fix_leap,
                req.year_divide, req.horoscope_divide, req.day_divide, req.algorithm,
            )
        else:
            _cache[key] = by_solar(
                req.date_str, req.time_index, req.gender,
                req.fix_leap, req.year_divide, req.horoscope_divide,
                req.day_divide, req.algorithm,
            )
    return _cache[key]


# ============================================================
# 1. 排盘
# ============================================================

@router.post("/paipan", response_model=PaipanResponse)
async def paipan(req: PaipanRequest):
    """排盘接口 — 获取完整的紫微斗数星盘"""
    try:
        astrolabe = _get_or_create_astrolabe(req)
        return PaipanResponse(astrolabe=astrolabe)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# 2. 运限
# ============================================================

class HoroscopeRequest(BaseModel):
    date_str: str
    time_index: int
    gender: str
    date_type: str = "solar"
    is_leap_month: bool = False
    fix_leap: bool = True
    year_divide: str = "normal"
    horoscope_divide: str = "normal"
    day_divide: str = "forward"
    algorithm: str = "default"
    target_date: str = ""  # 目标日期，默认当天
    target_time_index: int = -1  # 目标时辰


@router.post("/horoscope")
async def horoscope(req: HoroscopeRequest):
    """获取运限数据 — 大限/小限/流年/流月/流日/流时"""
    try:
        paipan_req = PaipanRequest(
            date_str=req.date_str, time_index=req.time_index, gender=req.gender,
            date_type=req.date_type, is_leap_month=req.is_leap_month,
            fix_leap=req.fix_leap, year_divide=req.year_divide,
            horoscope_divide=req.horoscope_divide, day_divide=req.day_divide,
            algorithm=req.algorithm,
        )
        astrolabe = _get_or_create_astrolabe(paipan_req)
        target = req.target_date if req.target_date else None
        ti = req.target_time_index if req.target_time_index >= 0 else None
        h = get_horoscope_data(astrolabe, target, ti, req.horoscope_divide)
        return h.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# 3. 宫位查询
# ============================================================

class PalaceQueryRequest(PaipanRequest):
    palace: str | int  # 宫位名或索引


class StarsQueryRequest(PalaceQueryRequest):
    stars: list[str]  # 星耀名称列表


class MutagenQueryRequest(PalaceQueryRequest):
    mutagen: str  # 四化: 禄/权/科/忌


@router.post("/palace/has_stars")
async def api_palace_has_stars(req: StarsQueryRequest):
    """判断指定宫位是否存在某些星耀（全部包含才返回true）"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_has_stars(palace, req.stars)}


@router.post("/palace/not_have_stars")
async def api_palace_not_have(req: StarsQueryRequest):
    """判断指定宫位是否不含某些星耀"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_not_have_stars(palace, req.stars)}


@router.post("/palace/has_one_of_stars")
async def api_palace_has_one_of(req: StarsQueryRequest):
    """判断指定宫位是否包含其中一颗星耀"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_has_one_of_stars(palace, req.stars)}


@router.post("/palace/has_mutagen")
async def api_palace_has_mutagen(req: MutagenQueryRequest):
    """判断指定宫位是否存在四化"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_has_mutagen(palace, req.mutagen)}


class EmptyQueryRequest(PalaceQueryRequest):
    exclude_stars: list[str] = []


@router.post("/palace/is_empty")
async def api_palace_is_empty(req: EmptyQueryRequest):
    """判断指定宫位是否是空宫"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_is_empty(palace, req.exclude_stars or None)}


# ============================================================
# 4. 三方四正
# ============================================================

@router.post("/palace/surrounded")
async def api_surrounded_palaces(req: PalaceQueryRequest):
    """获取指定宫位三方四正"""
    astrolabe = _get_or_create_astrolabe(req)
    sp = get_surrounded_palaces(astrolabe, req.palace)
    return {
        "target": sp.target.model_dump(),
        "opposite": sp.opposite.model_dump(),
        "wealth": sp.wealth.model_dump(),
        "career": sp.career.model_dump(),
    }


@router.post("/palace/surrounded/has_stars")
async def api_surrounded_has_stars(req: StarsQueryRequest):
    """判断指定宫位三方四正是否存在某些星耀"""
    astrolabe = _get_or_create_astrolabe(req)
    sp = get_surrounded_palaces(astrolabe, req.palace)
    return {"result": sp.have(req.stars)}


@router.post("/palace/surrounded/has_mutagen")
async def api_surrounded_has_mutagen(req: MutagenQueryRequest):
    """判断指定宫位三方四正是否存在四化"""
    astrolabe = _get_or_create_astrolabe(req)
    sp = get_surrounded_palaces(astrolabe, req.palace)
    return {"result": sp.have_mutagen(req.mutagen)}


# ============================================================
# 5. 飞星
# ============================================================

class FlyToRequest(PalaceQueryRequest):
    to_palace: str | int
    mutagens: list[str]


@router.post("/palace/flies_to")
async def api_palace_flies_to(req: FlyToRequest):
    """判断宫位是否产生飞星到目标宫位"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_flies_to(astrolabe, palace, req.to_palace, req.mutagens)}


@router.post("/palace/self_mutaged")
async def api_palace_self_mutaged(req: MutagenQueryRequest):
    """判断宫位是否有自化"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    return {"result": palace_self_mutaged(palace, req.mutagen)}


@router.post("/palace/mutaged_places")
async def api_palace_mutaged_places(req: PalaceQueryRequest):
    """获取宫位产生的四化宫位（禄权科忌）"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = get_palace(astrolabe, req.palace)
    if not palace:
        raise HTTPException(status_code=404, detail="宫位不存在")
    places = palace_mutaged_places(astrolabe, palace)
    return {
        "places": [
            {"name": p.name, "index": p.index} if p else None
            for p in places
        ]
    }


# ============================================================
# 6. 星耀查询
# ============================================================

class StarQueryRequest(PaipanRequest):
    star_name: str


class StarBrightnessRequest(StarQueryRequest):
    brightness: str | list[str]


class StarMutagenRequest(StarQueryRequest):
    mutagen: str | list[str]


@router.post("/star/palace")
async def api_star_palace(req: StarQueryRequest):
    """获取指定星耀所在宫位"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = find_star_palace(astrolabe, req.star_name)
    if not palace:
        raise HTTPException(status_code=404, detail=f"星耀 {req.star_name} 不存在")
    return palace.model_dump()


@router.post("/star/surrounded")
async def api_star_surrounded(req: StarQueryRequest):
    """获取指定星耀三方四正宫位"""
    astrolabe = _get_or_create_astrolabe(req)
    sp = star_surrounded_palaces(astrolabe, req.star_name)
    if not sp:
        raise HTTPException(status_code=404, detail=f"星耀 {req.star_name} 不存在")
    return {
        "target": sp.target.model_dump(),
        "opposite": sp.opposite.model_dump(),
        "wealth": sp.wealth.model_dump(),
        "career": sp.career.model_dump(),
    }


@router.post("/star/opposite")
async def api_star_opposite(req: StarQueryRequest):
    """获取指定星耀对宫"""
    astrolabe = _get_or_create_astrolabe(req)
    palace = star_opposite_palace(astrolabe, req.star_name)
    if not palace:
        raise HTTPException(status_code=404, detail=f"星耀 {req.star_name} 不存在")
    return palace.model_dump()


@router.post("/star/with_brightness")
async def api_star_with_brightness(req: StarBrightnessRequest):
    """判断指定星耀是否是某个亮度"""
    astrolabe = _get_or_create_astrolabe(req)
    return {"result": star_with_brightness(astrolabe, req.star_name, req.brightness)}


@router.post("/star/with_mutagen")
async def api_star_with_mutagen(req: StarMutagenRequest):
    """判断指定星耀是否存在四化"""
    astrolabe = _get_or_create_astrolabe(req)
    return {"result": star_with_mutagen(astrolabe, req.star_name, req.mutagen)}


# ============================================================
# 7. 四化查询
# ============================================================

class HeavenlyStemRequest(BaseModel):
    heavenly_stem: str


@router.post("/mutagen/by_stem")
async def api_mutagen_by_stem(req: HeavenlyStemRequest):
    """根据天干获取四化"""
    mutagens = get_mutagens_by_heavenly_stem(req.heavenly_stem)
    if not mutagens:
        raise HTTPException(status_code=400, detail="无效的天干")
    return {
        "heavenly_stem": req.heavenly_stem,
        "禄": mutagens[0] if len(mutagens) > 0 else "",
        "权": mutagens[1] if len(mutagens) > 1 else "",
        "科": mutagens[2] if len(mutagens) > 2 else "",
        "忌": mutagens[3] if len(mutagens) > 3 else "",
    }


# ============================================================
# 8. 运限宫位查询
# ============================================================

class HoroscopePalaceRequest(HoroscopeRequest):
    palace_name: str
    scope: str  # origin/decadal/yearly/monthly/daily/hourly


class HoroscopeStarsRequest(HoroscopePalaceRequest):
    stars: list[str]


class HoroscopeMutagenRequest(HoroscopePalaceRequest):
    mutagen: str


@router.post("/horoscope/palace")
async def api_horoscope_palace(req: HoroscopePalaceRequest):
    """获取指定运限宫位"""
    paipan_req = PaipanRequest(
        date_str=req.date_str, time_index=req.time_index, gender=req.gender,
        date_type=req.date_type, algorithm=req.algorithm,
    )
    astrolabe = _get_or_create_astrolabe(paipan_req)
    h = get_horoscope_data(astrolabe, req.target_date or None, None, req.horoscope_divide)
    palace = horoscope_palace(astrolabe, h, req.palace_name, req.scope)
    if not palace:
        raise HTTPException(status_code=404, detail="运限宫位不存在")
    return palace.model_dump()


@router.post("/horoscope/surrounded")
async def api_horoscope_surrounded(req: HoroscopePalaceRequest):
    """获取指定运限宫位的三方四正"""
    paipan_req = PaipanRequest(
        date_str=req.date_str, time_index=req.time_index, gender=req.gender,
        date_type=req.date_type, algorithm=req.algorithm,
    )
    astrolabe = _get_or_create_astrolabe(paipan_req)
    h = get_horoscope_data(astrolabe, req.target_date or None, None, req.horoscope_divide)
    sp = horoscope_surrounded_palaces(astrolabe, h, req.palace_name, req.scope)
    if not sp:
        raise HTTPException(status_code=404, detail="运限宫位不存在")
    return {
        "target": sp.target.model_dump(),
        "opposite": sp.opposite.model_dump(),
        "wealth": sp.wealth.model_dump(),
        "career": sp.career.model_dump(),
    }


@router.post("/horoscope/has_stars")
async def api_horoscope_has_stars(req: HoroscopeStarsRequest):
    """判断指定运限宫位内是否存在某些流耀"""
    paipan_req = PaipanRequest(
        date_str=req.date_str, time_index=req.time_index, gender=req.gender,
        date_type=req.date_type, algorithm=req.algorithm,
    )
    astrolabe = _get_or_create_astrolabe(paipan_req)
    h = get_horoscope_data(astrolabe, req.target_date or None, None, req.horoscope_divide)
    return {"result": horoscope_has_stars(astrolabe, h, req.palace_name, req.scope, req.stars)}


@router.post("/horoscope/has_mutagen")
async def api_horoscope_has_mutagen(req: HoroscopeMutagenRequest):
    """判断指定运限宫位内是否存在四化"""
    paipan_req = PaipanRequest(
        date_str=req.date_str, time_index=req.time_index, gender=req.gender,
        date_type=req.date_type, algorithm=req.algorithm,
    )
    astrolabe = _get_or_create_astrolabe(paipan_req)
    h = get_horoscope_data(astrolabe, req.target_date or None, None, req.horoscope_divide)
    return {"result": horoscope_has_mutagen(astrolabe, h, req.palace_name, req.scope, req.mutagen)}


@router.post("/horoscope/surrounded/has_stars")
async def api_horoscope_surrounded_has_stars(req: HoroscopeStarsRequest):
    """判断指定运限宫位三方四正内是否存在某些流耀"""
    paipan_req = PaipanRequest(
        date_str=req.date_str, time_index=req.time_index, gender=req.gender,
        date_type=req.date_type, algorithm=req.algorithm,
    )
    astrolabe = _get_or_create_astrolabe(paipan_req)
    h = get_horoscope_data(astrolabe, req.target_date or None, None, req.horoscope_divide)
    return {"result": horoscope_is_surrounded_by_stars(astrolabe, h, req.palace_name, req.scope, req.stars)}


@router.post("/horoscope/surrounded/has_mutagen")
async def api_horoscope_surrounded_has_mutagen(req: HoroscopeMutagenRequest):
    """判断指定运限三方四正内是否存在四化"""
    paipan_req = PaipanRequest(
        date_str=req.date_str, time_index=req.time_index, gender=req.gender,
        date_type=req.date_type, algorithm=req.algorithm,
    )
    astrolabe = _get_or_create_astrolabe(paipan_req)
    h = get_horoscope_data(astrolabe, req.target_date or None, None, req.horoscope_divide)
    return {"result": horoscope_surrounded_has_mutagen(astrolabe, h, req.palace_name, req.scope, req.mutagen)}


@router.get("/health")
async def health():
    return {"status": "ok"}


# ============================================================
# 9. 紫微斗数报告生成
# ============================================================

class ReportRequest(BaseModel):
    date_str: str
    time_index: int
    gender: str
    date_type: str = "solar"
    is_leap_month: bool = False
    target_date: str = ""
    language: str = "zh-CN"

@router.post("/report/generate")
async def generate_report(req: ReportRequest):
    """生成紫微斗数详细分析报告(Markdown格式)"""
    try:
        paipan_req = PaipanRequest(
            date_str=req.date_str, 
            time_index=req.time_index, 
            gender=req.gender,
            date_type=req.date_type, 
            is_leap_month=req.is_leap_month,
        )
        astrolabe = _get_or_create_astrolabe(paipan_req)
        
        target = req.target_date if req.target_date else None
        h = get_horoscope_data(astrolabe, target)
        
        formatter = ReportFormatter(astrolabe, h)
        report_content = formatter.render()
        
        if req.language == "zh-TW":
            import zhconv
            report_content = zhconv.convert(report_content, 'zh-tw')
        
        filename = f"紫微斗数报告_{req.date_str}.md"
        if req.language == "zh-TW":
            filename = f"紫微鬥數報告_{req.date_str}.md"
        # URL encode filename for header
        from urllib.parse import quote
        encoded_filename = quote(filename)
        
        return Response(
            content=report_content,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

