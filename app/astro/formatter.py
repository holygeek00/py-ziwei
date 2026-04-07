from app.core.types import Astrolabe, Horoscope, Star, HoroscopeItem
from app.core.calendar_utils import solar_to_lunar, lunar_to_solar
from app.astro.horoscope import get_horoscope_data, horoscope_surrounded_palaces
from app.astro.analyzer import get_surrounded_palaces, palace_mutaged_places, mutagens_to_stars, palace_has_stars, palace_is_empty

class ReportFormatter:
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
        prompt = "你現在是資深的國學易經術數領域專家，請詳細分析下面這個紫微斗數命盤，綜合使用三合紫微、飛星紫微、河洛紫微、欽天四化等各流派紫微斗數的分析技法，對命盤十二宮星曜分布、限流疊宮和各宮位間的飛宮四化進行細緻分析，進而對命主的健康、學業、事業、财運、人際關系、婚姻和感情等各個方面進行全面分析和總結，關鍵事件須給出發生時間範圍、吉兇屬性、事件對命主的影響程度等信息，並結合命主的自身特點給出針對性的解決方案和建議。另外，命盤信息裏附帶了十二個大限共一百二十個流年的信息，請對前八個大限的所有流年進行分析，給出每一年需要關注的重大事件和注意事項。"
        self.log(prompt)
        self.log()
        self.log("紫微斗数详细分析报告")
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
            is_empty_str = "(空宫)" if palace_is_empty(p) else ""
            self.log(f"│ ├{p_display_name}[{p.heavenly_stem}{p.earthly_branch}]{is_empty_str}")
            
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
            
            # 三方四正
            try:
                sp = get_surrounded_palaces(self.astrolabe, p.index)
                sp_names = []
                for tp in [sp.opposite, sp.wealth, sp.career]:
                    if tp:
                        sp_names.append(tp.name if tp.name.endswith("宫") else f"{tp.name}宫")
                self.log(f"│ │ ├三方四正 : {', '.join(sp_names)}")
            except Exception:
                pass
            
            # 飞星
            try:
                mutaged_places = palace_mutaged_places(self.astrolabe, p)
                fly_strs = []
                mutagens_label = ["化禄", "化权", "化科", "化忌"]
                for i, mut_p in enumerate(mutaged_places):
                    if mut_p:
                        p_name = mut_p.name if mut_p.name.endswith("宫") else f"{mut_p.name}宫"
                        fly_strs.append(f"{mutagens_label[i]}入{p_name}")
                if fly_strs:
                    self.log(f"│ │ ├宫位飞星 : {', '.join(fly_strs)}")
            except Exception:
                pass

            # 自化
            try:
                self_muts = []
                for m in ["禄", "权", "科", "忌"]:
                    stars_for_m = mutagens_to_stars(p.heavenly_stem, m)
                    if stars_for_m and palace_has_stars(p, stars_for_m):
                        self_muts.append(f"自化{m}({stars_for_m[0]})")
                if self_muts:
                    self.log(f"│ │ ├宫位自化 : {', '.join(self_muts)}")
            except Exception:
                pass
            
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
            
        scope_map = {"大限": "decadal", "流年": "yearly", "流月": "monthly", "流日": "daily"}
        scope = scope_map.get(label)
        if scope:
            try:
                sp = horoscope_surrounded_palaces(self.astrolabe, self.horoscope, "命宫", scope)
                if sp:
                    sp_branches = []
                    for tp in [sp.opposite, sp.wealth, sp.career]:
                        if tp:
                            sp_branches.append(f"{tp.name.replace('宫', '')}({tp.earthly_branch})")
                    self.log(f"│ ├运限三方四正 : {', '.join(sp_branches)}")
            except Exception:
                pass
        
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
