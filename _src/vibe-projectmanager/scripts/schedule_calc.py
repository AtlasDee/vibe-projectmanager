"""排期推算与回读检查（references/wbs-and-schedule.md）。只用 Python 标准库，Windows / macOS / Linux 通用。

用法：
    python schedule_calc.py plan     <排期> [--start YYYY-MM-DD] [--holidays <文件>] [--table <表名或ID>] [--write <输出.md>]
    python schedule_calc.py check    <排期> [--baseline <基线>] [--as-of YYYY-MM-DD] [--soon N] [--holidays <文件>] [--table ...]
    python schedule_calc.py snapshot <排期> -o <基线.csv> [--table ...]

<排期> 三种格式，字段名与团队的多维表格一致（别名见 COLS）：
    .md    本地排期表草稿：第一张含「任务计划」列的表；层级用 WBS 列（1 / 1.2 / 1.2.3）或「父记录」列
    .csv   多维表格导出：有 _record_id 列时，父记录、前置任务按 record_id 对应；没有时按任务名对应
    .json  多维表格只读导出（bitable.json）：含多张表时用 --table 指定表名或 table_id
--holidays  节假日文件：每行一个日期；行内写了 补班 的算工作日。不给时按周一至周五
--as-of     截至日期，默认今天

plan      对有工时、没填死日期的叶子任务，按前置任务、日历和责任人（同一人同一时间只做一件）从 --start 往后排；
          已填计划开始、计划结束的视为定值不动；父级日期按子级汇总；输出关键路径、浮动、里程碑和 Mermaid 甘特图。
          --write 另存一份填好日期的本地排期表（只写本地文件，不碰多维表格）。
check     回读检查：概况、里程碑（与基线比）、基线比对、逾期未完成、即将到期、父级汇总不一致、数据质量。
          基线取 --baseline 文件；没给时用表内的「基线开始 / 基线结束」列；都没有时只报当前计划。
snapshot  把当前排期存成基线快照（CSV：record_id、路径、日期、工时、责任人、里程碑），供以后 check --baseline。

输出 Markdown 到标准输出，只算不判断：逾期是否属实、要不要升级由人定。读不准、被跳过的内容列在最后一节。
退出码：0 = 已输出；2 = 用法错误或没读到任务行。
"""
import csv
import datetime
import io
import json
import math
import os
import re
import sys
from collections import defaultdict

BS = chr(92)
COLS = {
    "id": ("_record_id", "record_id", "ID"),
    "wbs": ("WBS", "WBS编码"),
    "name": ("任务计划", "任务", "工作包", "名称"),
    "parent": ("父记录", "父级"),
    "start": ("计划开始",),
    "end": ("计划结束",),
    "astart": ("实际开始",),
    "aend": ("实际结束",),
    "bstart": ("基线开始",),
    "bend": ("基线结束",),
    "effort": ("工时（人天）", "正常工时（人天）", "工时", "工期"),
    "progress": ("进度", "进度/Progress"),
    "done": ("完成状态",),
    "status": ("状态",),
    "node": ("节点",),
    "team": ("团队",),
    "owner": ("责任人",),
    "milestone": ("里程碑节点",),
    "pred": ("前置任务", "前置", "依赖"),
    "source": ("出处",),
    "note": ("备注",),
    "path": ("路径",),
}
DONE_STATUS = ("已完成", "已上线", "完成", "已发布", "已关闭")
NOT_STARTED = ("未开始",)
UNKNOWN = {"", "🔵", "待更新", "待定", "tbd", "—", "-", "?", "？"}
PHASE_NODES = {"开发": {"开发"}, "联调": {"联调"}, "测试": {"测试"}, "验收": {"验收"},
               "灰度": {"灰度", "演示"}, "发布": {"发版", "发布"}}
DATE_IN_NAME = re.compile(r"(?<![\dA-Za-z.])(\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}[日号]?|\d{1,2}\s?[日号](?!码)|(0[1-9]|1[0-2])[0-3]\d)(?![\d.])")
SHOW = 25  # 每个清单最多列几行


# ---------- 基础解析 ----------

def norm_header(h):
    return (h or "").replace("(", "（").replace(")", "）").replace(" ", "").replace("`", "").replace("**", "").strip()


def clean(v):
    return (v or "").replace("`", "").replace("**", "").strip()


def is_unknown(v):
    v = clean(v)
    return v.lower() in UNKNOWN or v.startswith("🔵")


def parse_date(v):
    v = clean(v)
    if is_unknown(v):
        return None
    m = re.match(r"^(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?", v)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def parse_num(v):
    v = clean(v).replace("%", "")
    if is_unknown(v):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_progress(v):
    raw = clean(v)
    n = parse_num(raw)
    if n is None:
        return None
    if raw.endswith("%") or n > 1:
        n = n / 100.0
    return n


def parse_bool(v):
    v = clean(v).lower()
    if v in ("true", "1", "是", "✔", "✅", "y", "yes", "已完成"):
        return True
    if v in ("false", "0", "否", "", "n", "no"):
        return False if v else None
    return None


def split_multi(v):
    v = clean(v)
    if is_unknown(v):
        return []
    return [x.strip() for x in re.split(r"[;；、,，]", v) if x.strip()]


