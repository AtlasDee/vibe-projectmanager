"""行动项检查与扫描（vibe-assistant）。只读，只用 Python 标准库。

用法：
    python action_items.py check <纪要或通话文件>...
    python action_items.py scan <助理目录> [--today YYYY-MM-DD] [--soon N] [--owner 姓名]

check：检查纪要（# 会议纪要 / # 站会纪要）或通话文件（# 通话总结）
  - 必备的节都在、不为空（没有的写 无）
  - 行动项：编号 A<n> 不重复；事项、负责人、截止、验收标准都填了；负责人只有一个人；
    截止是 YYYY-MM-DD（可加括号写原话）或 待定（待定（注释）、TBD、? 也按待定算）
  - 决定（纪要）：编号 D<n>，拍板人、理由都填了
  - 待议区（纪要）：编号 P<n>，为什么没定、下一步、建议负责人都填了
  - 状态为 定稿 / 已确认 的文件：行动项不许 待定，待你确认 一节要清空；草稿里的 待定 只提示
scan：读 <助理目录>/行动项.md，列出逾期、今天到期、即将到期、阻塞、待定；
  核对定稿纪要和已确认通话里的行动项是否都登记进台账、纪要与通话有没有同名、台账的来源文件是否存在
只查上面这些；必备节以外的节（议程、风险与阻塞、下次会议等）和验收标准写得对不对，靠人工自检。
退出码：check 0 = 无问题，1 = 有问题；scan 0 = 读完（有没有逾期都是 0），1 = 台账不存在或读不了；
  2 = 用法错误。
"""
import datetime as dt
import glob
import os
import re
import sys

DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*(?:[（(].*[)）])?$")  # 允许 2026-11-20（原话：下周前）
MULTI_OWNER = re.compile(r"[、/，,；;&+]|\S{2,}[和与及]\S{2,}")
PENDING_WORDS = ("tbd", "tba", "?", "？", "—", "-", "未定", "不详")
OPEN = ("未开始", "进行中", "阻塞")
STATUSES = OPEN + ("已完成", "已取消")
PENDING = "待定"

KINDS = {
    "会议纪要": ("纪要", ["元信息", "参会", "摘要", "决定", "行动项", "待议区", "附件与出处", "版本记录"]),
    "站会纪要": ("纪要", ["元信息", "参会", "行动项", "待议区"]),
    "通话总结": ("通话", ["摘要", "决定", "行动项", "下次会面"]),
}
FINAL = ("定稿", "已确认")


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def is_pending(v):
    """空、待定（含 待定（问组织者） 这类带注释的）、TBD、? 等都算没定。"""
    v = v.strip().strip("*`").strip()
    return not v or v.startswith(PENDING) or v.lower() in PENDING_WORDS


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    parts = re.split(r"(?<!\\)\|", s)
    return [p.strip().replace("\\|", "|").strip("`").strip() for p in parts]


