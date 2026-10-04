# -*- coding: utf-8 -*-
"""
抖音报送格式工具 —— 解析核心（Win32 重写版）
支持：舆情通一键复制文本、抖音/快手/小红书分享文本
"""

import datetime
import re

VERSION = "9.3"

# ===================== 报送标签 =====================

TAG_GROUPS = [
    ("涉稳", [
        ("2.1", "涉稳-煽动集体维权"),
        ("2.2", "涉稳-过激维权信访"),
        ("2.3", "涉稳-非组织化大规模聚集"),
        ("2.4", "涉稳-其他影响社会稳定的突出情况"),
        ("2.5", "涉稳-涉及专项行动"),
    ]),
    ("涉警", [
        ("3.1", "涉警-个人极端行为"),
        ("3.2", "涉警-重大刑事案件"),
        ("3.3", "涉警-敏感案件"),
        ("3.4", "涉警-执法监督"),
        ("3.5", "涉警-涉及专项行动案件"),
        ("3.6", "涉警-网络谣言"),
        ("3.7", "涉警-引流摆拍"),
    ]),
    ("涉未成年人", [
        ("4.1", "涉未成年人-侵害事件"),
        ("4.2", "涉未成年人-违法犯罪"),
        ("4.3", "涉未成年人-非正常死亡"),
        ("4.4", "涉未成年人-失联"),
        ("4.5", "涉未成年人-涉校事故"),
    ]),
    ("涉公共安全", [
        ("5.1", "涉公共安全-交通事故"),
        ("5.2", "涉公共安全-安全事故"),
        ("5.3", "涉公共安全-人员失联"),
        ("5.4", "涉公共安全-非正常死亡"),
    ]),
    ("涉豫", [
        ("6.1", "涉豫-民生问题"),
        ("6.2", "涉豫-网红企业"),
        ("6.3", "涉豫-三农问题"),
        ("6.4", "涉豫-重大考试"),
        ("6.5", "涉豫-换届选举"),
    ]),
]

ALL_TAGS = []
TAG_SEQ_MAP = {}
for _cat, _items in TAG_GROUPS:
    for _seq, _tag in _items:
        ALL_TAGS.append((_seq, _tag))
        TAG_SEQ_MAP[_tag] = _seq

TAG_DESCRIPTIONS = {
    "2.2": "为达诉求，实施游行示威、堵路堵门等扰乱治安秩序行为",
    "2.3": "夜骑、杀猪宴等",
    "3.1": "扬言或实施后在网络上曝光",
    "3.2": "八大罪，敏感视频图片流出及网络炒作命案细节",
    "3.3": "少数人群、弱势群体、出租外卖特殊人群聚集，公共场所打架伤人",
    "3.4": "报道、反映公安违法违纪情况，及作风问题等易引发炒作的突出情况",
    "3.5": "特定时段，如过年期间盗窃案、4.15关注飙车炸街等",
    "3.7": "具有社会危害性的恶意挑唆社会矛盾情绪行为，及实施违反公序良俗行为等",
    "4.1": "残忍手段等侵害未成年权益的情况",
    "4.2": "飙车炸街、拉门撬锁、结党结社等违反法律法规及部门规章的相关情况",
    "4.3": "猝死、跳楼跳河等自伤自残情况",
    "4.5": "校内发生踩踏、火灾、食品安全等，校车交通事故，或学生集体喊楼、撕书、张贴异见标语等",
    "5.1": "亡人、起火、爆炸、连环相撞等现场较为惨烈的情况",
    "5.2": "发生火灾爆炸、极端天气、道路楼房坍塌等事故",
    "5.3": "成年人失联走失",
    "5.4": "成年人自伤自残等情况",
    "6.1": "环保、教育、金融、就业、医疗、养老、住房、出行等重点领域",
    "6.2": "造谣抹黑，恶意炒作攻击我省著名企业及法人的情况",
    "6.3": "毁耕、毁青、假种子化肥、烂场雨等危害农业农村农民正常生产生活秩序的情况",
    "6.5": "村两委、小组长换届的相关情况",
}

# ===================== 河南地名 =====================

HENAN_CITIES = [
    "安阳", "鹤壁", "焦作", "济源", "开封", "漯河", "洛阳", "南阳",
    "平顶山", "濮阳", "三门峡", "商丘", "新乡", "信阳", "许昌",
    "郑州", "周口", "驻马店",
]