def split_row(line):
    cells, cur, i = [], "", 0
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith(BS + "|"):
        s = s[:-1]
    while i < len(s):
        if s[i] == BS and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if s[i] == "|":
            cells.append(cur.strip())
            cur = ""
        else:
            cur += s[i]
        i += 1
    cells.append(cur.strip())
    return cells


def is_sep(line):
    return bool(re.match(r"^\|[-| :]+\|\s*$", (line or "").strip()))


# ---------- 日历 ----------

class Calendar:
    def __init__(self, holidays=(), makeup=()):
        self.holidays, self.makeup = set(holidays), set(makeup)

    def is_work(self, d):
        return d in self.makeup or (d.weekday() < 5 and d not in self.holidays)

    def next_work(self, d, include=True):
        d = d if include else d + datetime.timedelta(days=1)
        while not self.is_work(d):
            d += datetime.timedelta(days=1)
        return d

    def add(self, d, n):
        """从工作日 d 起，往后数 n 个工作日（n=0 为 d 本身）。"""
        d = self.next_work(d)
        while n > 0:
            d = self.next_work(d, include=False)
            n -= 1
        return d

    def between(self, a, b):
        """a→b 之间的工作日数（不含 a，含 b）；b 早于 a 时为负。"""
        if a == b:
            return 0
        sign, lo, hi = (1, a, b) if b > a else (-1, b, a)
        n, d = 0, lo
        while d < hi:
            d += datetime.timedelta(days=1)
            if self.is_work(d):
                n += 1
        return sign * n


def load_holidays(path, notes):
    hol, mk = set(), set()
    if not path:
        return Calendar()
    try:
        text = io.open(path, encoding="utf-8-sig").read()
    except OSError as e:
        notes.append("节假日文件读不到：%s（%s），按周一至周五计" % (path, e))
        return Calendar()
    for line in text.splitlines():
        m = re.search(r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})", line)
        if not m:
            continue
        d = parse_date(m.group(1))
        if d is None:
            notes.append("节假日文件里读不出的日期：%s" % line.strip())
        elif "补班" in line:
            mk.add(d)
        else:
            hol.add(d)
    return Calendar(hol, mk)


# ---------- 读入 ----------

def map_columns(headers):
    idx = {}
    nh = [norm_header(h) for h in headers]
    for key, names in COLS.items():
        for name in names:
            n = norm_header(name)
            if n in nh:
                idx[key] = headers[nh.index(n)]
                break
    return idx


def rows_from_records(headers, records, label):
    """records: [dict 列名→文本]；返回 (表名, 行列表, 列映射)。"""
    return label, records, map_columns(headers)


def load_md(path, notes):
    lines = io.open(path, encoding="utf-8-sig").read().splitlines()
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and is_sep(lines[i + 1]):
            headers = split_row(lines[i])
            if not any(norm_header(h) in [norm_header(n) for n in COLS["name"]] for h in headers):
                continue
            recs, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|") and not is_sep(lines[j]):
                cells = split_row(lines[j])
                if len(cells) != len(headers):
                    notes.append("第 %d 行列数 %d，与表头 %d 列不符，已按位置读取" % (j + 1, len(cells), len(headers)))
                recs.append({h: (cells[k] if k < len(cells) else "") for k, h in enumerate(headers)})
                j += 1
            title = next((l.lstrip("# ").strip() for l in lines[:i] if l.startswith("# ")), os.path.basename(path))
            title = re.sub(r"^排期表[：:]\s*", "", title)
            return rows_from_records(headers, recs, title)
    raise ValueError("没找到含「任务计划」列的表格")


def load_csv(path, notes):
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        headers = rd.fieldnames or []
        recs = [dict(r) for r in rd]
    return rows_from_records(headers, recs, os.path.splitext(os.path.basename(path))[0])


def json_cell(v, ftype, tz):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if ftype in (5, 1001, 1002):
        try:
            ms = float(v)
            if ms > 1e11:
                d = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ms, hours=tz)
                return d.strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            pass
        return str(v)
    if ftype in (18, 21):
        ids = []
        for x in v if isinstance(v, list) else [v]:
            if isinstance(x, dict):
                ids.extend(x.get("record_ids") or x.get("link_record_ids") or [])
        return ";".join(ids)
    if isinstance(v, dict):
        if "value" in v and ftype in (19, 20):
            inner = v["value"]
            return ";".join(json_cell(x, 0, tz) for x in (inner if isinstance(inner, list) else [inner]))
        for k in ("text", "name", "link"):
            if v.get(k):
                return str(v[k])
        return ""
    if isinstance(v, list):
        sep = "" if ftype == 1 else ";"
        return sep.join(json_cell(x, 0, tz) for x in v)
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def load_json(path, table, notes):
    d = json.load(io.open(path, encoding="utf-8-sig"))
    tables = d.get("tables") or []
    tz = float(d.get("tz_hours", 8))
    if table:
        pick = [t for t in tables if table in (t.get("name"), t.get("table_id"))]
    else:
        pick = tables if len(tables) == 1 else []
    if len(pick) != 1:
        names = "、".join("%s（%s）" % (t.get("name"), t.get("table_id")) for t in tables)
        raise ValueError("JSON 里有 %d 张表，用 --table 指定一张：%s" % (len(tables), names))
    t = pick[0]
    types = {f.get("field_name"): f.get("type") for f in t.get("fields", [])}
    headers = ["_record_id"] + list(types)
    recs = []
    for r in t.get("records", []):
        fl = r.get("fields", r)
        rid = r.get("record_id") or r.get("_id") or ""
        row = {"_record_id": rid}
        for n, ty in types.items():
            row[n] = json_cell(fl.get(n), ty or 0, tz)
        recs.append(row)
    return rows_from_records(headers, recs, t.get("name"))


