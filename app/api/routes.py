"""
API 路由
"""
from fastapi import APIRouter, HTTPException
from app.core.types import PaipanRequest, PaipanResponse
from app.astro.astro import by_solar, by_lunar

router = APIRouter()


@router.post("/paipan", response_model=PaipanResponse)
async def paipan(req: PaipanRequest):
    """
    排盘接口

    通过阳历或农历日期 + 时辰 + 性别，计算完整的紫微斗数命盘
    """
    try:
        if req.date_type == "lunar":
            astrolabe = by_lunar(
                lunar_date_str=req.date_str,
                time_index=req.time_index,
                gender=req.gender,
                is_leap_month=req.is_leap_month,
                fix_leap=req.fix_leap,
                year_divide=req.year_divide,
                horoscope_divide=req.horoscope_divide,
                day_divide=req.day_divide,
                algorithm=req.algorithm,
            )
        else:
            astrolabe = by_solar(
                solar_date=req.date_str,
                time_index=req.time_index,
                gender=req.gender,
                fix_leap=req.fix_leap,
                year_divide=req.year_divide,
                horoscope_divide=req.horoscope_divide,
                day_divide=req.day_divide,
                algorithm=req.algorithm,
            )
        return PaipanResponse(astrolabe=astrolabe)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok"}