COUNTY_TO_CITY = {
    "中牟": "郑州", "巩义": "郑州", "荥阳": "郑州", "新密": "郑州", "新郑": "郑州", "登封": "郑州",
    "中原": "郑州", "二七": "郑州", "管城": "郑州", "金水": "郑州", "上街": "郑州", "惠济": "郑州",
    "杞县": "开封", "通许": "开封", "尉氏": "开封", "兰考": "开封", "祥符": "开封",
    "龙亭": "开封", "顺河": "开封", "鼓楼": "开封", "禹王台": "开封",
    "新安": "洛阳", "栾川": "洛阳", "嵩县": "洛阳", "汝阳": "洛阳", "宜阳": "洛阳",
    "洛宁": "洛阳", "伊川": "洛阳", "偃师": "洛阳", "孟津": "洛阳",
    "老城": "洛阳", "西工": "洛阳", "瀍河": "洛阳", "涧西": "洛阳", "吉利": "洛阳", "洛龙": "洛阳",
    "宝丰": "洛阳", "叶县": "平顶山", "鲁山": "平顶山", "郏县": "平顶山",
    "舞钢": "平顶山", "汝州": "平顶山",
    "新华": "平顶山", "卫东": "平顶山", "石龙": "平顶山", "湛河": "平顶山",
    "汤阴": "安阳", "滑县": "安阳", "内黄": "安阳", "林州": "安阳",
    "文峰": "安阳", "北关": "安阳", "殷都": "安阳", "龙安": "安阳", "安阳县": "安阳",
    "浚县": "鹤壁", "淇县": "鹤壁",
    "鹤山": "鹤壁", "山城": "鹤壁", "淇滨": "鹤壁",
    "获嘉": "新乡", "原阳": "新乡", "延津": "新乡", "封丘": "新乡",
    "长垣": "新乡", "卫辉": "新乡", "辉县": "新乡",
    "红旗": "新乡", "卫滨": "新乡", "凤泉": "新乡", "牧野": "新乡", "新乡县": "新乡",
    "修武": "焦作", "博爱": "焦作", "武陟": "焦作", "温县": "焦作",
    "沁阳": "焦作", "孟州": "焦作",
    "解放": "焦作", "中站": "焦作", "马村": "焦作", "山阳": "焦作",
    "清丰": "濮阳", "南乐": "濮阳", "范县": "濮阳", "台前": "濮阳",
    "华龙": "濮阳", "濮阳县": "濮阳",
    "鄢陵": "许昌", "襄城": "许昌", "禹州": "许昌", "长葛": "许昌",
    "魏都": "许昌", "建安": "许昌",
    "舞阳": "漯河", "临颍": "漯河",
    "源汇": "漯河", "郾城": "漯河", "召陵": "漯河",
    "渑池": "三门峡", "卢氏": "三门峡", "义马": "三门峡", "灵宝": "三门峡", "陕州": "三门峡",
    "湖滨": "三门峡",
    "南召": "南阳", "方城": "南阳", "西峡": "南阳", "镇平": "南阳", "内乡": "南阳",
    "淅川": "南阳", "社旗": "南阳", "唐河": "南阳", "新野": "南阳", "桐柏": "南阳", "邓州": "南阳",
    "宛城": "南阳", "卧龙": "南阳",
    "民权": "商丘", "睢县": "商丘", "宁陵": "商丘", "柘城": "商丘",
    "虞城": "商丘", "夏邑": "商丘", "永城": "商丘",
    "梁园": "商丘", "睢阳": "商丘",
    "罗山": "信阳", "光山": "信阳", "新县": "信阳", "商城": "信阳",
    "固始": "信阳", "潢川": "信阳", "淮滨": "信阳", "息县": "信阳",
    "浉河": "信阳", "平桥": "信阳",
    "扶沟": "周口", "西华": "周口", "商水": "周口", "沈丘": "周口",
    "郸城": "周口", "太康": "周口", "鹿邑": "周口", "项城": "周口", "淮阳": "周口",
    "川汇": "周口",
    "西平": "驻马店", "上蔡": "驻马店", "平舆": "驻马店", "正阳": "驻马店",
    "确山": "驻马店", "泌阳": "驻马店", "汝南": "驻马店", "遂平": "驻马店", "新蔡": "驻马店",
    "驿城": "驻马店",
    "济源": "济源",
}

# 修正宝丰（误写为洛阳）
COUNTY_TO_CITY["宝丰"] = "平顶山"

# 河南主要乡镇/街道 -> 所属地市
TOWN_TO_CITY = {
    # 驻马店
    "古吕": "驻马店", "砖店": "驻马店", "陈店": "驻马店", "佛阁寺": "驻马店", "练村": "驻马店",
    # 周口
    "太昊": "周口", "弦歌": "周口",
}


# ===================== 一键复制文本解析 =====================

FIELD_PATTERN = re.compile(
    r"^(摘要|原文链接|来源网站|发布时间|作者|账号ID|抖音号)[：:]\s*(.*)$"
)