def load(path, table, notes):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".md":
        return load_md(path, notes)
    if ext == ".csv":
        return load_csv(path, notes)
    if ext == ".json":
        return load_json(path, table, notes)
    raise ValueError("不认识的格式：%s（支持 .md / .csv / .json）" % path)


# ---------- 模型 ----------

class Task:
    __slots__ = ("id", "name", "raw_parent", "parent", "children", "order", "wbs", "start", "end", "astart",
                 "aend", "bstart", "bend", "effort", "progress", "done", "status", "node", "team", "owner",
                 "milestone", "preds", "source", "note", "path_hint", "dur", "es", "ef", "ls", "how")

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, None)
        self.children, self.preds = [], []


def build(label, recs, cmap, notes):
    g = lambda r, k: (r.get(cmap[k]) or "") if k in cmap else ""
    if "name" not in cmap:
        raise ValueError("没有「任务计划」列")
    tasks = []
    for i, r in enumerate(recs, 1):
        t = Task()
        t.order = i
        t.wbs = clean(g(r, "wbs"))
        t.id = clean(g(r, "id")) or t.wbs or "行%d" % i
        t.name = clean(g(r, "name"))
        t.raw_parent = clean(g(r, "parent"))
        t.path_hint = clean(g(r, "path"))
        for k in ("start", "end", "astart", "aend", "bstart", "bend"):
            raw = g(r, k)
            val = parse_date(raw)
            if val is None and not is_unknown(raw):
                notes.append("%s的%s读不出日期：%s" % (label_of(t), COLS[k][0], clean(raw)))
            setattr(t, k, val)
        raw = g(r, "effort")
        t.effort = parse_num(raw)
        if t.effort is None and not is_unknown(raw):
            notes.append("%s的工时不是数字：%s" % (label_of(t), clean(raw)))
        t.progress = parse_progress(g(r, "progress"))
        t.done = parse_bool(g(r, "done"))
        t.status = clean(g(r, "status"))
        t.node = split_multi(g(r, "node"))
        t.team = split_multi(g(r, "team"))
        t.owner = split_multi(g(r, "owner"))
        t.milestone = clean(g(r, "milestone"))
        t.preds = split_multi(g(r, "pred"))
        t.source = clean(g(r, "source"))
        t.note = clean(g(r, "note"))
        tasks.append(t)
    link_tree(tasks, "parent" in cmap or "wbs" not in cmap, notes)
    return tasks


def label_of(t):
    return "「%s」" % (t.name or t.id)


def resolver(tasks):
    by_id = {t.id: t for t in tasks}
    by_wbs = {t.wbs: t for t in tasks if t.wbs}
    by_name = defaultdict(list)
    for t in tasks:
        if t.name:
            by_name[t.name].append(t)

    def find(token):
        token = clean(token)
        if token in by_id:
            return by_id[token], None
        if token in by_wbs:
            return by_wbs[token], None
        hits = by_name.get(token, [])
        if len(hits) == 1:
            return hits[0], None
        return None, ("重名 %d 行" % len(hits) if hits else "找不到")
    return find


def link_tree(tasks, use_parent_col, notes):
    find = resolver(tasks)
    by_wbs = {t.wbs: t for t in tasks if t.wbs}
    for t in tasks:
        p = None
        if use_parent_col and t.raw_parent:
            ref = split_multi(t.raw_parent)[0] if split_multi(t.raw_parent) else ""
            if ref:
                p, why = find(ref)
                if p is None:
                    notes.append("%s的父记录 %s %s，按顶层处理" % (label_of(t), ref, why))
        elif t.wbs and "." in t.wbs:
            p = by_wbs.get(t.wbs.rsplit(".", 1)[0])
            if p is None:
                notes.append("%s的 WBS %s 找不到上一级，按顶层处理" % (label_of(t), t.wbs))
        if p is t:
            p = None
        t.parent = p
    # 父链成环的断开
    for t in tasks:
        seen, cur = set(), t
        while cur.parent is not None:
            if cur.id in seen:
                notes.append("父记录成环（含 %s），已断开" % label_of(cur))
                cur.parent = None
                break
            seen.add(cur.id)
            cur = cur.parent
    for t in tasks:
        if t.parent is not None:
            t.parent.children.append(t)


def path_of(t):
    parts, cur = [], t
    while cur is not None:
        parts.append(cur.name or "（无名称）")
        cur = cur.parent
    return " / ".join(reversed(parts))


def top_of(t):
    cur = t
    while cur.parent is not None:
        cur = cur.parent
    return cur


def leaves(tasks):
    return [t for t in tasks if not t.children]


def is_done(t):
    return bool(t.done) or (t.progress is not None and t.progress >= 1) or t.status in DONE_STATUS


def descend_leaves(t):
    if not t.children:
        return [t]
    out = []
    for c in t.children:
        out.extend(descend_leaves(c))
    return out


