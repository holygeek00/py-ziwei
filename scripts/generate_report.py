#!/usr/bin/env python3
"""
Zi Wei Dou Shu Detailed Report Generator
Generates a report with detailed Yearly/Monthly/Daily analysis.
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
from app.astro.formatter import ReportFormatter

def main():
    parser = argparse.ArgumentParser(description="生成详细的紫微斗数报表")
    parser.add_argument("--date", type=str, required=True, help="出生日期 (YYYY-MM-DD)")
    parser.add_argument("--time", type=int, required=True, help="时辰索引 (0-12)")
    parser.add_argument("--gender", type=str, required=True, choices=["男", "女", "male", "female"], help="性别")
    parser.add_argument("--target", type=str, help="目标分析日期 (YYYY-MM-DD), 默认为今天")
    parser.add_argument("--type", type=str, default="solar", choices=["solar", "lunar"], help="日期类型")
    parser.add_argument("--leap", action="store_true", help="是否闰月 (仅限农历)")
    parser.add_argument("--lang", type=str, default="zh-CN", choices=["zh-CN", "zh-TW"], help="语言: zh-CN(简体) 或 zh-TW(繁体)")

    args = parser.parse_args()

    gender = "male" if args.gender in ["男", "male"] else "female"
    
    try:
        if args.type == "lunar":
            astrolabe = by_lunar(args.date, args.time, gender, is_leap_month=args.leap)
        else:
            astrolabe = by_solar(args.date, args.time, gender)
        
        target_date = args.target if args.target else datetime.now().strftime("%Y-%m-%d")
        horoscope = get_horoscope_data(astrolabe, target_date)
        
        formatter = ReportFormatter(astrolabe, horoscope)
        report_content = formatter.render()
        
        if args.lang == "zh-TW":
            import zhconv
            report_content = zhconv.convert(report_content, 'zh-tw')
            
        print(report_content)
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