def tables(text):
    """返回文本里的表格：[(表头, [行...]), ...]，行是 {列名: 值}。"""
    out = []
    lines = [x.strip() for x in text.split("\n")]  # 容许缩进的表格
    i = 0
    while i < len(lines):
        if (lines[i].startswith("|") and i + 1 < len(lines)
                and re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$", lines[i + 1])):
            head = cells(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                vals = cells(lines[j])
                rows.append(dict(zip(head, vals + [""] * (len(head) - len(vals)))))
                j += 1
            out.append((head, rows))
            i = j
        else:
            i += 1
    return out


def sections(text):
    """按二级标题切节：{节名: 内容}。节名去掉开头的编号（如 1、2.1）和结尾的（n）计数。"""
    out = {}
    cur = None
    for line in text.split("\n"):
        m = re.match(r"^##(?!#)\s*(.+?)\s*$", line)
        if m:
            name = re.sub(r"^\d+(?:\.\d+)*\s+", "", m.group(1))
            name = re.sub(r"[（(]\d+[)）]$", "", name).strip()
            cur = name
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def is_none(body):
    return body.strip() in ("无", "- 无", "`无`")


def kind_of(text):
    m = re.search(r"^# (会议纪要|站会纪要|通话总结)\b", text, re.M)
    return m.group(1) if m else None


def status_of(text):
    m = re.search(r"^[*\s]*状态[*\s]*[:：]\s*(.+)$", text, re.M)
    if not m:
        return ""
    v = re.split(r"[（(\s]", m.group(1).strip().strip("*`").strip(), maxsplit=1)[0]
    return v.strip("*`")


def actions_in(text):
    body = sections(text).get("行动项", "")
    tb = tables(body)
    return tb[0] if tb else (None, [])


# ---------------------------------------------------------------- check
def check_file(path):
    probs, hints = [], []
    try:
        text = read(path)
    except (OSError, UnicodeDecodeError) as e:
        return [f"读不了（要 UTF-8 文本）：{e.__class__.__name__}"], []
    k = kind_of(text)
    if not k:
        return ["不是纪要或通话文件：一级标题应以 会议纪要、站会纪要 或 通话总结 开头"], []
    kind, required = KINDS[k]
    status = status_of(text)
    final = status in FINAL
    if not status:
        hints.append("没有 状态 行，按草稿检查")
    secs = sections(text)

    for name in required:
        if name not in secs:
            probs.append(f"缺少一节：{name}")
        elif not secs[name]:
            probs.append(f"{name} 一节为空：没有的写 无")

    def need(row, cols, where):
        for c in cols:
            if not row.get(c, "").strip():
                probs.append(f"{where}：{c} 为空")

    # 行动项
    if "行动项" in secs and secs["行动项"] and not is_none(secs["行动项"]):
        head, rows = actions_in(text)
        if head is None:
            probs.append("行动项一节没有表格")
        else:
            miss = [c for c in ("编号", "事项", "负责人", "截止", "验收标准") if c not in head]
            if miss:
                probs.append(f"行动项表缺列：{'、'.join(miss)}")
            seen = set()
            ids = [r.get("编号", "") for r in rows]
            for n, r in enumerate(rows, 1):
                rid = r.get("编号", "")
                where = f"行动项 {rid or '(无编号)'}" + (f"（第 {n} 行）" if ids.count(rid) > 1 else "")
                if not re.match(r"^A\d+$", rid):
                    probs.append(f"{where}：编号应为 A<n>")
                elif rid in seen:
                    probs.append(f"{where}：编号重复")
                seen.add(rid)
                need(r, ("事项", "负责人", "截止", "验收标准"), where)
                owner, due = r.get("负责人", ""), r.get("截止", "")
                if owner and not is_pending(owner) and MULTI_OWNER.search(owner):
                    probs.append(f"{where}：负责人只写一个人（{owner}），其余写进台账备注")
                if due and not is_pending(due) and not valid_date(due):
                    probs.append(f"{where}：截止应为 YYYY-MM-DD（可加括号写原话）或 待定（{due}）")
                for c, v in (("负责人", owner), ("截止", due)):
                    if v and is_pending(v):
                        (probs if final else hints).append(
                            f"{where}：{c} 待定" + ("，定稿前要补上或移进待议区" if final else "，定稿前要补上"))

    # 决定（纪要用表格）
    if kind == "纪要" and secs.get("决定") and not is_none(secs["决定"]):
        tb = tables(secs["决定"])
        if not tb:
            probs.append("决定一节没有表格")
        else:
            for r in tb[0][1]:
                rid = r.get("编号", "")
                where = f"决定 {rid or '(无编号)'}"
                if not re.match(r"^D\d+$", rid):
                    probs.append(f"{where}：编号应为 D<n>")
                need(r, ("决定", "拍板人", "理由"), where)

    # 待议区
    if kind == "纪要" and secs.get("待议区") and not is_none(secs["待议区"]):
        tb = tables(secs["待议区"])
        if not tb:
            probs.append("待议区一节没有表格")
        else:
            seen = set()
            for r in tb[0][1]:
                rid = r.get("编号", "")
                where = f"待议区 {rid or '(无编号)'}"
                if not re.match(r"^P\d+$", rid):
                    probs.append(f"{where}：编号应为 P<n>")
                elif rid in seen:
                    probs.append(f"{where}：编号重复")
                seen.add(rid)
                need(r, ("事项", "为什么没定", "下一步", "建议负责人"), where)

    if final and secs.get("待你确认") and not is_none(secs["待你确认"]):
        probs.append(f"状态为 {status}，待你确认 一节还没清空")
    return probs, hints


def parse_date(s):
    m = DATE.match(s.strip())
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def valid_date(s):
    return parse_date(s) is not None


def cmd_check(paths):
    total = 0
    for p in paths:
        probs, hints = check_file(p)
        total += len(probs)
        print(f"## {os.path.basename(p)}")
        for x in probs:
            print(f"- 问题：{x}")
        for x in hints:
            print(f"- 提示：{x}")
        if not probs and not hints:
            print("- 无问题")
    print(f"\n{'OK' if total == 0 else 'FAIL'}：{total} 个问题")
    return 0 if total == 0 else 1


# ---------------------------------------------------------------- scan
def load_ledger(path):
    for head, rows in tables(read(path)):
        if all(c in head for c in ("编号", "负责人", "截止", "状态")):
            return rows
    return None


def cmd_scan(root, today, soon, owner):
    ledger_path = os.path.join(root, "行动项.md")
    if not os.path.isfile(ledger_path):
        print(f"台账不存在：{root.rstrip('/')}/行动项.md")
        return 1
    try:
        rows = load_ledger(ledger_path)
    except (OSError, UnicodeDecodeError) as e:
        print(f"台账读不了（要 UTF-8 文本）：{e.__class__.__name__}")
        return 1
    if rows is None:
        print("台账里没有含 编号、负责人、截止、状态 四列的表格")
        return 1

    bad, dup, seen = [], [], set()
    soon_key = f"{soon} 天内到期"
    cats = {"逾期": [], "今天到期": [], soon_key: [], "阻塞": [], "待定": []}
    if soon == 0:
        del cats[soon_key]
    count = {s: 0 for s in STATUSES}
    for r in rows:
        rid, st = r.get("编号", ""), r.get("状态", "").strip("*` ")
        if rid in seen:
            dup.append(rid)
        seen.add(rid)
        if st not in STATUSES:
            bad.append(f"{rid}：状态读不准（{st or '空'}），应为 {'、'.join(STATUSES)}")
            continue
        count[st] += 1
        if st not in OPEN:
            continue
        due, who = r.get("截止", ""), r.get("负责人", "")
        if is_pending(who) or is_pending(due):
            cats["待定"].append((r, "负责人待定" if is_pending(who) else "截止待定"))
        if st == "阻塞":
            cats["阻塞"].append((r, ""))
        if is_pending(due):
            continue
        d = parse_date(due)
        if d is None:
            bad.append(f"{rid}：截止读不准（{due}）")
            continue
        if d < today:
            cats["逾期"].append((r, f"逾期 {(today - d).days} 天"))
        elif d == today:
            cats["今天到期"].append((r, ""))
        elif (d - today).days <= soon:
            cats[soon_key].append((r, f"还有 {(d - today).days} 天"))

    # 定稿纪要、已确认通话里的行动项是否都已登记
    unreg, nosrc, clash, unreadable = [], [], [], []
    stems = {}
    for sub in ("纪要", "通话"):
        for p in sorted(glob.glob(os.path.join(root, sub, "*.md"))):
            stem = os.path.splitext(os.path.basename(p))[0]
            stems.setdefault(stem, []).append(sub)
            try:
                text = read(p)
            except (OSError, UnicodeDecodeError) as e:
                unreadable.append(f"{sub}/{stem}.md：读不了（要 UTF-8 文本）：{e.__class__.__name__}")
                continue
            if status_of(text) not in FINAL:
                continue
            for r in actions_in(text)[1]:
                rid = r.get("编号", "")
                if rid and f"{stem}/{rid}" not in seen:
                    unreg.append(f"{stem}/{rid} {r.get('事项', '')}（{sub}/{stem}.md）")
    for stem, subs in sorted(stems.items()):
        if len(subs) > 1:
            clash.append(f"{stem}：纪要/ 和 通话/ 下同名，行动项编号会撞，改一个简称")
    for r in rows:
        src = r.get("来源", "")
        if src and not os.path.isfile(os.path.join(root, src)):
            nosrc.append(f"{r.get('编号', '')}：来源 {src} 不存在")

    print(f"# 行动项扫描 · 截至 {today.isoformat()}")
    print()
    print("状态：" + "　".join(f"{s} {count[s]}" for s in STATUSES))
    for name, items in cats.items():
        print(f"\n## {name}（{len(items)}）")
        groups = [(None, items)]
        if owner:
            groups = [(f"{owner} 负责", [x for x in items if x[0].get("负责人") == owner]),
                      ("其他人", [x for x in items if x[0].get("负责人") != owner])]
        for label, its in groups:
            if label:
                print(f"### {label}（{len(its)}）")
            for r, note in sorted(its, key=lambda x: (x[0].get("截止", ""), x[0].get("编号", ""))):
                extra = f" · {note}" if note else ""
                print(f"- {r.get('编号', '')} {r.get('事项', '')} · {r.get('负责人', '') or '空'} · "
                      f"{r.get('截止', '') or '空'}{extra}")
    for title, items in (("未登记进台账", unreg), ("编号重复", sorted(set(dup))),
                         ("纪要与通话同名", clash), ("来源文件不存在", nosrc), ("读不准", bad + unreadable)):
        if items:
            print(f"\n## {title}（{len(items)}）")
            for x in items:
                print(f"- {x}")
    return 0


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "scan"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[0] == "check":
        return cmd_check(argv[1:])
    root, rest = argv[1], argv[2:]
    today, soon, owner = dt.date.today(), 3, ""
    i = 0
    try:
        while i < len(rest):
            if rest[i] == "--today":
                today = dt.date.fromisoformat(rest[i + 1])
            elif rest[i] == "--soon":
                soon = int(rest[i + 1])
                if soon < 0:
                    raise ValueError
            elif rest[i] == "--owner":
                owner = rest[i + 1]
            else:
                raise ValueError
            i += 2
    except (IndexError, ValueError):
        print(f"参数读不准：{' '.join(rest)}\n\n{__doc__.strip()}", file=sys.stderr)
        return 2
    return cmd_scan(root, today, soon, owner)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