def rollup_dates(t, attr_s="start", attr_e="end"):
    """返回子孙叶子的 (最早开始, 最晚结束)。"""
    ds = [getattr(x, attr_s) for x in descend_leaves(t) if getattr(x, attr_s)]
    de = [getattr(x, attr_e) for x in descend_leaves(t) if getattr(x, attr_e)]
    return (min(ds) if ds else None, max(de) if de else None)


# ---------- 输出工具 ----------

def fmt(d):
    return d.strftime("%Y-%m-%d") if d else "—"


def esc(s):
    return (s or "").replace("|", BS + "|").replace("\n", " ")


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(esc(str(c)) for c in r) + " |" for r in rows]
    return out


def capped(rows):
    if len(rows) <= SHOW:
        return rows, ""
    return rows[:SHOW], "…另 %d 行未列出" % (len(rows) - SHOW)


def pct(x):
    return "—" if x is None else "%d%%" % round(x * 100)


# ---------- plan ----------

def plan(label, tasks, cal, start, notes):
    find = resolver(tasks)
    lv = leaves(tasks)
    out = ["# 排期推算：%s" % label, ""]
    out.append("- 起点：%s · 日历：%s" % (fmt(start), "周一至周五，另有节假日 %d 天、补班 %d 天" % (
        len(cal.holidays), len(cal.makeup)) if (cal.holidays or cal.makeup) else "周一至周五（没给节假日文件）"))
    out.append("- 工期换算 🔶：工期（工作日）= 工时（人天）÷ 责任人数，向上取整；工时为 0 的是里程碑")
    out.append("- 已填计划开始和计划结束的任务视为定值，不重排；父级日期按子级汇总")
    out.append("")
    issues = defaultdict(list)
    # 前置：解析到叶子集合
    pred_leaves = {}
    for t in lv:
        ps = []
        for tok in t.preds:
            p, why = find(tok)
            if p is None:
                issues["前置任务引用不到"].append([path_of(t), tok, why])
                continue
            ps.extend(x for x in descend_leaves(p) if x is not t)
        pred_leaves[t.id] = ps
    # 工期
    for t in lv:
        n = max(1, len(t.owner))
        if t.start and t.end:
            if t.effort == 0:  # 工时 0 是里程碑：填了日期也按 0 天
                t.dur = 0
            else:
                t.dur = max(0, cal.between(cal.next_work(t.start), t.end) + 1) if t.end >= t.start else None
            t.how = "原值"
        elif t.effort is not None:
            t.dur = 0 if t.effort == 0 else int(math.ceil(t.effort / n))
            t.how = "推算"
        else:
            t.dur = None
            t.how = None
    # 拓扑序
    order, state, cyc = [], {}, set()

    def visit(t, stack):
        if state.get(t.id) == 2:
            return True
        if state.get(t.id) == 1:
            loop = stack[[x.id for x in stack].index(t.id):] if t.id in [x.id for x in stack] else stack
            issues["循环依赖（环上的任务不排）"].append([" → ".join(x.name or x.id for x in loop + [t]), "", ""])
            cyc.update(x.id for x in loop)
            return False
        state[t.id] = 1
        ok = all(visit(p, stack + [t]) for p in pred_leaves[t.id])
        state[t.id] = 2
        order.append(t)
        return ok

    for t in sorted(lv, key=lambda x: x.order):
        visit(t, [])
    busy = defaultdict(list)  # 责任人 → [(开始, 结束, 任务)]
    res_pred = defaultdict(list)  # 任务 → 因同一责任人排队而必须等的任务
    for t in order:
        if t.how == "原值":
            t.es, t.ef = t.start, t.end
            for o in t.owner:
                for (s, e, x) in busy[o]:
                    if not (t.ef < s or t.es > e):
                        issues["同一责任人时间重叠（定值任务，未调整）"].append([path_of(t), o, "与「%s」%s～%s 重叠" % (x.name, fmt(s), fmt(e))])
                busy[o].append((t.es, t.ef, t))
            continue
        if t.id in cyc:
            t.how = "排不了（循环依赖）"
            continue
        if t.dur is None:
            continue
        preds = [p for p in pred_leaves[t.id] if p.ef]
        missing = [p for p in pred_leaves[t.id] if not p.ef]
        if missing:
            issues["前置任务没有日期，按已知前置排"].append([path_of(t), "、".join(p.name for p in missing), ""])
        last = max((p.ef for p in preds), default=None)
        if t.dur == 0:
            t.es = t.ef = last or cal.next_work(t.start or start)
            continue
        es = cal.next_work(last, include=False) if last else cal.next_work(start)
        if t.start and t.start > es:
            es = cal.next_work(t.start)
        mover = None
        while True:
            ef = cal.add(es, t.dur - 1)
            clash = [(e, x) for o in t.owner for (s, e, x) in busy[o] if not (ef < s or es > e)]
            if not clash:
                break
            e, mover = max(clash, key=lambda c: c[0])
            es = cal.next_work(e, include=False)
        if mover is not None:  # 因同一责任人排队而推后：记为资源前置，参与浮动计算
            res_pred[t.id].append(mover)
        t.es, t.ef = es, ef
        for o in t.owner:
            busy[o].append((es, ef, t))
    # 同一责任人前后紧挨着的任务（含定值任务）视为排队
    for o, spans in busy.items():
        spans = sorted(spans, key=lambda x: (x[0], x[2].order))
        for (s1, e1, a), (s2, e2, b) in zip(spans, spans[1:]):
            if a.dur and b.dur and s2 == cal.next_work(e1, include=False) and a not in res_pred[b.id] \
                    and a not in pred_leaves[b.id]:
                res_pred[b.id].append(a)
    # 浮动：按前置任务和同一责任人排队一起算
    sched = [t for t in lv if t.ef]
    if sched:
        proj_end = max(t.ef for t in sched)
        succ = defaultdict(list)
        for t in sched:
            for p in pred_leaves[t.id] + res_pred[t.id]:
                if p.ef:
                    succ[p.id].append(t)
        # 后继先算：对前置 + 资源前置合成的图做拓扑排序，再倒序处理
        indeg = {t.id: 0 for t in sched}
        for t in sched:
            for s in succ[t.id]:
                indeg[s.id] += 1
        queue = sorted([t for t in sched if indeg[t.id] == 0], key=lambda x: x.order)
        topo = []
        while queue:
            t = queue.pop(0)
            topo.append(t)
            for s in succ[t.id]:
                indeg[s.id] -= 1
                if indeg[s.id] == 0:
                    queue.append(s)
        for t in reversed(topo):
            if succ[t.id]:
                lf = min((s.ls if s.dur == 0 else prev_work(cal, s.ls)) for s in succ[t.id] if s.ls)
            else:
                lf = proj_end
            t.ls = back(cal, lf, cal.between(t.es, t.ef))
    # 父级汇总
    for t in tasks:
        if t.children:
            t.es, t.ef = rollup_dates_attr(t)
    rows = []
    for t in sorted(tasks, key=lambda x: x.order):
        fl = ""
        if not t.children and t.ef and t.ls:
            f = cal.between(t.es, t.ls)
            fl = "●" if f == 0 else ("%d（冲突）" % f if f < 0 else str(f))
        how = "汇总" if t.children else (t.how or "排不了")
        rows.append([t.wbs or "", path_of(t), "、".join(t.owner), "" if t.dur is None else t.dur,
                     "、".join(t.preds), fmt(t.es), fmt(t.ef), fl, how])
    out.append("## 排期结果")
    out.append("")
    out += md_table(["WBS", "路径", "责任人", "工期", "前置任务", "计划开始", "计划结束", "浮动", "来源"], rows)
    out.append("")
    out.append("浮动单位为工作日，● 为关键路径；浮动按前置任务和同一责任人排队一起算。"
               "负数表示现有日期已经排不开（如定值任务晚于后继的定值），要改日期或依赖。")
    queued = [[path_of(t), "、".join(x.name for x in res_pred[t.id])] for t in sorted(lv, key=lambda x: x.order) if res_pred[t.id]]
    if queued:
        out.append("")
        out.append("同一责任人排队（因排队推后，或前后紧挨着）：")
        out.append("")
        out += md_table(["任务", "排在其后"], queued)
    out.append("")
    crit = sorted([t for t in order if t.ef and t.ls and cal.between(t.es, t.ls) == 0], key=lambda x: (x.es, x.order))
    out.append("## 关键路径")
    out.append("")
    if crit:
        s0 = min(t.es for t in sched)
        out.append(" → ".join(t.name for t in crit))
        out.append("")
        out.append("总工期：%s ～ %s，共 %d 个工作日" % (fmt(s0), fmt(proj_end), cal.between(s0, proj_end) + 1))
    else:
        out.append("没有可推算的任务。")
    out.append("")
    ms = [t for t in tasks if t.milestone]
    if ms:
        out.append("## 里程碑")
        out.append("")
        out += md_table(["里程碑节点", "路径", "日期"], [[t.milestone, path_of(t), fmt(t.ef)] for t in ms])
        out.append("")
    unscheduled = [[path_of(t), "没有工时，也没有计划日期", ""] for t in lv if t.ef is None and t.dur is None]
    if unscheduled:
        issues["排不了的叶子任务"] = unscheduled
    out += gantt(label, tasks)
    out += issue_block(issues, ["行", "项", "说明"])
    return out


