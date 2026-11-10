"""组合汇总（references/portfolio.md 第 8 节）。只读不写，只用 Python 标准库，Windows / macOS / Linux 通用。

用法：
    python portfolio_rollup.py <成员>... [--resources <资源分配表.md>] [--as-of YYYY-MM-DD]

<成员> 三种写法，可混用（但一个组合只该用一种成员类型，混用时会提示）：
    pm 目录             其下每个含 RAID日志.md 的需求目录算一个成员（需求型）；
                        名为 组合、或含 组合约定.md 的子目录是组合层；决策日志、变更请求等目录跳过
    需求目录            含 RAID日志.md 的目录，算一个成员
    名称=目录[,目录...] 一个项目型成员，名下几个需求目录；先于 pm 目录认领，同一目录不会再算进别的成员
    几个项目的 pm 目录一起传时，需求型成员的名称写成 <项目>/<需求>
--resources  组合的资源分配表（portfolio.md 第 2 节）
--as-of      截至日期，默认今天：复核当天到期也算到期；资源窗口按它分已过去、当前、将来

输出一份 Markdown 汇总到标准输出，供写组合台账和组合汇报前核对。只汇总，不判断。
读不准、被跳过的内容一律列在最后一节，不静默丢掉。
退出码：0 = 已输出；2 = 用法错误或一个成员都没找到。
"""
import datetime
import os
import re
import sys
from collections import defaultdict

RAID_FILE = "RAID日志.md"
COMBO = "组合"
COMBO_MARK = "组合约定.md"
NON_MEMBER_DIRS = {"决策日志", "变更请求", COMBO}
REQ_MARKERS = ("门禁记录.md", "任务台账.md")
SECTIONS = ("风险", "假设", "问题", "依赖")
LEVELS = ("严重", "高", "中", "低")
CLOSED = ("关闭", "已发生", "已验证", "不成立", "已解决", "已交付", "作废")  # 已缓解 不算关闭，照常复核
DEP_BAD = ("未确认", "延误", "受阻", "有风险")
UNKNOWN = {"", "🔵", "待更新", "待定", "tbd", "—", "-", "?", "？", "无"}
BS = chr(92)


# ---------- 单元格与表格 ----------

def clean(cell):
    """去掉 code 反引号、加粗星号和首尾空白（团队约定用 code 写值）。"""
    return (cell or "").replace("`", "").replace("**", "").strip()


def is_unknown(s):
    s = clean(s)
    return s.lower() in UNKNOWN or s.startswith("🔵")


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
    return bool(re.match(r"^\|[-| :]+\|\s*$", line or ""))


def parse_tables(text):
    """返回 [(所在 ## 小节名, [行字典])]。表头下一行必须是分隔行；两张表紧挨着时，遇到新的分隔行就另起一张。"""
    out, section, lines, i = [], None, text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            section = m.group(1)
        elif line.startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
            header = [clean(h) for h in split_row(line)]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].startswith("|") and not is_sep(lines[j]):
                if j + 1 < len(lines) and is_sep(lines[j + 1]):
                    break  # 这一行是下一张表的表头
                cells = split_row(lines[j])
                row = {h: (cells[k] if k < len(cells) else "") for k, h in enumerate(header)}
                if any(clean(v) for v in row.values()):
                    rows.append(row)
                j += 1
            out.append((section, rows))
            i = j
            continue
        i += 1
    return out


def col(row, *prefixes):
    """按列名前缀取值，兼容 方向（进 / 出）、方向（进/出）、方向 这类写法。"""
    for k, v in row.items():
        if any(clean(k).startswith(p) for p in prefixes):
            return v
    return ""


# ---------- 取值 ----------

def is_closed(status):
    s = clean(status)
    return not s.startswith("未") and any(k in s for k in CLOSED)


def level_of(cell):
    s = clean(cell)
    for lv in LEVELS:
        if lv in s:
            return lv
    return None


