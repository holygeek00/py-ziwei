# 紫微斗数排盘 API 文档 (基于 py-iztro)

本 API 提供完整的紫微斗数排盘及逻辑查询功能，由 Python FastAPI 驱动，移植自 [iztro](https://github.com/iztro/iztro)。

## 1. 核心接口

### 1.1 排盘接口 (Paipan)
获取完整的紫微斗数星盘数据。

- **URL**: `/api/paipan`
- **Method**: `POST`
- **功能**: 输入出生日期、时间、性别等信息，返回含有 12 宫位、星耀分布、大限等信息的完整星盘。
- **请求参数 (`PaipanRequest`)**:
    - `date_str` (string): 日期字符串 (如 "2000-01-01")
    - `time_index` (int): 时辰索引 (0-12, 0 为早子时, 12 为晚子时)
    - `gender` (string): 性别 ("male" 或 "female")
    - `date_type` (string): 日期类型 ("solar" 阳历 或 "lunar" 农历，默认 "solar")
    - `is_leap_month` (boolean): 是否闰月 (默认 `false`)
    - `fix_leap` (boolean): 是否调整闰月 (默认 `true`)
- **响应**: 返回 `PaipanResponse`，包含 `astrolabe` (星盘) 和可选的 `horoscope` (当前运限)。

### 1.2 运限数据接口 (Horoscope)
获取指定时刻的各级运限数据。

- **URL**: `/api/horoscope`
- **Method**: `POST`
- **功能**: 在已有排盘基础上，获取特定年份/月份/日期/时辰的运限信息（大限、小限、流年、流月、流日、流时）。
- **请求参数 (`HoroscopeRequest`)**:
    - `date_str`, `time_index`, `gender`: 同排盘参数
    - `target_date` (string): 目标日期
    - `target_time_index` (int): 目标时辰索引

---

## 2. 宫位查询接口 (Palace Queries)

这些接口用于判断一个宫位内是否存在特定的星耀或四化。

### 2.1 基础查询
- **判断是否存在星耀**: `/api/palace/has_stars` (需包含所有指定星耀)
- **判断是否不含星耀**: `/api/palace/not_have_stars`
- **判断是否包含其中之一**: `/api/palace/has_one_of_stars`
- **判断是否有四化**: `/api/palace/has_mutagen` (禄权科忌)
- **判断是否空宫**: `/api/palace/is_empty`

### 2.2 关联查询 (三方四正)
- **获取三方四正**: `/api/palace/surrounded` (获取指定宫位的对宫、财帛、官禄位)
- **三方四正是否存在星耀**: `/api/palace/surrounded/has_stars`
- **三方四正是否存在四化**: `/api/palace/surrounded/has_mutagen`

### 2.3 飞星与自化 (Flying Stars)
- **宫位飞星**: `/api/palace/flies_to` (判断宫位 A 是否产生某个四化到宫位 B)
- **宫位自化**: `/api/palace/self_mutaged` (判断宫位是否产生自化)
- **飞出宫位**: `/api/palace/mutaged_places` (获取该宫位天干产生的四化星所在的宫位)

---

## 3. 星耀查询接口 (Star Queries)

### 3.1 位置定位
- **获取星耀所在宫位**: `/api/star/palace`
- **获取星耀三方四正**: `/api/star/surrounded`
- **获取星耀对宫**: `/api/star/opposite`

### 3.2 属性判断
- **判断星耀亮度**: `/api/star/with_brightness` (庙旺利陷)
- **判断星耀四化**: `/api/star/with_mutagen`

---

## 4. 动态运限查询接口 (Horoscope Logic)

专门针对流年、流月等动态盘进行逻辑判断。

- **获取运限宫位**: `/api/horoscope/palace` (如：流年命宫、流年财帛宫等)
- **获取运限三方四正**: `/api/horoscope/surrounded`
- **判断运限宫位流耀**: `/api/horoscope/has_stars` (判断流年星耀如：流羊、流陀等)
- **判断运限宫位四化**: `/api/horoscope/has_mutagen`
- **判断运限三方四正流耀**: `/api/horoscope/surrounded/has_stars`
- **判断运限三方四正四化**: `/api/horoscope/surrounded/has_mutagen`

---

## 5. 数据结构说明 (Schemas)

### Astrolabe (星盘)
包含排盘的核心结果：
- `solar_date`: 阳历日期
- `lunar_date`: 农历日期
- `chinese_date`: 干支日期 (如：庚辰年戊子月...)
- `five_elements_class`: 五行局
- `soul`/`body`: 命主/身主
- `palaces`: 包含 12 个宫位的数组

### Palace (宫位对象)
- `name`: 宫位名称 (命宫、兄弟等)
- `heavenly_stem`/`earthly_branch`: 宫位天干地支
- `major_stars`: 主星列表
- `minor_stars`: 辅星列表
- `adjective_stars`: 杂曜
- `decadal`: 该宫位的大限起止年份

### Star (星耀对象)
- `name`: 星名
- `type`: 类型 (主星/辅星等)
- `brightness`: 亮度 (庙/旺/得/利/平/不/陷)
- `mutagen`: 四化 (禄/权/科/忌)

---

## 6. 其他接口

- **健康检查**: `/api/health`
- **根据天干获取四化**: `/api/mutagen/by_stem`