def prev_work(cal, d):
    d -= datetime.timedelta(days=1)
    while not cal.is_work(d):
        d -= datetime.timedelta(days=1)
    return d


def back(cal, d, n):
    while n > 0:
        d = prev_work(cal, d)
        n -= 1
    return d


def rollup_dates_attr(t):
    ds = [x.es for x in descend_leaves(t) if x.es]
    de = [x.ef for x in descend_leaves(t) if x.ef]
    return (min(ds) if ds else None, max(de) if de else None)


def gantt(label, tasks):
    lv = [t for t in sorted(tasks, key=lambda x: x.order) if not t.children and t.es and t.ef]
    if not lv:
        return []
    out = ["## 甘特图", "", "```mermaid", "gantt", "    title %s" % mm(label), "    dateFormat YYYY-MM-DD",
           "    axisFormat %m-%d"]
    sec = None
    for i, t in enumerate(lv, 1):
        top = top_of(t).name or "（无名称）"
        if top != sec:
            out.append("    section %s" % mm(top))
            sec = top
        name = mm(t.name if t.parent is None or t.parent.parent is None else "%s·%s" % (t.parent.name, t.name))
        if t.dur == 0 or t.milestone and t.es == t.ef and t.dur in (0, None):
            out.append("    %s :milestone, t%d, %s, 0d" % (name, i, fmt(t.ef)))
        else:
            out.append("    %s :t%d, %s, %s" % (name, i, fmt(t.es), fmt(t.ef + datetime.timedelta(days=1))))
    out += ["```", ""]
    return out