def parse_date(cell):
    s = clean(cell)
    m = re.search(r"(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})", s)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def date_or_note(cell):
    """返回 (日期或 None, 是否写了却读不出)。"""
    d = parse_date(cell)
    return d, (d is None and not is_unknown(cell))


def workdays(start, end):
    """end - start 的工作日数（周一至周五），end 早于 start 时为负。"""
    sign, a, b = (1, start, end) if end >= start else (-1, end, start)
    n, d = 0, a
    while d < b:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return sign * n


def parse_slack(cell):
    s = clean(cell).replace("−", "-").replace("🔶", "").strip()
    if "=" in s:
        s = s.rsplit("=", 1)[1].strip()
    m = re.fullmatch(r"(-?\d+)\s*(个?工作日|天)?", s)
    return int(m.group(1)) if m else None


def parse_pct(cell):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*%", clean(cell).replace("％", "%"))
    return float(m.group(1)) if m else None


def direction(cell):
    """返回 进 / 出 / None（读不出）。"""
    s = clean(cell).lower()
    out_ = any(k in s for k in ("出", "提供", "out", "等我们", "对方等"))
    in_ = any(k in s for k in ("进", "入", "in", "我们等", "等对方"))
    if out_ and not in_:
        return "出"
    if in_ and not out_:
        return "进"
    return None


# ---------- 成员 ----------

def norm(p):
    return os.path.normcase(os.path.realpath(p))


def has_raid(d):
    return os.path.isfile(os.path.join(d, RAID_FILE))


def is_combo(d):
    return os.path.basename(os.path.normpath(d)) == COMBO or os.path.isfile(os.path.join(d, COMBO_MARK))


def collect(args, notes):
    """返回 (成员 [{name, dirs, named}], 组合层目录, 没有 RAID 日志的需求目录)。"""
    claimed, members, combos, no_raid = {}, [], [], []
    named_args = [a for a in args if "=" in a and not os.path.isdir(a)]
    dir_args = [a for a in args if a not in named_args]

    for a in named_args:  # 项目型成员先认领
        name, rest = (x.strip() for x in a.split("=", 1))
        dirs = []
        for d in [x for x in rest.split(",") if x.strip()]:
            if not has_raid(d):
                notes.append(f"成员 {name} 的目录没有 {RAID_FILE}：{show(d)}")
            elif norm(d) in claimed:
                notes.append(f"{show(d)} 已归入成员 {claimed[norm(d)]}，不再归入 {name}")
            else:
                claimed[norm(d)] = name
                dirs.append(d)
        if dirs:
            members.append({"name": name, "dirs": dirs, "named": True, "proj": None})

    def add_auto(d, proj):
        if norm(d) in claimed:
            if claimed[norm(d)] != "组合层":
                notes.append(f"{show(d)} 已归入成员 {claimed[norm(d)]}，跳过")
            return
        claimed[norm(d)] = os.path.basename(os.path.normpath(d))
        members.append({"name": os.path.basename(os.path.normpath(d)), "dirs": [d], "named": False, "proj": proj})

    def add_combo(d):
        if norm(d) not in claimed:
            claimed[norm(d)] = "组合层"
            combos.append(d)

    for a in dir_args:
        if not os.path.isdir(a):
            notes.append(f"不是目录，已跳过：{show(a)}")
            continue
        if has_raid(a):
            add_combo(a) if is_combo(a) else add_auto(a, os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(a)))))
            continue
        proj = os.path.basename(os.path.dirname(os.path.abspath(a)))
        found = False
        for sub in sorted(os.listdir(a)):
            d = os.path.join(a, sub)
            if not os.path.isdir(d) or sub.startswith(("_", ".")):
                continue
            if is_combo(d):
                if has_raid(d):
                    add_combo(d)
                continue
            if sub in NON_MEMBER_DIRS:
                continue
            if has_raid(d):
                add_auto(d, proj)
                found = True
            elif any(os.path.isfile(os.path.join(d, m)) for m in REQ_MARKERS):
                no_raid.append(d)
        if not found and not combos:
            notes.append(f"{show(a)} 下没找到含 {RAID_FILE} 的需求目录")

    autos = [m for m in members if not m["named"]]
    if autos and len(autos) < len(members):
        notes.append("成员类型混用：既有项目型成员（名称=目录），又有需求型成员；一个组合只该用一种（portfolio.md 第 0 节）")
    if len({m["proj"] for m in autos}) > 1:  # 几个项目的 pm 目录一起传：名称写成 <项目>/<需求>
        for m in autos:
            m["name"] = f"{m['proj']}/{m['name']}"
    counts = defaultdict(int)
    for m in members:
        counts[m["name"]] += 1
    if any(c > 1 for c in counts.values()):
        allp = [os.path.abspath(d) for m in members for d in m["dirs"]]
        base = os.path.commonpath(allp) if len(allp) > 1 else os.path.dirname(allp[0])
        for m in members:
            if counts[m["name"]] > 1 and not m["named"]:
                notes.append(f"成员名重复，改用相对路径区分：{m['name']}")
                m["name"] = os.path.relpath(os.path.abspath(m["dirs"][0]), base).replace(os.sep, "/")
    return members, combos, no_raid


