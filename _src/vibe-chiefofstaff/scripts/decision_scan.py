"""决策日志扫描（references/decision-log.md 第 6 节）。只读不写，只用 Python 标准库，Windows / macOS / Linux 通用。

用法：
    python decision_scan.py <决策目录> [--as-of YYYY-MM-DD] [--soon N] [--since YYYY-MM-DD]

<决策目录>  幕僚/决策/：读其中的决策文件（DEC-*.md），对照 决策索引.md；不读 讨论记录/ 等子目录
--as-of     截至日期，默认今天；截止日早于它的未完成跟进算逾期，当天到期的算即将到期
--soon      即将到期的天数窗口，默认 7（含当天）
--since     从这天起（含）新定的决定、完成的跟进单列一节，周报用

输出一份 Markdown 到标准输出：概况、逾期、即将到期、复核日已到、待定、生效的决定、不再提起的提议、
索引核对、读不准。只汇总，不判断：是不是同一件事、要不要复核，由人读了再定。
退出码：0 = 已输出；2 = 用法错误或目录不存在。
"""
import datetime
import os
import re
import sys

INDEX = "决策索引.md"
ACTIVE, SUPERSEDED, VOID = "生效", "已被取代", "作废"
DEC_STATES = (ACTIVE, SUPERSEDED, VOID)
OPEN = ("未完成", "进行中")
FU_STATES = ("未完成", "进行中", "已完成", "取消")
NO_RESURFACE = "不再提起"
UNKNOWN = {"", "待定", "待更新", "tbd", "—", "-", "?", "？", "🔵"}
BS = chr(92)
USAGE = __doc__.split("\n\n")[1]


# ---------- 单元格与表格 ----------

def clean(cell):
    return (cell or "").replace("`", "").replace("**", "").strip()


def is_unknown(s):
    s = clean(s)
    return s.lower() in UNKNOWN or s.startswith("🔵")


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith(BS + "|"):
        s = s[:-1]
    cells, cur, i = [], "", 0
    while i < len(s):
        if s[i] == BS and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if s[i] == "|":
            cells.append(cur)
            cur = ""
        else:
            cur += s[i]
        i += 1
    cells.append(cur)
    return [clean(c) for c in cells]


def tables(lines):
    """返回 [(所在小节标题, 表头, [行...])]；行按表头对成 dict。"""
    out, section, i = [], "", 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^#{1,4}\s+(.*)$", line)
        if m:
            section = m.group(1).strip()
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s|:-]+\|\s*$", lines[i + 1]):
            head = split_row(line)
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = split_row(lines[j])
                rows.append({h: (cells[k] if k < len(cells) else "") for k, h in enumerate(head)})
                j += 1
            out.append((section, head, rows))
            i = j
            continue
        i += 1
    return out


def parse_date(s):
    s = clean(s)
    m = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", s)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


# ---------- 读文件 ----------

def read_decision(path, problems):
    name = os.path.basename(path)
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    title = next((l for l in lines if l.startswith("# ")), "")
    m = re.match(r"^#\s+(DEC-\d+)\s*(.*)$", title)
    num = m.group(1) if m else ""
    if not m:
        problems.append(f"{name}：标题不是 # DEC-<编号> <标题>")
    d = {"file": name, "id": num or name, "title": (m.group(2) if m else title[2:]).strip(),
         "fields": {}, "rejected": [], "followups": []}
    for section, head, rows in tables(lines):
        if head[:2] == ["字段", "内容"]:
            d["fields"] = {r["字段"]: r["内容"] for r in rows}
        elif "否决" in section and "提议" in head:
            d["rejected"].extend(rows)
        elif "跟进" in section and "事项" in head:
            d["followups"].extend(rows)
    f = d["fields"]
    if not f:
        problems.append(f"{name}：没有 字段 | 内容 表，跳过")
        return None
    d["state"] = f.get("状态", "")
    if d["state"] not in DEC_STATES:
        problems.append(f"{name}：状态 {d['state'] or '（空）'} 不是 生效 / 已被取代 / 作废 之一")
    for key in ("日期", "截止日", "复核日"):
        v = f.get(key, "")
        d[key] = parse_date(v)
        if d[key] is None and not is_unknown(v):
            problems.append(f"{name}：{key} {v} 不是 YYYY-MM-DD")
    if d["日期"] is None:
        problems.append(f"{name}：缺日期")
    for r in d["followups"]:
        # 指针行：事项写「见 <别处> <编号>」、状态留空，表示在别处（如助理的行动项台账）跟踪，不计入统计
        r["_ptr"] = r.get("事项", "").startswith("见 ") and not r.get("状态", "")
        if r["_ptr"]:
            continue
        r["_due"] = parse_date(r.get("截止", ""))
        r["_done"] = parse_date(r.get("完成日", ""))
        st = r.get("状态", "")
        if st not in FU_STATES:
            problems.append(f"{name} {r.get('编号', '?')}：跟进状态 {st or '（空）'} 不是 {' / '.join(FU_STATES)} 之一")
        if r["_due"] is None and not is_unknown(r.get("截止", "")):
            problems.append(f"{name} {r.get('编号', '?')}：截止 {r.get('截止')} 不是 YYYY-MM-DD")
        if st == "已完成" and r["_done"] is None:
            problems.append(f"{name} {r.get('编号', '?')}：已完成但没有完成日")
    return d