def mm(s):
    s = re.sub(r"[:#;]", " ", s or "").strip()
    return (s[:40] + "…") if len(s) > 40 else (s or "（无名称）")


def write_md(path, label, tasks):
    out = ["# 排期表：%s" % label, "",
           "> 由 schedule_calc.py plan 生成的草稿；日期是推算值，确认后再定基线。", ""]
    rows = []
    for t in sorted(tasks, key=lambda x: x.order):
        rows.append([t.wbs or "", t.name, "；".join(t.node), "；".join(t.team), "；".join(t.owner),
                     "" if t.effort is None else ("%g" % t.effort), "；".join(t.preds), fmt(t.es) if t.es else "",
                     fmt(t.ef) if t.ef else "", t.milestone or "", t.source or "",
                     "" if t.parent is None else (t.parent.wbs or t.parent.name), t.note or ""])
    out += md_table(["WBS", "任务计划", "节点", "团队", "责任人", "工时（人天）", "前置任务", "计划开始", "计划结束",
                     "里程碑节点", "出处", "父记录", "备注"], rows)
    out.append("")
    out += gantt(label, tasks)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ---------- check ----------

def load_baseline(path, table, notes):
    bl_notes = []
    label, recs, cmap = load(path, table, bl_notes)
    bt = build(label, recs, cmap, bl_notes)
    if "path" in cmap:  # 快照按路径比对，父记录对不上不影响
        bl_notes = [n for n in bl_notes if "父记录" not in n]
    if bl_notes:
        notes.append("基线文件有 %d 处读不准（首条：%s）" % (len(bl_notes), bl_notes[0]))
    return bt