def ref(member, d, rid):
    rid = clean(rid)
    if "/" in rid:
        return rid
    if member is None:
        return f"{COMBO}/{rid}"
    if member["named"]:
        return f"{member['name']}/{os.path.basename(os.path.normpath(d))}/{rid}"
    return f"{member['name']}/{rid}"


def load_raid(d, notes):
    with open(os.path.join(d, RAID_FILE), encoding="utf-8") as f:
        tables = parse_tables(f.read())
    by = defaultdict(list)
    for section, rows in tables:
        if section in SECTIONS:
            by[section].extend(rows)
    missing = [s for s in SECTIONS if s not in {sec for sec, _ in tables}]
    if missing:
        notes.append(f"{os.path.join(d, RAID_FILE).replace(os.sep, '/')} 缺少小节：{'、'.join(missing)}（小节标题须为 ## 风险 / ## 假设 / ## 问题 / ## 依赖）")
    return by


def md_table(header, rows):
    if not rows:
        return "无\n"
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", BS + "|") for c in r) + " |")
    return "\n".join(out) + "\n"


def show(p):
    return os.path.normpath(p).replace(os.sep, "/")


# ---------- RAID 汇总 ----------

def rollup(members, combos, as_of, notes):
    out = [f"# 组合汇总（截至 {as_of.isoformat()}，脚本生成，核对后再用）", ""]
    out.append("成员：" + ("；".join(f"{m['name']}（{'、'.join(show(d) for d in m['dirs'])}）" for m in members) or "无"))
    if combos:
        out.append("组合层：" + "、".join(show(d) for d in combos))
    out.append("")

    level_rows, hot, overdue, bad_deps, combo_rows = [], [], [], [], []
    mode_members, provider = defaultdict(set), defaultdict(list)

    def scan(member, d, counts):
        label = member["name"] if member else COMBO
        for sec, rows in load_raid(d, notes).items():
            for row in rows:
                rid = ref(member, d, row.get("ID", ""))
                status = clean(row.get("状态", ""))
                closed = is_closed(status)
                due, bad_due = date_or_note(row.get("下次复核", ""))
                if bad_due:
                    notes.append(f"{rid} 的下次复核读不出（{clean(row.get('下次复核', ''))}），日期写成 YYYY-MM-DD")
                owner = clean(col(row, "负责人") or col(row, "我方负责人"))
                if due and due <= as_of and not closed:
                    overdue.append((rid, sec, status, due.isoformat(), owner))
                if closed:
                    continue
                if sec == "风险":
                    lv = level_of(row.get("等级", ""))
                    if lv is None:
                        notes.append(f"{rid} 的等级读不出（{clean(row.get('等级', '')) or '空'}），计入未判级")
                    counts[lv or "未判级"] += 1
                    ev = clean(row.get("证据", ""))
                    rm = re.search(r"同根\s*[:：]?\s*((?:[^\s/；;，,]+\s*/\s*)+[RI]\s*-\s*\d+\w*)", ev)
                    root = re.sub(r"\s+", "", rm.group(1)) if rm else ""
                    if "同根" in ev and not root:
                        notes.append(f"{rid} 的证据提到同根，但没读出组合条目编号（写成 同根：组合/R-xx）")
                    if member is None:
                        combo_rows.append((rid, sec, lv or "未判级", clean(row.get("风险", "")), owner))
                    elif lv in ("严重", "高"):
                        hot.append((rid, lv, clean(row.get("模式", "")), clean(row.get("风险", "")), clean(row.get("临近度", "")), owner, root))
                        if clean(row.get("模式", "")):
                            mode_members[clean(row["模式"])].add(label)
                elif sec in ("问题", "假设") and member is None:
                    combo_rows.append((rid, sec, clean(row.get("严重度", "") or row.get("把握度", "")), clean(row.get(sec, "")), owner))
                elif sec == "依赖" and member is not None:
                    dcell = col(row, "方向")
                    dirn = direction(dcell)
                    if dirn is None:
                        notes.append(f"{rid} 的方向读不出（{clean(dcell) or '空'}），按我方等待计；方向只写 进 或 出")
                    if dirn == "出":
                        continue  # 我方是提供方的那一行，由等待方汇报
                    need, bad_n = date_or_note(row.get("需要日期", ""))
                    commit, bad_c = date_or_note(row.get("承诺日期", ""))
                    slack_cell = clean(row.get("浮动", ""))
                    slack = parse_slack(slack_cell)
                    shown = slack_cell
                    if slack is None and not is_unknown(slack_cell):
                        notes.append(f"{rid} 的浮动读不出（{slack_cell}），写成整数或 🔶 算式 = 整数")
                    if slack is None and need and commit:
                        slack = workdays(commit, need)
                        shown = f"{slack}（按日期算）"
                    for bad, name in ((bad_n, "需要日期"), (bad_c, "承诺日期")):
                        if bad:
                            notes.append(f"{rid} 的{name}读不出（{clean(row.get(name, ''))}）")
                    if any(k in status for k in DEP_BAD) or (slack is not None and slack <= 5):
                        bad_deps.append((rid, clean(row.get("交付物", "")), clean(row.get("提供方负责人", "")), clean(row.get("需要日期", "")), clean(row.get("承诺日期", "")), shown, status))
                    who = clean(row.get("提供方负责人", ""))
                    if not is_unknown(who):
                        provider[who].append((label, rid))

    for m in members:
        counts = defaultdict(int)
        for d in m["dirs"]:
            scan(m, d, counts)
        level_rows.append((m["name"], *(counts.get(k, 0) for k in (*LEVELS, "未判级"))))
    for d in combos:
        scan(None, d, defaultdict(int))

    out += ["## 打开风险的等级计数（已缓解的仍算打开）", "", md_table(["成员", *LEVELS, "未判级"], level_rows)]
    out += ["## 成员的严重与高级打开风险（同根一栏有值的，在组合层合并处理）", "", md_table(["条目", "等级", "模式", "风险", "临近度", "负责人", "同根"], hot)]
    out += ["## 组合层自己的打开条目", "", md_table(["条目", "类别", "等级或程度", "内容", "负责人"], combo_rows)]
    conc = [(k, len(v), "、".join(sorted(v))) for k, v in sorted(mode_members.items()) if len(v) >= 2]
    out += ["## 集中：同一模式在两个以上成员有严重或高级风险（含已标同根的）", "", md_table(["模式", "成员数", "成员"], conc)]
    out += ["## 我方等待的有问题依赖（健康度 🟡 或 🔴：未确认、延误、受阻、有风险，或浮动不超过 5 个工作日）", "", md_table(["条目", "交付物", "提供方负责人", "需要日期", "承诺日期", "浮动", "状态"], bad_deps)]
    shared = []
    for who, items in sorted(provider.items()):
        ls = {lb for lb, _ in items}
        if len(ls) >= 2:
            shared.append((who, len(ls), "、".join(r for _, r in items)))
    out += ["## 同一提供方负责人压在多个成员上（同根风险线索）", "", md_table(["提供方负责人", "成员数", "依赖"], shared)]
    out += ["## 到期未复核（下次复核不晚于截至日期且未关闭）", "", md_table(["条目", "类别", "状态", "下次复核", "负责人"], overdue)]
    return out