def parse_fields(text):
    fields = {}
    for line in text.splitlines():
        line = line.strip()
        m = FIELD_PATTERN.match(line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def format_time(raw):
    if not raw:
        return ""
    m = re.match(r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日\s]+(\d{1,2}):(\d{1,2})", raw)
    if m:
        return "%d月%d日%02d时%02d分" % (
            int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
    m = re.match(r"(\d{1,2})[-/月](\d{1,2})[日\s]+(\d{1,2}):(\d{1,2})", raw)
    if m:
        return "%d月%d日%02d时%02d分" % (
            int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
    return raw


def detect_city_from_text(text):
    """从全文搜索：先地市，再区县，再乡镇，最后省份"""
    for m in re.findall(r"([\u4e00-\u9fff]{2,4})市", text):
        if m in HENAN_CITIES:
            return m
    for c in HENAN_CITIES:
        if c in text:
            return c
    for county, mc in COUNTY_TO_CITY.items():
        if county in text:
            return mc
    for town, mc in TOWN_TO_CITY.items():
        if town in text:
            return mc
    if "河南" in text:
        return "河南"
    return ""


def is_punctuation(ch):
    """判断字符是否为标点/符号（非汉字字母数字）"""
    if ch.isalnum():
        return True
    if "\u4e00" <= ch <= "\u9fff":
        return True
    return False


def make_summary_part(summary):
    """摘要末尾只要是标点就不补句号"""
    if not summary:
        return ""
    if not is_punctuation(summary[-1]):
        return summary
    return summary + "。"


# ===================== 分享文本解析 =====================

def convert_share_text(text, city_override=None):
    now = datetime.datetime.now()
    time_str = "%d月%d日%d时%02d分" % (now.month, now.day, now.hour, now.minute)
    city = city_override.strip() if city_override and city_override.strip() else "河南"

    if "kuaishou.com" in text:
        platform = "快手"
        url_match = re.search(r"(https?://[^\s]+)", text)
        url = url_match.group(1) if url_match else ""
        author_match = re.search(r"@(.+?)\s*发了一个快手作品", text)
        author = author_match.group(1).strip() if author_match else ""
        douyin_id = ""
        summary = ""
    elif "xiaohongshu.com" in text or "xhslink.com" in text:
        platform = "小红书"
        url_match = re.search(r"(https?://[^\s]+)", text)
        url = url_match.group(1) if url_match else ""
        author = ""
        douyin_id = ""
        summary = ""
    else:
        platform = "抖音"
        url_match = re.search(r"(https?://[^\s]+)", text)
        url = url_match.group(1) if url_match else ""
        author_match = re.search(r"【(.+?)的作品】", text)
        author = author_match.group(1).strip() if author_match else ""
        douyin_id = ""
        summary_match = re.search(r"】\s*(.+?)\s*https?://", text, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""

    if city == "河南":
        city = detect_city_from_text(text) or "河南"

    summary_part = make_summary_part(summary)
    result = "%s，%s，%s\u201c%s\u201d（ID：%s）发布，%s链接：%s" % (
        time_str, city, platform, author, douyin_id, summary_part, url)
    return result


# ===================== 统一入口 =====================

def convert_text(text, city_override=None):
    if not text or not text.strip():
        return None, "输入为空"
    fields = parse_fields(text)
    if not fields and (
        "kuaishou.com" in text or "douyin.com" in text
        or "xiaohongshu.com" in text or "xhslink.com" in text
    ):
        return convert_share_text(text, city_override), None
    if not fields:
        return None, "未识别到有效字段"
    time_str = format_time(fields.get("发布时间", ""))
    if city_override and city_override.strip():
        city = city_override.strip()
    else:
        city = detect_city_from_text(text) or "河南"
    platform = fields.get("来源网站", "抖音")
    author = fields.get("作者", "")
    douyin_id = fields.get("抖音号", "") or fields.get("账号ID", "")
    summary = fields.get("摘要", "")
    url = fields.get("原文链接", "")
    summary_part = make_summary_part(summary)
    result = "%s，%s，%s\u201c%s\u201d（ID：%s）发布，%s链接：%s" % (
        time_str, city, platform, author, douyin_id, summary_part, url)
    return result, None


# ===================== 结果字符串 <-> 字段 =====================

def parse_result_to_fields(result):
    """把报送结果字符串拆回各字段"""
    url = ""
    body = result
    if "链接：" in result:
        body, url = result.split("链接：", 1)
        url = url.strip()
    m = re.match(
        r"^(.+?)\uff0c(.+?)\uff0c(.+?)[\u201c\"](.*?)[\u201d\"]"
        r"(?:\uff08ID\uff1a(.*?)\uff09)?\u53d1\u5e03\uff0c(.*)",
        body
    )
    if m:
        return {
            "tag": "",
            "time": m.group(1).strip(),
            "city": m.group(2).strip(),
            "platform": m.group(3).strip(),
            "author": m.group(4).strip(),
            "douyin_id": (m.group(5) or "").strip(),
            "summary": m.group(6).strip(),
            "url": url,
        }
    return {"tag": "", "time": "", "city": "", "platform": "",
            "author": "", "douyin_id": "", "summary": "", "url": url}


def build_result_from_fields(f):
    tag = f.get("tag", "").strip()
    time_str = f.get("time", "").strip()
    city = f.get("city", "").strip()
    platform = f.get("platform", "").strip()
    author = f.get("author", "").strip()
    douyin_id = f.get("douyin_id", "").strip()
    summary = f.get("summary", "").strip()
    url = f.get("url", "").strip()
    summary_part = make_summary_part(summary)
    body = "%s，%s，%s\u201c%s\u201d（ID：%s）发布，%s链接：%s" % (
        time_str, city, platform, author, douyin_id, summary_part, url)
    if tag:
        body = "\u3010%s\u3011" % tag + body
    return body
