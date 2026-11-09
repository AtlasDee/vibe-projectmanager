"""算 PRD 冻结版本的 md5（prd-review-gate.md 第 1 节）。只用 Python 标准库，Windows / macOS / Linux 通用。

用法：
    python prd_md5.py <文件>                  # 本地 md：整个文件（算法 本地整文件）
    python prd_md5.py <文件> --lark-export    # Lark_Bot 导出的云文档：剥掉固定文件头后的正文（算法 云文档正文）

口径：按 UTF-8 读入，换行统一为 \\n，去掉首尾空白，对 UTF-8 字节算 md5。
--lark-export 只剥掉导出脚本写的固定文件头：
    第 1 行 `# 标题`、空行、`> 来源：` 行（只有用链接导出时才有）、`> docx token：` 行、`> 导出方式：` 行、空行。
正文里同样以 `>` 开头的高亮块、引用块（例如开篇摘要）一字不跳。
文件头不符合这个结构时报错退出，不猜。

输出一行 ASCII：md5=<32 位十六进制> algo=<local|lark-export>
退出码：0 = 成功；2 = 用法错误或文件头不符。
"""
import hashlib
import sys

HEADER_PREFIXES = ("> 来源：", "> docx token：", "> 导出方式：")


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")


def strip_lark_header(text):
    lines = text.split("\n")
    if not lines or not lines[0].startswith("# "):
        raise ValueError("第 1 行不是 `# 标题`")
    i = 1
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    seen = []
    while i < len(lines) and lines[i].startswith(HEADER_PREFIXES):
        seen.append(lines[i])
        i += 1
    if not any(s.startswith("> docx token：") for s in seen) or not seen[-1:] or not seen[-1].startswith("> 导出方式："):
        raise ValueError("没找到以 `> 导出方式：` 结尾的导出文件头，可能不是 Lark_Bot 的导出文件")
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:])


def main(argv):
    for stream in (sys.stdout, sys.stderr):  # 非 UTF-8 终端（如 Windows 默认代码页）下中文报错也能读
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args =[a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    unknown = flags - {"--lark-export"}
    if len(args) != 1 or unknown:
        print(__doc__, file=sys.stderr)
        return 2
    text = read_text(args[0])
    algo = "local"
    if "--lark-export" in flags:
        try:
            text = strip_lark_header(text)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        algo = "lark-export"
    digest = hashlib.md5(text.strip().encode("utf-8")).hexdigest()
    print(f"md5={digest} algo={algo}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
