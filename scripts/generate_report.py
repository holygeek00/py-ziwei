#!/usr/bin/env python3
"""
Zi Wei Dou Shu Detailed Report Generator
Generates a report in WenMoTianJi style with detailed Yearly/Monthly/Daily analysis.
"""

import sys
import os
import argparse
from datetime import datetime

# Add the parent directory to sys.path to import the app package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.astro.astro import by_solar, by_lunar
from app.astro.horoscope import get_horoscope_data
from app.core.types import Astrolabe, Horoscope, Palace, Star, HoroscopeItem
from app.core.calendar_utils import solar_to_lunar, lunar_to_solar

class WenMoFormatter:
    def __init__(self, astrolabe: Astrolabe, horoscope: Horoscope = None):
        self.astrolabe = astrolabe
        self.horoscope = horoscope
        self.output = []

    def log(self, text: str = ""):
        self.output.append(text)

    def format_star(self, star: Star) -> str:
        s = f"{star.name}"
        if star.brightness:
            s += f"[{star.brightness}]"
        if star.mutagen:
            s += f"[{star.mutagen}]"
        return s

    def get_overlapping_palaces(self, earthly_branch: str) -> list[str]:
        """Find which luck palaces overlap with this base palace branch"""
        overlaps = []
        if not self.horoscope:
            return overlaps
        
        # Priority mapping for labels
        cycle_labels = {
            "decadal": "大",
            "yearly": "流",
            "monthly": "月",
            "daily": "日"
        }
        
        branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        try:
            idx = branches.index(earthly_branch)
        except ValueError:
            return overlaps

        cycles = [
            (cycle_labels["decadal"], self.horoscope.decadal),
            (cycle_labels["yearly"], self.horoscope.yearly),
            (cycle_labels["monthly"], self.horoscope.monthly),
            (cycle_labels["daily"], self.horoscope.daily)
        ]
        
        for label, item in cycles:
            if not item: continue
            # The luck palace name at this branch for this cycle
            p_name = item.palace_names[idx]
            # Strip "宫" if present for concise view like "大命", "流财"
            short_name = p_name.replace("宫", "")
            overlaps.append(f"{label}{short_name}")
            
        return overlaps

    def render_header(self):
        self.log("文墨天机风格紫微斗数详细分析报告")
        self.log("│")
        self.log(f"├性别 : {self.astrolabe.gender}")
        self.log(f"├阳历时间 : {self.astrolabe.solar_date} {self.astrolabe.time}")
        self.log(f"├农历时间 : {self.astrolabe.lunar_date}")
        self.log(f"├干支四柱 : {self.astrolabe.chinese_date}")
        self.log(f"├五行局数 : {self.astrolabe.five_elements_class}")
        self.log(f"└命主:{self.astrolabe.soul}; 身主:{self.astrolabe.body}; 命宫地支:{self.astrolabe.earthly_branch_of_soul_palace}; 身宫地支:{self.astrolabe.earthly_branch_of_body_palace}")
        self.log()

    def render_palaces(self):
        self.log("├命盘十二宫")
        self.log("│ │ ")
        for p in self.astrolabe.palaces:
            p_display_name = p.name if p.name.endswith("宫") else f"{p.name}宫"
            self.log(f"│ ├{p_display_name}[{p.heavenly_stem}{p.earthly_branch}]")
            
            # Stars
            if p.major_stars:
                self.log(f"│ │ ├主星 : {', '.join([self.format_star(s) for s in p.major_stars])}")
            if p.minor_stars:
                self.log(f"│ │ ├辅星 : {', '.join([self.format_star(s) for s in p.minor_stars])}")
            if p.adjective_stars:
                # Group adjective stars to keep it concise
                self.log(f"│ │ ├杂曜 : {', '.join([s.name for s in p.adjective_stars[:8]])}")
            
            # Spirit stars
            self.log(f"│ │ ├神煞 : {p.changsheng12}, {p.boshi12}, {p.jiangqian12}, {p.suiqian12}")
            
            # Luck cycles
            self.log(f"│ │ ├大限 : {p.decadal.range[0]}~{p.decadal.range[1]}岁")
            
            # Overlapping
            overlaps = self.get_overlapping_palaces(p.earthly_branch)
            if overlaps:
                self.log(f"│ │ └限流叠宫 : {' -> '.join(overlaps)}")
            else:
                self.log("│ │ └限流叠宫 : 无")
            self.log("│ │ ")

    def render_horoscope_detail(self, label: str, item: HoroscopeItem):
        self.log(f"├{label}分析 [{item.heavenly_stem}{item.earthly_branch}年/月/日]")
        self.log(f"│ ├运限命宫所在 : {item.earthly_branch}宫")
        if item.mutagen:
            self.log(f"│ ├流迁四化 : {', '.join(item.mutagen)}")
        
        # Find which base palace this luck life palace falls into
        base_palace = next((p for p in self.astrolabe.palaces if p.earthly_branch == item.earthly_branch), None)
        if base_palace:
            p_name = base_palace.name if base_palace.name.endswith("宫") else f"{base_palace.name}宫"
            self.log(f"│ ├落入原局 : {p_name}")
        
        # Show stars in the luck life palace
        if item.stars and len(item.stars) > item.index:
            stars_in_palace = item.stars[item.index]
            if stars_in_palace:
                self.log(f"│ └流耀分布 : {', '.join([s.name for s in stars_in_palace])}")
        self.log("│")

    def render_monthly_summary(self):
        self.log("├流月命宫列表汇总 (当年12个月)")
        try:
            lunar_info = solar_to_lunar(self.horoscope.solar_date)
            year = lunar_info["lunarYear"]
            
            for m in range(1, 13):
                # Use the 15th of each lunar month to calculate the flow
                solar_date = lunar_to_solar(f"{year}-{m}-15")
                h = get_horoscope_data(self.astrolabe, solar_date)
                item = h.monthly
                
                # Find base palace
                base_palace = next((p for p in self.astrolabe.palaces if p.earthly_branch == item.earthly_branch), None)
                if base_palace:
                    p_name = base_palace.name if base_palace.name.endswith("宫") else f"{base_palace.name}宫"
                else:
                    p_name = "未知"
                
                self.log(f"│ ├{m:2}月 [{item.heavenly_stem}{item.earthly_branch}] : 命宫落 [{item.earthly_branch}] ({p_name})")
        except Exception as e:
            self.log(f"│ ├汇总失败: {str(e)}")
        self.log("│")

    def render(self):
        self.render_header()
        self.render_palaces()
        
        if self.horoscope:
            self.log("├当前运限详细概览")
            self.log("│")
            self.render_horoscope_detail("流年", self.horoscope.yearly)
            
            # Monthly summary requested by user
            self.render_monthly_summary()
            
            self.render_horoscope_detail("流月", self.horoscope.monthly)
            self.render_horoscope_detail("流日", self.horoscope.daily)
        
        self.log("└报告生成完毕")
        return "\n".join(self.output)

def main():
    parser = argparse.ArgumentParser(description="生成详细的紫微斗数报表")
    parser.add_argument("--date", type=str, required=True, help="出生日期 (YYYY-MM-DD)")
    parser.add_argument("--time", type=int, required=True, help="时辰索引 (0-12)")
    parser.add_argument("--gender", type=str, required=True, choices=["男", "女", "male", "female"], help="性别")
    parser.add_argument("--target", type=str, help="目标分析日期 (YYYY-MM-DD), 默认为今天")
    parser.add_argument("--type", type=str, default="solar", choices=["solar", "lunar"], help="日期类型")
    parser.add_argument("--leap", action="store_true", help="是否闰月 (仅限农历)")

    args = parser.parse_args()

    gender = "male" if args.gender in ["男", "male"] else "female"
    
    try:
        if args.type == "lunar":
            astrolabe = by_lunar(args.date, args.time, gender, is_leap_month=args.leap)
        else:
            astrolabe = by_solar(args.date, args.time, gender)
        
        target_date = args.target if args.target else datetime.now().strftime("%Y-%m-%d")
        horoscope = get_horoscope_data(astrolabe, target_date)
        
        formatter = WenMoFormatter(astrolabe, horoscope)
        print(formatter.render())
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
