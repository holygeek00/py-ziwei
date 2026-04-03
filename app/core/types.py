"""
Pydantic 数据模型和类型定义
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class Star(BaseModel):
    """星耀"""
    name: str
    type: str  # major, soft, tough, adjective, flower, helper, lucun, tianma
    scope: str  # origin, decadal, yearly, monthly, daily, hourly
    brightness: str = ""
    mutagen: str = ""


class Decadal(BaseModel):
    """大限"""
    range: list[int]  # [起始年龄, 截止年龄]
    heavenly_stem: str
    earthly_branch: str


class Palace(BaseModel):
    """宫位"""
    index: int
    name: str
    is_body_palace: bool = False
    is_original_palace: bool = False
    heavenly_stem: str
    earthly_branch: str
    major_stars: list[Star] = []
    minor_stars: list[Star] = []
    adjective_stars: list[Star] = []
    changsheng12: str = ""
    boshi12: str = ""
    jiangqian12: str = ""
    suiqian12: str = ""
    decadal: Decadal = Decadal(range=[0, 0], heavenly_stem="", earthly_branch="")
    ages: list[int] = []


class HoroscopeItem(BaseModel):
    """运限项"""
    index: int
    name: str
    heavenly_stem: str
    earthly_branch: str
    palace_names: list[str] = []
    mutagen: list[str] = []
    stars: Optional[list[list[Star]]] = None


class Horoscope(BaseModel):
    """运限"""
    solar_date: str
    lunar_date: str
    decadal: HoroscopeItem
    age: HoroscopeItem
    yearly: HoroscopeItem
    monthly: HoroscopeItem
    daily: HoroscopeItem
    hourly: HoroscopeItem


class Astrolabe(BaseModel):
    """星盘"""
    gender: str
    solar_date: str
    lunar_date: str
    chinese_date: str
    time: str
    time_range: str
    sign: str
    zodiac: str
    earthly_branch_of_soul_palace: str
    earthly_branch_of_body_palace: str
    soul: str  # 命主
    body: str  # 身主
    five_elements_class: str  # 五行局
    palaces: list[Palace]


class PaipanRequest(BaseModel):
    """排盘请求"""
    date_str: str  # YYYY-M-D
    time_index: int  # 0~12
    gender: str  # 男/女
    date_type: str = "solar"  # solar / lunar
    is_leap_month: bool = False
    fix_leap: bool = True
    year_divide: str = "normal"  # normal / exact
    horoscope_divide: str = "normal"
    day_divide: str = "forward"  # current / forward
    algorithm: str = "default"  # default / zhongzhou


class PaipanResponse(BaseModel):
    """排盘响应"""
    astrolabe: Astrolabe
    horoscope: Optional[Horoscope] = None