def check(label, tasks, cal, as_of, soon, baseline, notes):
    lv = leaves(tasks)
    out = ["# 排期检查：%s · 截至 %s" % (label, fmt(as_of)), ""]
    # 概况
    dated = [t for t in lv if t.start or t.end]
    ds = [x for t in tasks for x in (t.start, t.end) if x]
    done = [t for t in lv if is_done(t)]
    out.append("## 概况")
    out.append("")
    out.append("- 行数 %d，叶子任务 %d；计划跨度 %s ～ %s" % (len(tasks), len(lv), fmt(min(ds) if ds else None),
                                                       fmt(max(ds) if ds else None)))
    out.append("- 叶子：已完成 %d · 有计划日期 %d · 有责任人 %d · 填了工时 %d · 填了实际日期 %d" % (
        len(done), len(dated), sum(1 for t in lv if t.owner), sum(1 for t in lv if t.effort is not None),
        sum(1 for t in lv if t.astart or t.aend)))
    out.append("- 已完成的判定：勾了完成状态，或进度 100%%，或状态为 %s 之一" % "、".join(DONE_STATUS))
    out.append("")
    # 基线
    base = {}
    if baseline is not None:
        by_id = {t.id: t for t in baseline}
        by_path = defaultdict(list)
        for t in baseline:
            by_path[t.path_hint or path_of(t)].append(t)
        used = set()
        for t in tasks:
            b = by_id.get(t.id)
            if b is None:
                hits = by_path.get(path_of(t), [])
                b = hits[0] if len(hits) == 1 else None
            if b is not None and b.id not in used:
                base[t.id] = (b.start, b.end)
                used.add(b.id)
        removed = [b for b in baseline if b.id not in used]
        src = "基线文件"
    else:
        for t in tasks:
            if t.bstart or t.bend:
                base[t.id] = (t.bstart, t.bend)
        removed = []
        src = "表内基线列" if base else None
    # 里程碑
    ms = [t for t in tasks if t.milestone]
    out.append("## 里程碑")
    out.append("")
    if ms:
        rows = []
        for t in ms:
            end = t.end or rollup_dates(t)[1]
            b = base.get(t.id, (None, None))[1]
            dev = "" if not (b and end) else "%+d" % cal.between(b, end)
            st = "已完成" if is_done(t) else ("已过期未完成" if end and end < as_of else "未到")
            rows.append([t.milestone, path_of(t), fmt(b), fmt(end), dev, st])
        out += md_table(["里程碑节点", "路径", "基线", "当前计划", "偏差（工作日）", "状态"], rows)
    else:
        out.append("表里没有标里程碑节点。各顶层阶段按子级汇总的完成日供参考：")
        out.append("")
        rows = []
        for t in [x for x in tasks if x.parent is None]:
            s, e = rollup_dates(t) if t.children else (t.start, t.end)
            rows.append([t.name, fmt(s), fmt(e), "已完成" if all(is_done(x) for x in descend_leaves(t)) else ""])
        out += md_table(["阶段", "最早开始", "最晚结束", "叶子全部完成"], rows)
    out.append("")
    # 基线比对
    out.append("## 基线比对")
    out.append("")
    if src is None:
        out.append("没有基线（没给 --baseline，表里也没有基线列），本节跳过。定基线：`schedule_calc.py snapshot`。")
    else:
        late, early, nochange, added = [], [], 0, []
        for t in tasks:
            if t.id not in base:
                added.append(t)
                continue
            bs, be = base[t.id]
            if be and t.end and t.end != be:
                d = cal.between(be, t.end)
                (late if t.end > be else early).append([path_of(t), fmt(be), fmt(t.end), "%+d" % d])
            else:
                nochange += 1
        if baseline is not None:
            out.append("来源：基线文件。计划结束推迟 %d 行、提前 %d 行、未变 %d 行；新增 %d 行；基线里有、现在没有的 %d 行。" % (
                len(late), len(early), nochange, len(added), len(removed)))
        else:
            out.append("来源：表内基线列。计划结束推迟 %d 行、提前 %d 行、未变 %d 行；没填基线的 %d 行。" % (
                len(late), len(early), nochange, len(added)))
        out.append("")
        if late:
            late.sort(key=lambda r: -int(r[3]))
            rows, more = capped(late)
            out.append("**计划结束推迟**（改了计划日期后，表里的距离截止日不会再显示延期，以这里为准）：")
            out.append("")
            out += md_table(["路径", "基线结束", "当前计划结束", "偏差（工作日）"], rows)
            if more:
                out.append(more)
            out.append("")
        if baseline is not None and added:
            rows, more = capped([[path_of(t), fmt(t.start), fmt(t.end)] for t in added])
            out.append("**新增行**：")
            out.append("")
            out += md_table(["路径", "计划开始", "计划结束"], rows)
            if more:
                out.append(more)
            out.append("")
        if removed:
            rows, more = capped([[b.path_hint or path_of(b), fmt(b.end)] for b in removed])
            out.append("**基线里有、现在没有**：")
            out.append("")
            out += md_table(["路径", "基线结束"], rows)
            if more:
                out.append(more)
            out.append("")
    if out[-1] != "":
        out.append("")
    # 逾期
    overdue = sorted([t for t in lv if t.end and t.end < as_of and not is_done(t)],
                     key=lambda t: (t.end, t.order))
    out.append("## 逾期未完成（计划结束早于 %s，且未完成）" % fmt(as_of))
    out.append("")
    if overdue:
        released = [t for t in tasks if t.parent is None and ("发布" in (t.name or "") or "发版" in (t.name or ""))]
        rel_end = max([rollup_dates(t)[1] or t.end for t in released if (rollup_dates(t)[1] or t.end)], default=None)
        if rel_end and rel_end < as_of:
            out.append("⚠ 本排期的发布阶段计划在 %s，已经过去。下面多半是发布后没回填的行：先请负责人核实，确认真没做完的才算延期。" % fmt(rel_end))
            out.append("")
        rows, more = capped([[path_of(t), "、".join(t.owner) or "🔵", fmt(t.end), cal.between(t.end, as_of),
                              pct(t.progress), t.status or ""] for t in overdue])
        out += md_table(["路径", "责任人", "计划结束", "逾期（工作日）", "进度", "状态"], rows)
        if more:
            out.append(more)
        by_top = defaultdict(int)
        for t in overdue:
            by_top[top_of(t).name or "（无名称）"] += 1
        out.append("")
        out.append("按顶层阶段：" + "，".join("%s %d" % kv for kv in by_top.items()))
    else:
        out.append("无。")
    out.append("")
    # 即将到期
    horizon = cal.add(as_of, soon)
    due = sorted([t for t in lv if t.end and as_of <= t.end <= horizon and not is_done(t)], key=lambda t: t.end)
    out.append("## 即将到期（%d 个工作日内，截至 %s）" % (soon, fmt(horizon)))
    out.append("")
    if due:
        rows, more = capped([[path_of(t), "、".join(t.owner) or "🔵", fmt(t.end), pct(t.progress)] for t in due])
        out += md_table(["路径", "责任人", "计划结束", "进度"], rows)
        if more:
            out.append(more)
    else:
        out.append("无。")
    out.append("")
    # 父级
    span_bad, prog_bad = [], []
    for t in tasks:
        if not t.children:
            continue
        cs, ce = rollup_dates(t)
        if t.start and t.end and cs and ce and (cs < t.start or ce > t.end):
            span_bad.append([path_of(t), "%s ～ %s" % (fmt(t.start), fmt(t.end)), "%s ～ %s" % (fmt(cs), fmt(ce))])
        kids = descend_leaves(t)
        all_done = all(is_done(x) for x in kids)
        if is_done(t) and not all_done:
            prog_bad.append([path_of(t), "父级已完成", "有 %d 个子任务未完成" % sum(1 for x in kids if not is_done(x))])
        elif all_done and kids and not is_done(t) and (t.done is not None or t.progress is not None):
            prog_bad.append([path_of(t), "父级未完成", "子任务全部完成"])
    out.append("## 父级汇总不一致")
    out.append("")
    if span_bad or prog_bad:
        if span_bad:
            rows, more = capped(span_bad)
            out.append("**父级日期没覆盖子级**（父级日期是手填的，不随子级汇总）：")
            out.append("")
            out += md_table(["路径", "父级日期", "子级实际跨度"], rows)
            if more:
                out.append(more)
            out.append("")
        if prog_bad:
            rows, more = capped(prog_bad)
            out.append("**完成情况与子级不符**：")
            out.append("")
            out += md_table(["路径", "父级", "子级"], rows)
            if more:
                out.append(more)
            out.append("")
    else:
        out.append("无。")
        out.append("")
    # 数据质量
    issues = defaultdict(list)
    find = resolver(tasks)
    for t in tasks:
        p = path_of(t)
        if not t.name:
            issues["空名称行"].append([p, t.id, ""])
        if t.done and t.progress is not None and t.progress < 1:
            issues["勾了完成但进度不到 100%"].append([p, pct(t.progress), ""])
        if t.status in DONE_STATUS and t.progress is not None and t.progress < 1:
            issues["状态与进度不符"].append([p, t.status, pct(t.progress)])
        if t.status in NOT_STARTED and ((t.progress or 0) > 0 or t.done):
            issues["状态与进度不符"].append([p, t.status, "进度 %s%s" % (pct(t.progress), "，已勾完成" if t.done else "")])
        if bool(t.start) != bool(t.end):
            issues["只有一端计划日期"].append([p, fmt(t.start), fmt(t.end)])
        if t.start and t.end and t.end < t.start:
            issues["计划结束早于计划开始"].append([p, fmt(t.start), fmt(t.end)])
        if t.astart and t.aend and t.aend < t.astart:
            issues["实际结束早于实际开始"].append([p, fmt(t.astart), fmt(t.aend)])
        if not t.children and t.name and not (t.start or t.end):
            issues["叶子任务没有计划日期"].append([p, "", ""])
        m = DATE_IN_NAME.search(t.name or "")
        if m:
            issues["名称里写了日期（日期应放进日期列）"].append([p, m.group(0), ""])
        if t.node:
            hits = [k for k in PHASE_NODES if k in (t.name or "") or (k == "发布" and "发版" in (t.name or ""))]
            if len(hits) == 1 and not (set(t.node) & PHASE_NODES[hits[0]]):
                issues["节点与名称不符（提示）"].append([p, "名称含 %s" % hits[0], "节点为 %s" % "、".join(t.node)])
        for tok in t.preds:
            x, why = find(tok)
            if x is None:
                issues["前置任务引用不到"].append([p, tok, why])
    out += issue_block(issues, ["行", "项", "说明"], title="## 数据质量")
    return out