def read_index(path, problems):
    if not os.path.isfile(path):
        problems.append(f"没有 {INDEX}")
        return None
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    for _, head, rows in tables(lines):
        if "编号" in head and "文件" in head:
            return rows
    problems.append(f"{INDEX}：没有含 编号、文件 两列的表")
    return None


# ---------- 输出 ----------

def table(head, rows):
    if not rows:
        return ["无", ""]
    esc = lambda c: str(c).replace("|", BS + "|")
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return out + [""]


def main(argv):
    args, opts, i = [], {"--as-of": None, "--soon": "7", "--since": None}, 0
    while i < len(argv):
        a = argv[i]
        if a in opts:
            if i + 1 >= len(argv):
                return usage(f"{a} 缺少取值")
            opts[a] = argv[i + 1]
            i += 2
        elif a.startswith("-"):
            return usage(f"不认识的参数 {a}")
        else:
            args.append(a)
            i += 1
    if len(args) != 1:
        return usage("要给且只给一个决策目录")
    root = args[0]
    if not os.path.isdir(root):
        return usage(f"目录不存在：{root}")
    as_of = parse_date(opts["--as-of"]) if opts["--as-of"] else datetime.date.today()
    since = parse_date(opts["--since"]) if opts["--since"] else None
    if as_of is None or (opts["--since"] and since is None):
        return usage("日期要写成 YYYY-MM-DD")
    if not opts["--soon"].isdigit():
        return usage("--soon 要是非负整数")
    soon = int(opts["--soon"])

    problems, decisions = [], []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if not os.path.isfile(full) or not name.endswith(".md") or name == INDEX:
            continue
        d = read_decision(full, problems)
        if d:
            decisions.append(d)
    index = read_index(os.path.join(root, INDEX), problems)

    by_state = {s: [d for d in decisions if d["state"] == s] for s in DEC_STATES}
    active = by_state[ACTIVE]
    fus = [(d, r) for d in active for r in d["followups"] if not r["_ptr"]]
    ptrs = sum(1 for d in active for r in d["followups"] if r["_ptr"])
    count = {s: sum(1 for _, r in fus if r.get("状态") == s) for s in FU_STATES}
    overdue = [(d, r) for d, r in fus if r.get("状态") in OPEN and r["_due"] and r["_due"] < as_of]
    upcoming = [(d, r) for d, r in fus if r.get("状态") in OPEN and r["_due"] and 0 <= (r["_due"] - as_of).days < soon]
    review = [d for d in active if d["复核日"] and d["复核日"] <= as_of]

    out = [f"# 决策扫描（截至 {as_of}）", "", f"目录：{root}", "", "## 概况", ""]
    out.append(f"- 决定：生效 {len(active)}，已被取代 {len(by_state[SUPERSEDED])}，作废 {len(by_state[VOID])}，"
               f"状态不明 {len(decisions) - sum(len(v) for v in by_state.values())}")
    out.append(f"- 生效决定的跟进：未完成 {count['未完成']}，进行中 {count['进行中']}，已完成 {count['已完成']}，取消 {count['取消']}"
               f"；其中逾期 {len(overdue)}，{soon} 天内到期 {len(upcoming)}"
               + (f"；另有 {ptrs} 条指向别处跟踪，不计入" if ptrs else ""))
    out.append(f"- 复核日已到的生效决定：{len(review)}")
    out.append("")

    out += [f"## 逾期的跟进（{len(overdue)}）", ""]
    overdue.sort(key=lambda x: (x[1]["_due"], x[0]["id"]))
    out += table(["跟进", "事项", "负责人", "截止", "逾期天数"],
                 [[f"{d['id']}/{r.get('编号', '?')}", r.get("事项", ""), r.get("负责人", "") or "（空）",
                   r["_due"], (as_of - r["_due"]).days] for d, r in overdue])

    out += [f"## {soon} 天内到期的跟进（{len(upcoming)}）", ""]
    upcoming.sort(key=lambda x: (x[1]["_due"], x[0]["id"]))
    out += table(["跟进", "事项", "负责人", "截止", "剩余天数"],
                 [[f"{d['id']}/{r.get('编号', '?')}", r.get("事项", ""), r.get("负责人", "") or "（空）",
                   r["_due"], (r["_due"] - as_of).days] for d, r in upcoming])

    out += [f"## 复核日已到的决定（{len(review)}）", ""]
    out += table(["决定", "日期", "内容", "负责人", "复核日"],
                 [[d["id"], d["日期"] or "", d["fields"].get("决定", ""), d["fields"].get("负责人", ""), d["复核日"]]
                  for d in sorted(review, key=lambda d: (d["复核日"], d["id"]))])

    pending = []
    for d in active:
        for key in ("负责人", "截止日", "复核日"):
            if is_unknown(d["fields"].get(key, "")):
                pending.append([d["id"], key, d["fields"].get(key, "") or "（空）"])
        for r in d["followups"]:
            if r["_ptr"] or r.get("状态") not in OPEN:
                continue
            for key in ("负责人", "截止"):
                if is_unknown(r.get(key, "")):
                    pending.append([f"{d['id']}/{r.get('编号', '?')}", key, r.get(key, "") or "（空）"])
    out += [f"## 待定（{len(pending)}）", "", "生效决定及其未完成跟进里，负责人、日期还没定的：", ""]
    out += table(["出处", "字段", "当前值"], pending)

    if since:
        new = [d for d in decisions if d["日期"] and since <= d["日期"] <= as_of]
        done = [(d, r) for d in decisions for r in d["followups"]
                if not r["_ptr"] and r.get("状态") == "已完成" and r["_done"] and since <= r["_done"] <= as_of]
        out += [f"## 自 {since} 起", "", f"新定的决定（{len(new)}）：", ""]
        out += table(["决定", "日期", "内容", "状态"],
                     [[d["id"], d["日期"], d["fields"].get("决定", ""), d["state"]] for d in new])
        out += [f"完成的跟进（{len(done)}）：", ""]
        out += table(["跟进", "事项", "完成日", "结果"],
                     [[f"{d['id']}/{r.get('编号', '?')}", r.get("事项", ""), r["_done"], r.get("结果", "")]
                      for d, r in sorted(done, key=lambda x: (x[1]["_done"], x[0]["id"]))])

    out += [f"## 生效的决定（{len(active)}）", "", "写新决定前对照：同一件事是否已有生效的决定、负责人是否冲突。", ""]
    out += table(["决定", "日期", "内容", "负责人"],
                 [[d["id"], d["日期"] or "", d["fields"].get("决定", ""), d["fields"].get("负责人", "")] for d in active])

    rejected = [[d["id"], r.get("提议", ""), r.get("理由", "")] for d in decisions for r in d["rejected"]
                if NO_RESURFACE in r.get("标记", "")]
    out += [f"## 标了不再提起的提议（{len(rejected)}）", ""]
    out += table(["出处", "提议", "理由"], rejected)

    idx_notes = []
    if index is not None:
        files = {d["file"]: d for d in decisions}
        listed = set()
        for r in index:
            fn = r.get("文件", "")
            listed.add(fn)
            if fn not in files:
                idx_notes.append(f"索引有 {r.get('编号', '?')}，但没有文件 {fn}")
            elif r.get("状态", "") and r.get("状态") != files[fn]["state"]:
                idx_notes.append(f"{r.get('编号', '?')}：索引状态 {r.get('状态')}，文件状态 {files[fn]['state']}")
        for fn in sorted(set(files) - listed):
            idx_notes.append(f"文件 {fn} 没登记在索引里")
    for d in decisions:
        by = d["fields"].get("被取代于", "")
        no_by = is_unknown(by) or by == "无"
        if d["state"] == SUPERSEDED and no_by:
            idx_notes.append(f"{d['id']} 状态为已被取代，但 被取代于 没写是哪个决定")
        elif d["state"] == ACTIVE and not no_by:
            idx_notes.append(f"{d['id']} 状态为生效，但 被取代于 写了 {by}")
        if d["state"] in (SUPERSEDED, VOID):
            n = sum(1 for r in d["followups"] if not r["_ptr"] and r.get("状态") in OPEN)
            if n:
                idx_notes.append(f"{d['id']} 已{('被取代' if d['state'] == SUPERSEDED else '作废')}，名下仍有 {n} 条未完成跟进（未计入上面的统计）")
    out += [f"## 索引核对（{len(idx_notes)}）", ""]
    out += [f"- {n}" for n in idx_notes] or ["无"]
    out.append("")

    out += [f"## 读不准（{len(problems)}）", ""]
    out += [f"- {p}" for p in problems] or ["无"]
    sys.stdout.write("\n".join(out) + "\n")
    return 0


def usage(msg):
    sys.stderr.write(f"{msg}\n\n{USAGE}\n")
    return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