# ---------- 资源 ----------

def resources(path, as_of, notes):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    first = text.split("\n", 1)[0]
    head = re.search(r"周期\s*([^（\n]+)", first)
    base = re.search(r"上次定基线[:：]\s*([^）)\n]+)", text)
    bd = parse_date(base.group(1)) if base else None
    if bd and (as_of - bd).days > 92:
        notes.append(f"资源分配表的基线是 {bd.isoformat()}，已超过一个季度没重定")

    items = defaultdict(list)  # (类型, 名称) -> [条目]
    for section, rows in parse_tables(text):
        for r in rows:
            name_v = col(r, "姓名或技能", "姓名")
            pct_v = col(r, "占比", "投入占比")
            if not any(clean(k).startswith(("姓名", "姓名或技能")) for k in r) or not any(clean(k).startswith(("占比", "投入占比")) for k in r):
                continue
            name = clean(name_v)
            if is_unknown(name):
                notes.append(f"资源表一行姓名未定（{name or '空'}），未计入")
                continue
            member = clean(r.get("成员", ""))
            pct = parse_pct(pct_v)
            if pct is None:
                notes.append(f"资源表 {name} · {member} 的占比读不准（{clean(pct_v) or '空'}），未计入；占比只写百分数，如 60%")
                continue
            avail_cell = col(r, "可用量", "可用")
            avail = parse_pct(avail_cell)
            if avail is None and not is_unknown(avail_cell):
                notes.append(f"资源表 {name} · {member} 的可用量读不准（{clean(avail_cell)}）")
            s_raw, e_raw = clean(r.get("起", "")), clean(r.get("止", ""))
            s, e = parse_date(s_raw), parse_date(e_raw)
            sec_period = re.match(r"周期\s*(.+)", section or "")
            period = clean(r.get("周期", "")) or (sec_period.group(1).strip() if sec_period else (head.group(1).strip() if head else ""))
            if (s_raw or e_raw) and not (s and e):
                notes.append(f"资源表 {name} · {member} 的起止日期不全或读不出（起 {s_raw or '空'}，止 {e_raw or '空'}），未计入；起止都写 YYYY-MM-DD")
                continue
            if not (s and e):  # 没写起止的，按所在周期的两个日期展开
                ds = re.findall(r"\d{4}\s*[-/.年]\s*\d{1,2}\s*[-/.月]\s*\d{1,2}", period)
                if len(ds) >= 2:
                    s, e = parse_date(ds[0]), parse_date(ds[1])
            kind_cell = clean(r.get("类型", ""))
            if "类型" in {clean(k) for k in r} and not kind_cell:
                notes.append(f"资源表 {name} · {member} 的类型没写，按人计；类型写 人 或 技能")
            kind = "技能" if "技能" in kind_cell else "人"
            items[(kind, name)].append({"member": member, "pct": pct, "soft": "意向" in clean(r.get("预订", "")), "s": s, "e": e, "period": period or "未写周期", "avail": avail})

    def windows(rows):
        """有起止日期的按重叠取各时段；没有日期的按周期标签合计。返回 [(窗口, 时段, 条目)]。"""
        res, seen = [], set()
        dated = [x for x in rows if x["s"] and x["e"]]
        undated = [x for x in rows if not (x["s"] and x["e"])]
        for day in sorted({x["s"] for x in dated}):
            grp = [x for x in dated if x["s"] <= day <= x["e"]]
            key = frozenset(id(x) for x in grp)
            if key in seen:
                continue
            seen.add(key)
            end = min(x["e"] for x in grp)
            when = "已过去" if end < as_of else ("当前" if day <= as_of else "将来")
            res.append((f"{day.isoformat()} → {end.isoformat()}", when, grp))
        for per in sorted({x["period"] for x in undated}):
            res.append((per, "未知", [x for x in undated if x["period"] == per]))
        if dated and undated:
            notes.append(f"资源表 {rows[0]['member']} 等行里同一人或技能既有带日期又有不带日期的行，两部分没法合并比较；请补起止日期")
        return res

    def fmt(v):
        return f"{v:g}%"

    cross, single, skill_rows, past = [], [], [], 0
    for (kind, name), rows in sorted(items.items()):
        for win, when, grp in windows(rows):
            if when == "已过去":
                past += 1
                continue
            tot = sum(x["pct"] for x in grp)
            conf = sum(x["pct"] for x in grp if not x["soft"])
            avails = [x["avail"] for x in grp if x["avail"] is not None]
            avail = min(avails) if avails else (100.0 if kind == "人" else None)
            mems = {x["member"] for x in grp}
            detail = "、".join(f"{x['member']} {fmt(x['pct'])}{'（意向）' if x['soft'] else ''}" for x in grp)
            if kind == "技能":
                if len(mems) >= 2 and (avail is None or tot > avail):
                    skill_rows.append((name, win, when, len(mems), fmt(tot), fmt(avail) if avail is not None else "🔵 未写", detail))
                continue
            if tot > avail:
                row = (name, win, when, fmt(tot), fmt(conf), fmt(avail), detail)
                (cross if len(mems) >= 2 else single).append(row)
    out = ["## 资源：超出可用量的人（两个以上成员，组合冲突；时段为当前的记问题，将来的记风险）", ""]
    out.append(md_table(["姓名", "窗口", "时段", "合计", "其中已确认", "可用量", "明细"], cross))
    out += ["## 资源：单个成员内部超出（不算组合冲突，交该成员自己排期）", "", md_table(["姓名", "窗口", "时段", "合计", "其中已确认", "可用量", "明细"], single)]
    out += ["## 资源：同一技能被多个成员同时要，且超出可用量或可用量未写", "", md_table(["技能", "窗口", "时段", "成员数", "需求合计", "可用量", "明细"], skill_rows)]
    if past:
        notes.append(f"资源表里有 {past} 个已过去的窗口，未列出")
    return out