def issue_block(issues, header, title="## 需要处理"):
    out = [title, ""]
    if not issues:
        return out + ["无。", ""]
    for k, rows in issues.items():
        out.append("**%s**（%d）：" % (k, len(rows)))
        out.append("")
        shown, more = capped(rows)
        out += md_table(header, shown)
        if more:
            out.append(more)
        out.append("")
    return out


# ---------- snapshot ----------

def snapshot(tasks, path):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["_record_id", "路径", "任务计划", "父记录", "计划开始", "计划结束", "工时（人天）", "责任人", "里程碑节点", "节点"])
        for t in sorted(tasks, key=lambda x: x.order):
            w.writerow([t.id, path_of(t), t.name, t.parent.id if t.parent else "", fmt(t.start) if t.start else "",
                        fmt(t.end) if t.end else "", "" if t.effort is None else "%g" % t.effort, ";".join(t.owner),
                        t.milestone or "", ";".join(t.node)])


# ---------- 入口 ----------

def arg(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def main(argv):
    if len(argv) < 2 or argv[0] not in ("plan", "check", "snapshot"):
        sys.stderr.write(__doc__)
        return 2
    cmd, path = argv[0], argv[1]
    notes = []
    try:
        label, recs, cmap = load(path, arg(argv, "--table"), notes)
        tasks = build(label, recs, cmap, notes)
    except (OSError, ValueError) as e:
        sys.stderr.write("读不了 %s：%s\n" % (path, e))
        return 2
    if not tasks:
        sys.stderr.write("%s 里没有任务行\n" % path)
        return 2
    cal = load_holidays(arg(argv, "--holidays"), notes)
    as_of_raw = arg(argv, "--as-of")
    as_of = parse_date(as_of_raw) if as_of_raw else datetime.date.today()
    if as_of is None:
        sys.stderr.write("--as-of 读不出日期：%s\n" % as_of_raw)
        return 2
    if cmd == "snapshot":
        o = arg(argv, "-o")
        if not o:
            sys.stderr.write("snapshot 需要 -o <基线.csv>\n")
            return 2
        snapshot(tasks, o)
        print("基线快照 → %s（%d 行）" % (o, len(tasks)))
        for n in notes:
            print("- " + n)
        return 0
    if cmd == "plan":
        start_raw = arg(argv, "--start")
        start = parse_date(start_raw) if start_raw else as_of
        if start is None:
            sys.stderr.write("--start 读不出日期：%s\n" % start_raw)
            return 2
        out = plan(label, tasks, cal, start, notes)
        w = arg(argv, "--write")
        if w:
            write_md(w, label, tasks)
            out.append("已另存排期表草稿：%s" % w)
            out.append("")
    else:
        soon_raw = arg(argv, "--soon", "3")
        try:
            soon = int(soon_raw)
        except ValueError:
            sys.stderr.write("--soon 需要整数：%s\n" % soon_raw)
            return 2
        bl = None
        bpath = arg(argv, "--baseline")
        if bpath:
            try:
                bl = load_baseline(bpath, arg(argv, "--table"), notes)
            except (OSError, ValueError) as e:
                sys.stderr.write("读不了基线 %s：%s\n" % (bpath, e))
                return 2
        out = check(label, tasks, cal, as_of, soon, bl, notes)
    out.append("## 读不准与跳过")
    out.append("")
    out += ["- " + n for n in notes] if notes else ["无。"]
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
