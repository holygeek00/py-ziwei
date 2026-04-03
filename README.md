# 🌟 Py-Ziwei — 紫微斗数排盘 API

Python 版紫微斗数排盘后端，移植自 [iztro](https://github.com/SylarLong/iztro)，提供完整的排盘计算能力和 RESTful API 接口。

## ✨ 功能特性

- 🔮 **完整排盘** — 14 主星、14 辅星、~38 杂耀、长生/博士/岁前/将前 12 神
- 🎯 **四化标注** — 禄、权、科、忌，支持生年四化与流年四化
- 💡 **亮度标注** — 庙、旺、得、利、平、不、陷
- 📅 **阳历/农历** — 双模式排盘，自动处理闰月
- 🏛️ **多流派** — 通行版本 + 中州派
- 🔄 **运限计算** — 大限、小限、流年/流月/流日/流时流耀
- ⚡ **FastAPI** — 高性能异步 API，自带 Swagger 文档

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
cd py-ziwei

# 创建虚拟环境并安装
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. 启动 API 服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8787
```

访问 http://localhost:8787/docs 查看交互式 API 文档。

### 3. 调用排盘接口

```bash
curl -X POST http://localhost:8787/api/paipan \
  -H "Content-Type: application/json" \
  -d '{
    "date_str": "2000-8-16",
    "time_index": 2,
    "gender": "女"
  }'
```

### 4. 直接调用 Python

```python
from app.astro.astro import by_solar, by_lunar

# 阳历排盘
astrolabe = by_solar("2000-8-16", 2, "女")

# 农历排盘
astrolabe = by_lunar("2000-7-17", 2, "女")

# 查看结果
print(f"命宫: {astrolabe.earthly_branch_of_soul_palace}")
print(f"五行局: {astrolabe.five_elements_class}")
for palace in astrolabe.palaces:
    stars = ", ".join(s.name for s in palace.major_stars)
    print(f"  {palace.heavenly_stem}{palace.earthly_branch} {palace.name}: {stars}")
```

## 📋 API 参数说明

### POST `/api/paipan`

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|:----:|------|------|
| `date_str` | string | ✅ | — | 日期，格式 `YYYY-M-D` |
| `time_index` | int | ✅ | — | 时辰索引，`0`(早子) ~ `12`(晚子) |
| `gender` | string | ✅ | — | `"男"` 或 `"女"` |
| `date_type` | string | | `"solar"` | `"solar"`(阳历) / `"lunar"`(农历) |
| `is_leap_month` | bool | | `false` | 农历闰月标记 |
| `fix_leap` | bool | | `true` | 是否调整闰月（闰月后15天按下月算） |
| `year_divide` | string | | `"normal"` | `"normal"`(正月初一) / `"exact"`(立春) |
| `algorithm` | string | | `"default"` | `"default"`(通行) / `"zhongzhou"`(中州派) |

### 时辰索引对照

| 索引 | 时辰 | 时间段 |
|:----:|:----:|:------:|
| 0 | 早子时 | 00:00~01:00 |
| 1 | 丑时 | 01:00~03:00 |
| 2 | 寅时 | 03:00~05:00 |
| 3 | 卯时 | 05:00~07:00 |
| 4 | 辰时 | 07:00~09:00 |
| 5 | 巳时 | 09:00~11:00 |
| 6 | 午时 | 11:00~13:00 |
| 7 | 未时 | 13:00~15:00 |
| 8 | 申时 | 15:00~17:00 |
| 9 | 酉时 | 17:00~19:00 |
| 10 | 戌时 | 19:00~21:00 |
| 11 | 亥时 | 21:00~23:00 |
| 12 | 晚子时 | 23:00~00:00 |

## 📁 项目结构

```
py-ziwei/
├── pyproject.toml
├── README.md
└── app/
    ├── main.py                  # FastAPI 入口
    ├── api/
    │   └── routes.py            # API 路由
    ├── core/
    │   ├── constants.py         # 天干地支、亮度表、四化等常量
    │   ├── types.py             # Pydantic 数据模型
    │   ├── calendar_utils.py    # 农历/阳历转换
    │   └── utils.py             # 工具函数
    ├── star/
    │   ├── location.py          # 星耀位置算法
    │   ├── major_star.py        # 14 主星安放
    │   ├── minor_star.py        # 14 辅星安放
    │   ├── adjective_star.py    # ~38 杂耀安放
    │   ├── decorative_star.py   # 长生/博士/岁前/将前 12 神
    │   └── horoscope_star.py    # 流耀计算
    └── astro/
        ├── palace.py            # 命身宫、五行局、大限小限
        └── astro.py             # 排盘主入口
```

## 🔬 排盘结果示例

```
阳历: 2000-8-16 | 农历: 2000年7月17日 | 干支: 庚辰 甲申 丙午 庚寅
时辰: 寅时 (03:00~05:00) | 星座: 狮子座 | 生肖: 龙
命宫: 午 | 身宫: 戌 | 命主: 破军 | 身主: 文昌 | 五行局: 木三局

 宫位        主星                     辅星           大限
────────────────────────────────────────────────────────────
 戊寅 财帛   武曲(权)[得], 天相[庙]   天马           43~52岁
 己卯 子女   太阳(禄)[庙], 天梁[庙]                  33~42岁
 庚辰 夫妻   七杀[庙]                 右弼, 火星     23~32岁
 辛巳 兄弟   天机[平]                                13~22岁
 壬午 命宫   紫微[庙]                 文曲            3~12岁
 癸未 父母   (空宫)                   天钺, 陀罗   113~122岁
 甲申 福德   破军[得]                 文昌, 禄存   103~112岁
 乙酉 田宅   (空宫)                   地空, 擎羊    93~102岁
 丙戌 官禄⭐ 廉贞[利], 天府[庙]       左辅           83~92岁
 丁亥 仆役   太阴(科)[庙]                            73~82岁
 戊子 迁移   贪狼[旺]                 铃星           63~72岁
 己丑 疾厄   天同(忌)[不], 巨门[不]   天魁, 地劫     53~62岁
```

## 🧰 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | [FastAPI](https://fastapi.tiangolo.com/) |
| 数据验证 | [Pydantic](https://docs.pydantic.dev/) v2 |
| 农历计算 | [lunar-python](https://github.com/6tail/lunar-python)（寿星万年历） |
| ASGI 服务器 | [Uvicorn](https://www.uvicorn.org/) |

## 📜 致谢

本项目核心算法移植自 [iztro](https://github.com/SylarLong/iztro)，感谢原作者 SylarLong 的开源贡献。

## 📄 License

MIT
# py-ziwei
