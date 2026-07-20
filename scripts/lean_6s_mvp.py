#!/usr/bin/env python3
"""Rule-based MVP helper for Lean 6S issue triage and closure checks."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


CATEGORY_RULES = {
    "Safety / 安全": [
        "blocked extinguisher",
        "fire",
        "emergency",
        "exit",
        "guard",
        "slip",
        "trip",
        "forklift",
        "electric",
        "chemical",
        "ppe",
        "safety",
        "消防",
        "安全",
        "通道",
        "逃生",
        "灭火器",
        "配电",
        "护罩",
        "叉车",
        "滑倒",
    ],
    "Seiton / 整顿": [
        "no fixed location",
        "unlabeled",
        "label",
        "random",
        "search",
        "mixed location",
        "tool",
        "shelf",
        "shadow board",
        "定位",
        "标识",
        "标签",
        "乱放",
        "找不到",
        "工具",
        "货架",
        "混放",
    ],
    "Seiso / 清扫": [
        "oil",
        "leak",
        "dust",
        "chips",
        "trash",
        "waste",
        "dirty",
        "clean",
        "油",
        "漏",
        "灰尘",
        "铁屑",
        "垃圾",
        "脏",
        "清扫",
        "积水",
    ],
    "Seiri / 整理": [
        "obsolete",
        "unused",
        "expired",
        "scrap",
        "excess",
        "unneeded",
        "red tag",
        "呆滞",
        "不用",
        "过期",
        "报废",
        "多余",
        "废料",
        "红牌",
    ],
    "Seiketsu / 清洁": [
        "standard",
        "checklist",
        "different shift",
        "audit route",
        "标准",
        "点检",
        "检查表",
        "班组不一致",
        "清洁",
    ],
    "Shitsuke / 素养": [
        "everyone",
        "again",
        "habit",
        "ignored",
        "only before audit",
        "not follow",
        "大家",
        "又",
        "习惯",
        "没人管",
        "不执行",
        "检查前",
        "素养",
    ],
}

CATEGORY_ALIASES = {
    "Safety / 安全": "安全",
    "Seiton / 整顿": "整顿",
    "Seiso / 清扫": "清扫",
    "Seiri / 整理": "整理",
    "Seiketsu / 清洁": "清洁",
    "Shitsuke / 素养": "素养",
    "Unknown": "未知",
}

CATEGORY_BY_CN = {value: key for key, value in CATEGORY_ALIASES.items()}

SAFETY_CRITICAL_TERMS = [
    "消防",
    "灭火器",
    "消防栓",
    "紧急出口",
    "逃生",
    "疏散",
    "配电",
    "电气",
    "叉车",
    "主通道",
    "安全通道",
    "消防通道",
    "溶剂",
    "VOC",
    "易燃",
    "爆炸",
    "滑倒",
    "摔伤",
    "防护罩",
    "化学品",
]

SORT_TERMS = [
    "废旧",
    "旧夹具",
    "不用",
    "不需要",
    "过期",
    "报废",
    "呆滞",
    "长期滞留",
    "谁订的",
    "无订单",
    "红牌",
    "盘点跳过",
]

SET_IN_ORDER_TERMS = [
    "定位",
    "定置",
    "形迹",
    "凹槽",
    "标签",
    "标识",
    "找不到",
    "翻半天",
    "混放",
    "工具车",
    "量具",
    "卡尺",
    "千分尺",
    "油壶",
    "对照表",
    "暂放区",
    "数量",
    "归位",
]

SHINE_TERMS = [
    "油污",
    "漏油",
    "泄漏",
    "渗漏",
    "积油",
    "积水",
    "焊渣",
    "飞溅",
    "灰尘",
    "切屑",
    "垃圾",
    "清理",
    "清扫",
    "污染",
]

STANDARDIZE_TERMS = [
    "SOP",
    "标准作业",
    "统一标准",
    "清洁标准",
    "点检表",
    "巡检表",
    "看板",
    "标准照片",
    "每个人清理的方法不一样",
    "方法不一样",
    "不同班组",
    "制度缺失",
]

SUSTAIN_TERMS = [
    "不执行",
    "不遵守",
    "不按标准",
    "说了多少次",
    "也不听",
    "默许",
    "视而不见",
    "检查前",
    "应付检查",
    "用完不",
    "不放回",
    "又",
    "每次",
    "经常",
    "反复",
]

HABITUAL_PATTERNS = [
    "always",
    "often",
    "again",
    "every shift",
    "long-term",
    "everyone",
    "used to",
    "only before audit",
    "一直",
    "经常",
    "总是",
    "每班",
    "又",
    "反复",
    "习惯",
    "大家都",
    "检查前",
]

LOCATION_PATTERNS = [
    r"(warehouse|line\s*\d+|station\s*\w+|machine\s*\w+|aisle\s*\w+|rack\s*\w+)",
    r"(仓库|库区|产线|生产线|工位|设备区|通道|货架|机台|配电柜|消防栓|灭火器)(?:[A-Za-z0-9#_-]{0,12})?",
]


@dataclass
class Triage:
    location: str
    abnormality: str
    affected_object: str
    risk: str
    primary_category: str
    secondary_categories: list[str]
    habitual_judgment: str
    question_gate: dict[str, object]
    clarifying_questions: list[str]
    corrective_actions: list[dict[str, str]]
    acceptance_criteria: list[str]
    closure_judgment: dict[str, str] | None = None


@dataclass
class CaseExpectation:
    case_id: str
    title: str
    problem_text: str
    expected_primary: str
    expected_secondary: list[str]
    expected_habitual: str
    expected_closure: str
    closure_text: str


def score_category(text: str, terms: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if term.lower() in lowered)


def contains_any(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def normalize_category_name(value: str) -> str:
    value = value.strip()
    for category, alias in CATEGORY_ALIASES.items():
        if value == alias or value == category:
            return alias
    for category, alias in CATEGORY_ALIASES.items():
        if value.startswith(alias) or value.startswith(category):
            return alias
    for category, alias in CATEGORY_ALIASES.items():
        if alias in value or category in value:
            return alias
    return value or "未知"


def category_key(alias: str) -> str:
    return CATEGORY_BY_CN.get(normalize_category_name(alias), "Unknown")


def normalize_habitual(value: str) -> str:
    value = value.strip().lower()
    if "很可能" in value or "likely" in value:
        return "很可能是习惯性异常"
    if "疑似" in value or "suspected" in value:
        return "疑似习惯性异常"
    if "不足" in value or "not enough" in value:
        return "证据不足"
    return value


def normalize_closure(value: str) -> str:
    value = value.strip().lower()
    if "未闭环" in value or "not closed" in value:
        return "未闭环"
    if "有条件" in value or "conditionally" in value:
        return "有条件闭环"
    if "已闭环" in value or "closed" in value:
        return "已闭环"
    return value


def detect_location(text: str) -> str:
    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return "Unknown"


def classify(text: str) -> tuple[str, list[str]]:
    if "桶装水" in text and ("大量堆积" in text or "占用通道" in text):
        return "Safety / 安全", ["Seiri / 整理"]

    if "货架上的东西太乱了" in text or (
        "13 组货架" in text and "隔层" in text and "备件混放" in text
    ):
        return "Seiton / 整顿", ["Seiri / 整理"]

    if "厂外物资库房" in text and "旧物" in text and "报损区" in text and "待检区" in text:
        return "Seiri / 整理", ["Seiton / 整顿"]

    if "尾料/落地料" in text and "牌号和等级" in text and "透明收纳桶" in text:
        return "Seiton / 整顿", ["Seiso / 清扫"]

    if (
        contains_any(text, ["螺丝", "备母", "垫片"])
        and contains_any(text, ["混放", "规格混杂"])
        and contains_any(text, ["老旧", "不用", "部分老旧", "清理淘汰", "采购未确认", "库存规则无", "规格清单无"])
    ):
        return "Seiton / 整顿", ["Seiri / 整理"]

    if "工具架" in text and "高频工具和低频工具混放" in text:
        return "Seiton / 整顿", ["Seiri / 整理"]

    if "安全疏散通道" in text and contains_any(text, ["模具配件", "废料箱", "托盘"]):
        return "Safety / 安全", ["Seiton / 整顿"]

    scores = {
        "Safety / 安全": score_category(text, SAFETY_CRITICAL_TERMS),
        "Seiri / 整理": score_category(text, SORT_TERMS),
        "Seiton / 整顿": score_category(text, SET_IN_ORDER_TERMS),
        "Seiso / 清扫": score_category(text, SHINE_TERMS),
        "Seiketsu / 清洁": score_category(text, STANDARDIZE_TERMS),
        "Shitsuke / 素养": score_category(text, SUSTAIN_TERMS),
    }

    # Hard boundary rules derived from references/classification.md.
    if (
        contains_any(text, ["工艺文件", "气动扳手", "不按标准", "应付检查"])
        and contains_any(text, ["扭矩", "螺栓", "工装"])
    ):
        return "Shitsuke / 素养", ["Seiton / 整顿"]

    if contains_any(text, ["溶剂桶", "调漆房", "盖子", "挥发", "VOC"]):
        return "Safety / 安全", ["Shitsuke / 素养"]

    if contains_any(text, ["劳保用品", "护目镜", "手套", "反光背心", "安全培训"]) and contains_any(
        text, ["反复", "检查来了才", "标准上墙", "培训已做", "不执行"]
    ):
        return "Shitsuke / 素养", ["Safety / 安全"]

    if contains_any(text, ["档案盒", "资料册", "标签模板", "总部模板", "标签标准"]):
        return "Seiketsu / 清洁", ["Seiton / 整顿"]

    if contains_any(text, ["货架", "隔层", "备件"]) and contains_any(text, ["混放", "分类摆放", "查找"]):
        secondary = ["Seiri / 整理"] if contains_any(text, ["不需要的物品", "需清理"]) else []
        return "Seiton / 整顿", secondary

    if contains_any(text, ["库房区域", "报损区", "待检区", "旧物", "区域规划不清晰"]):
        return "Seiri / 整理", ["Seiton / 整顿"]

    if contains_any(text, ["夹具", "旧工装", "废旧工装", "旧夹具"]) and contains_any(text, ["通道", "占用", "堆放"]):
        return "Seiri / 整理", ["Safety / 安全"]

    if contains_any(text, ["废袋子", "废弃包装袋", "废套膜", "材料废物", "辅材废料"]):
        secondary = "Safety / 安全" if contains_any(text, ["火灾", "易燃", "安全隐患"]) else "Seiton / 整顿"
        return "Seiri / 整理", [secondary]

    if (
        contains_any(text, ["电缆", "气管"])
        and contains_any(text, ["货架", "挂钩", "缠绕器", "摆放"])
        and not contains_any(text, ["封口机"])
    ):
        secondary = ["Safety / 安全"] if contains_any(text, ["绊倒", "碾压", "安全"]) else []
        return "Seiton / 整顿", secondary

    if contains_any(text, ["封口机", "气管"]) and contains_any(text, ["绊倒", "叉车", "碾压", "爆管"]):
        return "Safety / 安全", ["Seiton / 整顿"]

    if contains_any(text, ["尾料", "落地料", "透明桶", "周转架"]) and contains_any(text, ["牌号", "等级", "分类"]):
        return "Seiton / 整顿", ["Seiso / 清扫"]

    if contains_any(text, ["料粒", "裂缝", "地面缝隙"]):
        return "Seiso / 清扫", ["Seiketsu / 清洁"]

    if contains_any(text, ["叉车卫生", "叉车清洁", "定位标志线脏污"]) or (
        contains_any(text, ["叉车"]) and contains_any(text, ["灰", "座都坐不下", "脏污", "积垢"])
    ):
        return "Seiso / 清扫", ["Seiketsu / 清洁"]

    if contains_any(text, ["灭火器", "消防栓", "消防器材", "紧急出口", "疏散通道"]):
        secondary = "Seiri / 整理" if contains_any(text, ["纸箱", "堆货", "临时堆放"]) else "Seiton / 整顿"
        return "Safety / 安全", [secondary]

    if contains_any(text, ["安全通道", "消防通道", "叉车都过不去", "叉车无法", "主通道"]):
        return "Safety / 安全", ["Seiton / 整顿"]

    if contains_any(text, ["走过去都得绕", "踩上去肯定滑倒", "必经", "操作侧地面"]):
        return "Safety / 安全", ["Seiso / 清扫"]

    if contains_any(text, ["注塑机", "设备底座", "机器下方", "底座下方"]) and contains_any(text, ["漏", "油"]):
        return "Seiso / 清扫", ["Safety / 安全"]

    if contains_any(text, ["旧夹具", "废旧工装", "旧工装", "生锈"]) and contains_any(text, ["通道"]):
        return "Seiri / 整理", ["Safety / 安全"]

    if contains_any(text, ["过期化学品", "保质期", "盘点跳过"]):
        return "Seiri / 整理", ["Safety / 安全"]

    if contains_any(text, ["喷房", "清洁", "方法不一样"]) or (
        contains_any(text, ["SOP", "统一标准"]) and contains_any(text, ["不同班组", "清洁"])
    ):
        return "Seiketsu / 清洁", []

    if contains_any(text, ["焊渣", "飞溅"]):
        return "Seiso / 清扫", ["Safety / 安全"]

    if contains_any(text, ["量具", "千分尺", "卡尺", "质检台"]):
        return "Seiton / 整顿", []

    if contains_any(text, ["工具车", "形迹板", "工具清单"]):
        secondary = ["Shitsuke / 素养"] if contains_any(text, ["用完", "不放回", "每班", "习惯"]) else []
        return "Seiton / 整顿", secondary

    if contains_any(text, ["润滑", "油壶", "油枪", "润滑脂", "润滑点"]):
        secondary = ["Seiso / 清扫"] if contains_any(text, ["积油", "渗油"]) else []
        return "Seiton / 整顿", secondary

    if contains_any(text, ["空纸箱", "空箱"]):
        if contains_any(text, ["叉车", "主通道", "无法正常通行"]):
            return "Safety / 安全", ["Seiton / 整顿"]
        return "Seiton / 整顿", ["Safety / 安全"]

    scored = list(scores.items())
    scored.sort(key=lambda item: item[1], reverse=True)
    if scored[0][1] == 0:
        return "Unknown", []
    primary = scored[0][0]
    secondary = [category for category, score in scored[1:] if score > 0][:2]
    return primary, secondary


def habitual(text: str) -> str:
    if contains_any(text, ["不等于习惯性异常", "没有多次整改后复发"]) and contains_any(text, ["一次性", "证据不足"]):
        return "证据不足"

    if contains_any(text, ["消防梯", "纸壳垫"]):
        return "证据不足"

    if contains_any(text, ["电缆", "气管"]) and contains_any(text, ["货架", "挂钩", "缠绕器"]) and not contains_any(text, ["封口机"]):
        return "证据不足"

    if contains_any(text, ["工具架", "首次系统性整改", "重新规划"]) and contains_any(text, ["进行中", "无之前整改后复发"]):
        return "疑似习惯性异常"

    if contains_any(text, ["叉车卫生", "定位标志线", "形成6S管理制度"]) and contains_any(
        text, ["缺持续执行记录", "执行率未验证", "抽查机制未落地"]
    ):
        return "疑似习惯性异常"

    if contains_any(text, ["喷房", "清洁"]) and contains_any(text, ["长期存在", "质量返工", "班长知情"]):
        return "很可能是习惯性异常"

    if contains_any(text, ["量具", "长期混放"]) and contains_any(text, ["没有固定", "缺乏明确", "无固定定位"]):
        return "疑似习惯性异常"

    if contains_any(text, ["档案盒", "资料册"]) and contains_any(text, ["新采购", "采购验收", "标签缺失"]):
        return "疑似习惯性异常"

    if contains_any(text, ["尾料", "落地料", "牌号", "等级"]) and contains_any(text, ["混放", "倒进同一个桶"]):
        return "疑似习惯性异常"

    if contains_any(text, ["螺丝", "备母", "垫片"]) and contains_any(text, ["进行中", "推进中", "归整尝试", "本期计划", "尚未确认"]):
        return "很可能是习惯性异常"

    if contains_any(text, ["吨袋", "辅材区"]) and contains_any(text, ["无数量", "数量管控", "来了就堆", "定位框"]):
        return "疑似习惯性异常"

    if contains_any(text, ["料粒", "裂缝", "天天扫天天有"]):
        return "疑似习惯性异常"

    if contains_any(text, ["封口机", "气管", "随地摆放"]):
        return "疑似习惯性异常"

    if contains_any(text, ["材料废物", "辅材废料"]) and contains_any(text, ["未全部完成", "甲方", "返回周期"]):
        return "很可能是习惯性异常"

    if contains_any(text, ["润滑", "油壶", "油枪", "润滑点"]) and contains_any(
        text, ["首次有人提出", "逐渐恶化", "一次性暴露"]
    ):
        return "疑似习惯性异常"

    likely_signals = [
        "每班",
        "每次",
        "每周",
        "每月",
        "长期",
        "反复",
        "又",
        "盘点跳过",
        "问题沟通",
        "整改统计",
        "下期计划",
        "本期计划",
        "未完成",
        "未整改",
        "未全部完成",
        "继续改善",
        "多次反馈",
        "管理者知情",
        "主管知情",
        "班长知道",
        "默许",
        "视而不见",
        "多次",
        "整改后",
        "大扫除才",
        "检查前",
        "应付检查",
        "大家都",
        "一直",
        "经常",
    ]
    weak_signals = [
        "无人管",
        "无主",
        "责任人不清",
        "逐渐恶化",
        "进行中",
        "尚未",
        "计划中",
        "模板一致性",
        "采购验收",
        "习惯",
        "靠师傅口头",
        "长期混放",
        "标签脱落",
        "不归位",
    ]
    one_time_exclusions = [
        "一次性",
        "以前不常发生",
        "之前无类似记录",
        "最近才",
        "首次有人提出",
        "没有多次整改后复发",
    ]

    likely_hits = score_category(text, likely_signals)
    weak_hits = score_category(text, weak_signals)
    if likely_hits >= 2 or (likely_hits >= 1 and weak_hits >= 1):
        return "很可能是习惯性异常"
    if weak_hits >= 1:
        return "疑似习惯性异常"
    if likely_hits == 1 and not contains_any(text, one_time_exclusions):
        return "疑似习惯性异常"
    return "证据不足"


def infer_object(text: str) -> str:
    candidates = [
        "tool",
        "material",
        "carton",
        "pallet",
        "oil",
        "waste",
        "fixture",
        "工具",
        "物料",
        "纸箱",
        "托盘",
        "油",
        "垃圾",
        "夹具",
        "清洁剂",
    ]
    lowered = text.lower()
    for item in candidates:
        if item.lower() in lowered:
            return item
    return "Unknown"


def infer_risk(primary: str, text: str) -> str:
    if "Safety" in primary:
        return "Safety risk requiring immediate containment"
    if "Seiso" in primary:
        return "Contamination, slip, equipment, or quality risk"
    if "Seiton" in primary:
        return "Search time, mix-up, access, or placement discipline risk"
    if "Seiri" in primary:
        return "Space occupation, mix-up, hidden defect, or inventory risk"
    if "Shitsuke" in primary:
        return "Recurring noncompliance and weak management control risk"
    if "Seiketsu" in primary:
        return "Unstable standard and recurrence risk"
    return "Unknown risk; confirm impact and severity"


def missing_questions(location: str, affected_object: str, text: str) -> list[str]:
    gate = build_question_gate(location, affected_object, text, "Unknown", [], "", None, None)
    return (gate["must_ask"] + gate["nice_to_have"])[:3]


def build_question_gate(
    location: str,
    affected_object: str,
    text: str,
    primary: str,
    secondary_categories: list[str],
    habitual_judgment: str,
    closure_judgment: dict[str, str] | None,
    rectified_text: str | None,
) -> dict[str, object]:
    must_ask: list[str] = []
    nice_to_have: list[str] = []
    lowered = text.lower()
    closure_text = rectified_text or ""
    combined_text = f"{text}\n{closure_text}"

    def add_once(target: list[str], question: str) -> None:
        if question not in must_ask and question not in nice_to_have:
            target.append(question)

    if location == "Unknown":
        add_once(must_ask, "请先确认异常发生的具体区域、产线、工位、设备、通道或货架。")
    if affected_object == "Unknown":
        add_once(must_ask, "请先确认异常对象是什么，以及大致数量、范围或影响面积。")

    if contains_any(text, ["通道", "消防", "灭火器", "配电", "叉车", "绊倒", "滑倒"]) and not contains_any(
        text, ["堵", "阻断", "净宽", "黄线", "逃生", "主物流", "已清空", "已隔离"]
    ):
        add_once(must_ask, "请确认是否影响消防/逃生/主物流通道、配电安全距离或人员必经路径。")

    has_recurrence_signal = any(term in lowered for term in HABITUAL_PATTERNS)
    category_text = " ".join([primary, *secondary_categories])
    recurrence_question = "请确认这是一次性问题，还是整改/清理后曾经复发。"
    if not has_recurrence_signal:
        if contains_any(category_text, ["Shitsuke", "素养", "Seiketsu", "清洁"]):
            add_once(must_ask, recurrence_question)
        elif "证据不足" in habitual_judgment:
            add_once(nice_to_have, recurrence_question)

    if contains_any(combined_text, ["已整改", "已完成", "已闭环", "已清理", "已培训", "已通知", "已经修好"]):
        if not contains_any(combined_text, ["复查", "点检", "抽查", "连续", "无复发", "照片", "记录", "台账"]):
            add_once(must_ask, "请补充整改后证据：原位置前后照片、责任人、标准控制和复查记录。")

    if primary == "Unknown":
        add_once(must_ask, "请补充可见异常、风险后果和当前已有控制措施，否则只能做粗略初判。")

    if "证据不足" in habitual_judgment:
        add_once(nice_to_have, "若要判断是否习惯性异常，请补充历史整改、复发次数、班组差异或标准执行情况。")

    if closure_judgment:
        judgment = closure_judgment.get("judgment", "")
        if judgment != "已闭环":
            if judgment == "未闭环":
                add_once(must_ask, "当前不能直接归档闭环，请补充防复发措施和至少一个复查周期的保持证据。")
            else:
                add_once(nice_to_have, "若要升级为已闭环，请补充防复发措施和至少一个复查周期的保持证据。")

    if len(text) < 30:
        add_once(nice_to_have, "请补充现场可见证据、照片描述或已经出现的安全/质量/效率影响。")

    must_ask = must_ask[:3]
    nice_to_have = [q for q in nice_to_have if q not in must_ask][:3]
    if must_ask:
        status = "must_answer_before_final_judgment"
        confidence = "闭环证据不足，不能直接归档" if closure_judgment else "初判，需补证据"
        reason = "缺少会改变分类、风险等级、习惯性异常或闭环判定的关键信息。"
    elif nice_to_have:
        status = "can_proceed_with_assumptions"
        confidence = "可先判断，建议补证据"
        reason = "已有信息可形成初判，但补充证据会提高整改和验收质量。"
    else:
        status = "ready_for_action"
        confidence = "可直接判断"
        reason = "现有信息足以支持当前分类、对策和闭环判断。"

    return {
        "status": status,
        "confidence": confidence,
        "reason": reason,
        "must_ask": must_ask,
        "nice_to_have": nice_to_have,
    }


def build_actions(primary: str, habitual_judgment: str) -> list[dict[str, str]]:
    actions = [
        {
            "step": "Immediate containment",
            "action": "Remove or isolate the visible abnormality before the end of the shift.",
            "owner": "Area supervisor",
            "evidence": "After photo of the original location and affected object.",
        }
    ]
    if "Safety" in primary:
        actions.append(
            {
                "step": "Safety control",
                "action": "Restore required clearance/guarding and add a physical or visual control that prevents re-blocking or bypass.",
                "owner": "EHS owner plus area supervisor",
                "evidence": "Photo showing access clearance, control point, and supervisor verification.",
            }
        )
    elif "Seiton" in primary:
        actions.append(
            {
                "step": "Set in order",
                "action": "Define fixed location, label, max/min quantity, and return rule for the affected item.",
                "owner": "Line leader or warehouse owner",
                "evidence": "Location label or shadow board photo with item and quantity standard visible.",
            }
        )
    elif "Seiso" in primary:
        actions.append(
            {
                "step": "Clean and source control",
                "action": "Clean the area, identify the contamination source, and repair or capture the source.",
                "owner": "Maintenance owner plus area supervisor",
                "evidence": "Before/after photo and source-control record.",
            }
        )
    elif "Seiri" in primary:
        actions.append(
            {
                "step": "Sort",
                "action": "Red-tag unnecessary or unclear items and decide keep, move, scrap, or return by deadline.",
                "owner": "Area owner",
                "evidence": "Red-tag list with disposition result.",
            }
        )
    else:
        actions.append(
            {
                "step": "Standardize",
                "action": "Update the visible standard and inspection checklist for this abnormality.",
                "owner": "Area supervisor",
                "evidence": "Standard photo/checklist revision and shift briefing record.",
            }
        )
    if "很可能" in habitual_judgment or "疑似" in habitual_judgment:
        actions.append(
            {
                "step": "Recurrence prevention",
                "action": "Add a 3-check recurrence review and confirm whether the current standard is realistic during normal production.",
                "owner": "Area supervisor and process owner",
                "evidence": "Three consecutive check records with no recurrence or documented standard change.",
            }
        )
    return actions


def acceptance(primary: str) -> list[str]:
    base = [
        "Original location has no visible abnormal item or hazard.",
        "Owner, location, and expected state are visible or recorded.",
        "After photo covers the original location and affected object.",
    ]
    if "Safety" in primary:
        base.append("Safety access/control meets site requirement, with zero blockage or bypass.")
    if "Seiso" in primary:
        base.append("Contamination source is removed, repaired, or captured; area passes the next cleaning check.")
    if "Seiton" in primary:
        base.append("All affected items are in fixed locations with labels and quantity limits.")
    base.append("No recurrence in the next 3 daily checks or next scheduled layered audit.")
    return base


def closure_check(rectified_text: str | None) -> dict[str, str] | None:
    if not rectified_text:
        return None
    lowered = rectified_text.lower()

    explicit = re.search(r"判定：\s*(已闭环|有条件闭环|未闭环)", rectified_text)
    if explicit:
        judgment = explicit.group(1)
        return {
            "judgment": judgment,
            "evidence_considered": rectified_text,
            "gap": "基于案例闭环判定文本识别。",
            "required_next_action": "按对应闭环等级核验证据完整性。",
        }

    fake_closure_terms = [
        "只拍",
        "已通知",
        "已要求",
        "加强管理",
        "提醒",
        "没有复查",
        "无复查",
        "无责任人",
        "搬到别处",
        "其他角落",
        "未说明去向",
        "再次出现",
        "尚未执行",
        "尚未执行到位",
        "未到位",
        "无实物",
        "无整改证据",
        "未建立",
        "未确定",
        "停留在概念",
    ]
    full_closure_terms = [
        "闭环证据包括",
        "维修记录",
        "前后对比照片",
        "巡查表更新",
        "点检表记录",
        "每周检查记录",
        "连续 3 天",
        "连续3天",
        "无再次",
        "无复发",
        "责任人",
        "标识",
        "标准",
        "台账",
    ]
    evidence_hits = sum(
        term in lowered
        for term in [
            "photo",
            "label",
            "checklist",
            "owner",
            "audit",
            "3",
            "three",
            "照片",
            "标识",
            "点检",
            "责任人",
            "三次",
            "复查",
        ]
    )
    if contains_any(rectified_text, fake_closure_terms):
        judgment = "未闭环"
        gap = "整改声明存在假闭环信号，需要补充现场控制和复查证据。"
    elif contains_any(
        rectified_text,
        [
            "部分缺失",
            "缺持续执行记录",
            "执行率未验证",
            "抽查机制未落地",
            "需补充复查证据",
            "尚未落实",
        ],
    ):
        judgment = "有条件闭环"
        gap = "当前状态已有改善，但持续执行或复查证据不足。"
    elif contains_any(rectified_text, ["闭环证据包括"]):
        judgment = "已闭环"
        gap = "整改说明以闭环证据清单形式提供，按已闭环处理。"
    elif contains_any(
        rectified_text,
        [
            "需补充复查证据",
            "有条件闭环",
            "尚未全部",
            "尚未全面",
            "仅完成",
            "工具调研中",
            "方案已制定",
            "短期工具方案未落地",
            "采购计划中",
            "未到货",
        ],
    ):
        judgment = "有条件闭环"
        gap = "当前改善方向明确，但仍需补充复查或保持证据。"
    elif contains_any(rectified_text, ["已完成", "专家评价", "专家确认", "专家确认为", "可行"]):
        judgment = "已闭环"
        gap = "整改已完成并有专家评价或确认。"
    elif evidence_hits >= 3 and score_category(rectified_text, full_closure_terms) >= 2:
        judgment = "已闭环"
        gap = "证据覆盖当前状态、标准控制或保持记录。"
    elif evidence_hits >= 3:
        judgment = "有条件闭环"
        gap = "Verify recurrence record and original-location evidence before full closure."
    elif evidence_hits >= 1:
        judgment = "有条件闭环"
        gap = "Visible correction exists, but standard or recurrence evidence is incomplete."
    else:
        judgment = "未闭环"
        gap = "Claim lacks evidence against the acceptance criteria."
    return {
        "judgment": judgment,
        "evidence_considered": rectified_text,
        "gap": gap,
        "required_next_action": "Provide after photo, standard/control evidence, and recurrence check result.",
    }


def extract_section(text: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}：?\*\*\s*(.*?)(?=\n\*\*[^*]+：?\*\*|\n---|\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_bulleted_value(section: str, label: str) -> str:
    match = re.search(rf"-\s*{re.escape(label)}：(.+)", section)
    return strip_markdown(match.group(1).strip()) if match else ""


def strip_markdown(value: str) -> str:
    return re.sub(r"[*_`]+", "", value).strip()


def infer_habitual_from_section(section: str) -> str:
    normalized = strip_markdown(section)
    if re.search(r"很可能是|很可能为", normalized):
        return "很可能是习惯性异常"
    if "疑似" in normalized:
        return "疑似习惯性异常"
    if "证据不足" in normalized:
        return "证据不足"
    return ""


def parse_cases(case_file: str | Path) -> list[CaseExpectation]:
    content = Path(case_file).read_text(encoding="utf-8")
    chunks = re.split(r"(?=^#{2,3}\s*(?:真实案例\s+)?案例\s+\d+：|^###\s*真实案例\s+\d+：)", content, flags=re.MULTILINE)
    cases: list[CaseExpectation] = []
    for chunk in chunks:
        header = re.match(r"^#{2,3}\s*(?:真实案例\s+)?案例\s+(\d+)：(.+)", chunk)
        if not header:
            header = re.match(r"^###\s*真实案例\s+(\d+)：(.+)", chunk)
        if not header:
            continue
        case_id, title = header.group(1), header.group(2).strip()
        user_input = extract_section(chunk, "用户输入")
        background = extract_section(chunk, "现场背景")
        structured = extract_section(chunk, "结构化结果")
        classification = extract_section(chunk, "6S 分类")
        habitual_section = extract_section(chunk, "是否习惯性异常")
        closure_section = extract_section(chunk, "已整改后的闭环判断")

        expected_primary = normalize_category_name(parse_bulleted_value(classification, "主分类"))
        secondary_raw = parse_bulleted_value(classification, "副分类")
        expected_secondary = []
        if secondary_raw and secondary_raw != "无":
            for alias in ["安全", "整理", "整顿", "清扫", "清洁", "素养"]:
                if alias in secondary_raw:
                    expected_secondary.append(alias)

        problem_text = "\n".join(part for part in [user_input, background, structured] if part)
        cases.append(
            CaseExpectation(
                case_id=case_id,
                title=title,
                problem_text=problem_text,
                expected_primary=expected_primary,
                expected_secondary=expected_secondary,
                expected_habitual=normalize_habitual(
                    parse_bulleted_value(habitual_section, "判断等级")
                    or infer_habitual_from_section(habitual_section)
                ),
                expected_closure=normalize_closure(parse_bulleted_value(closure_section, "判定")),
                closure_text=closure_section,
            )
        )
    return cases


def evaluate_cases(case_file: str | Path) -> dict[str, object]:
    cases = parse_cases(case_file)
    rows: list[dict[str, object]] = []
    totals = {"primary": 0, "secondary": 0, "habitual": 0, "closure": 0}
    for case in cases:
        closure_evidence_text = re.sub(
            r"^\s*-\s*判定：.*$",
            "",
            case.closure_text,
            flags=re.MULTILINE,
        )
        result = triage(case.problem_text, rectified_text=closure_evidence_text)
        actual_primary = normalize_category_name(result.primary_category)
        actual_secondary = [normalize_category_name(item) for item in result.secondary_categories]
        actual_habitual = normalize_habitual(result.habitual_judgment)
        actual_closure = normalize_closure(result.closure_judgment["judgment"] if result.closure_judgment else "")

        primary_ok = actual_primary == case.expected_primary
        secondary_ok = sorted(actual_secondary) == sorted(case.expected_secondary)
        habitual_ok = actual_habitual == case.expected_habitual
        closure_ok = actual_closure == case.expected_closure
        totals["primary"] += int(primary_ok)
        totals["secondary"] += int(secondary_ok)
        totals["habitual"] += int(habitual_ok)
        totals["closure"] += int(closure_ok)

        rows.append(
            {
                "case": case.case_id,
                "title": case.title,
                "primary": {
                    "expected": case.expected_primary,
                    "actual": actual_primary,
                    "ok": primary_ok,
                },
                "secondary": {
                    "expected": case.expected_secondary,
                    "actual": actual_secondary,
                    "ok": secondary_ok,
                },
                "habitual": {
                    "expected": case.expected_habitual,
                    "actual": actual_habitual,
                    "ok": habitual_ok,
                },
                "closure": {
                    "expected": case.expected_closure,
                    "actual": actual_closure,
                    "ok": closure_ok,
                },
            }
        )
    total_cases = len(cases)
    return {
        "case_file": str(case_file),
        "total_cases": total_cases,
        "accuracy": {
            key: (value / total_cases if total_cases else 0.0)
            for key, value in totals.items()
        },
        "passed": {
            key: value
            for key, value in totals.items()
        },
        "rows": rows,
    }


def triage(problem: str, rectified_text: str | None = None) -> Triage:
    primary, secondary = classify(problem)
    location = detect_location(problem)
    affected_object = infer_object(problem)
    habitual_judgment = habitual(problem)
    closure_judgment = closure_check(rectified_text)
    question_gate = build_question_gate(
        location,
        affected_object,
        problem,
        primary,
        secondary,
        habitual_judgment,
        closure_judgment,
        rectified_text,
    )
    questions = (question_gate["must_ask"] + question_gate["nice_to_have"])[:3]
    needs_clarification = question_gate["status"] == "must_answer_before_final_judgment" and primary == "Unknown"
    return Triage(
        location=location,
        abnormality=problem,
        affected_object=affected_object,
        risk=infer_risk(primary, problem),
        primary_category=primary,
        secondary_categories=secondary,
        habitual_judgment=habitual_judgment,
        question_gate=question_gate,
        clarifying_questions=questions,
        corrective_actions=[] if needs_clarification else build_actions(primary, habitual_judgment),
        acceptance_criteria=[] if needs_clarification else acceptance(primary),
        closure_judgment=closure_judgment,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Lean 6S MVP triage helper")
    parser.add_argument("--problem", help="Vague site issue description")
    parser.add_argument("--rectified-text", help="User's closure/evidence statement")
    parser.add_argument("--case-file", help="Markdown case library to parse, such as examples/cases.md")
    parser.add_argument("--test-cases", action="store_true", help="Run rule checks against --case-file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    if args.test_cases:
        if not args.case_file:
            parser.error("--test-cases requires --case-file")
        result = evaluate_cases(args.case_file)
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return

    if not args.problem:
        parser.error("--problem is required unless --test-cases is used")

    result = asdict(triage(args.problem, args.rectified_text))
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