# ---------- 入口 ----------

def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args, res, as_of, i = [], None, datetime.date.today(), 0
    while i < len(argv):
        a = argv[i]
        if a in ("--resources", "--as-of"):
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                print(f"error: {a} 后面要跟值", file=sys.stderr)
                return 2
            val, i = argv[i + 1], i + 2
        elif a.startswith(("--resources=", "--as-of=")):
            a, val = a.split("=", 1)
            i += 1
        elif a.startswith("--"):
            print(__doc__, file=sys.stderr)
            return 2
        else:
            args.append(a)
            i += 1
            continue
        if a == "--resources":
            res = val
        else:
            as_of = parse_date(val)
            if as_of is None:
                print("error: --as-of 要写成 YYYY-MM-DD", file=sys.stderr)
                return 2
    notes = []
    members, combos, no_raid = collect(args, notes)
    if not members and not combos:
        print("error: 没找到含 RAID日志.md 的成员目录", file=sys.stderr)
        for n in notes:
            print(f"- {n}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 2
    out = rollup(members, combos, as_of, notes)
    if res:
        if not os.path.isfile(res):
            print(f"error: 资源分配表不存在 {res}", file=sys.stderr)
            return 2
        out += resources(res, as_of, notes)
    out += ["## 有门禁记录或任务台账、但还没有 RAID 日志的需求目录", "", md_table(["目录"], [(show(d),) for d in sorted(no_raid)])]
    out += ["## 读不准与提示", ""]
    out += [f"- {n}" for n in notes] or ["无"]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
