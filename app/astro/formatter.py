from app.core.types import Astrolabe, Horoscope, Star, HoroscopeItem
from app.core.calendar_utils import solar_to_lunar, lunar_to_solar
from app.astro.horoscope import get_horoscope_data
from app.astro.analyzer import get_surrounded_palaces, palace_mutaged_places, mutagens_to_stars, palace_has_stars

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
        prompt = """角色设定： 你是精通三合紫微、飞星紫微（含自化与来因宫体系）、河洛紫微、欽天四化等多流派的资深紫微斗数分析师。分析时必须多流派交叉验证，避免单一流派偏见。
任务： 对以下命盘进行全面深度分析。请严格按下述流程和要求执行。

第一步：数据提取与校验（必须先完成，不可跳过）

逐项提取并列出：性别、出生时间（公历/农历/真太阳时）、四柱、五行局数、命主星、身主星、身宫所在宫位、来因宫位置。
逐宫列出十二宫的：宫位名称、天干地支、主星（标注庙旺利陷）、辅星、煞星、小星、禄存位置、天马位置、自化标注（↑/↓）。
明确列出生年四化（禄/权/科/忌）分别落在哪颗星、哪个宫位，并与年干四化表交叉核对是否正确。
校验关卡： 若发现五行局数与命宫天干地支不匹配、或生年四化与年干不对应等异常，须明确指出并说明可能原因，再继续后续分析。

第二步：命盘格局总览

命格定性：命宫主星组合的核心性格特质与人生基调。
身宫分析：身宫位置及星曜揭示的后天发展重心。
格局判断：是否构成经典格局（紫府同宫、机月同梁、杀破狼、日月并明/反背等），格局成立条件是否完备。
命宫三方四正（命/迁/官/财）整体力量与吉凶评估。
生年四化的全局布局分析（禄权科忌的落宫组合意味什么）。
来因宫的飞星派解读（此生课题根源）。

第三步：十二宫逐宫深度分析
按以下顺序逐宫分析：命宫→福德宫→官禄宫→财帛宫→迁移宫→夫妻宫→田宅宫→子女宫→交友宫→兄弟宫→父母宫→疾厄宫。
每宫须包含：

三合派： 宫内星曜组合效应（主星+辅星+煞星）、庙旺利陷的能量评估
飞星派： 该宫宫干飞出的四化落宫及影响；其他宫位飞化入本宫的效应；自化（向心/离心）解读
对宫互动与三方四正汇聚 的综合格局
该宫的核心论断（一句话总结本宫吉凶特征）

第四步：七大人生领域专题分析
对以下领域做交叉宫位综合分析（每个领域须注明主看宫位和辅看宫位）：
领域主看辅看重点关注性格心理命宫、福德、身宫父母、疾厄内在矛盾与心理倾向事业学业官禄、命宫、迁移父母、交友官禄与命宫四化互动财运理财财帛、田宅、福德官禄、命宫禄存/化禄位置、财帛煞星婚姻感情夫妻、福德、迁移子女、田宅夫妻宫化忌冲破、来因宫影响人际社交交友、迁移、兄弟命宫贵人运与小人运健康疾厄、命宫、福德父母星曜对应身体部位、易患疾病家庭不动产田宅、兄弟、父母子女、福德置产时机与家族关系
每个领域分析须给出：当前状态评估 → 潜在风险 → 有利时间窗口 → 针对性建议。
第五步：大限流年逐年分析
对前八个大限（共80个流年）逐一分析：
每个大限须包含：

大限宫位、大限天干、大限四化落宫
大限命宫星曜组合与三方四正吉凶评估
大限四化与原盘四化的叠加效应
该大限的整体运势定性（一句话总结）

每个流年须包含：

流年宫位、流年天干、流年四化
流年与大限、原盘的三重叠加分析
该年关注事项： 用以下格式标注——

事件类型（健康/事业/财运/感情/学业/人际/意外等）
吉凶属性（大吉/小吉/平/小凶/大凶）
影响程度（★~★★★★★）
时间提示（若可细化到月份则注明）
具体建议（趋吉或避凶的可操作行动）



第六步：综合总结

命盘三大优势 与 三大风险（精炼概括）
人生关键转折年份表（按时间排列，标注事件性质与吉凶）
针对性人生策略：结合命盘特点给出事业方向、理财方式、择偶建议、健康管理等可执行建议
趋吉避凶总纲：利用命盘优势化解不利因素的系统性方案


分析原则（务必遵守）

多流派交叉验证： 任何关键论断须至少两个流派佐证，单一流派结论须标注"仅为参考"。
避免绝对化： 使用"倾向于""较大概率""需注意"等概率性措辞，不做绝对断言。
组合优先于单星： 不孤立论星，必须结合同宫、对宫、三方四正综合判断。
先天后天结合： 原盘为先天格局，大限流年为后天运程，两者须叠加分析。
建设性导向： 对不利信息必须附带化解建议，不制造焦虑。"""
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
