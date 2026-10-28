import io
import json
from pathlib import Path

def read_file_by_ext(path: str, max_chars: int = 2000) -> str:
    """根据文件后缀读取内容，返回字符串（可截断）。"""
    p = Path(path)
    ext = p.suffix.lower()

    # ---------- 纯文本类 ----------
    if ext in {".txt", ".md", ".log", ".py", ".js", ".java", ".c", ".cpp",
               ".json", ".xml", ".html", ".css", ".yml", ".yaml", ".ini", ".conf"}:
        return _read_text(p, max_chars)

    # ---------- CSV / Excel ----------
    if ext in {".csv", ".xlsx", ".xls"}:
        return _read_table(p, max_chars)

    # ---------- PDF ----------
    if ext == ".pdf":
        try:
            import pdfplumber
        except ImportError:
            return "[需要安装: pip install pdfplumber]"
        with pdfplumber.open(p) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages[:3])
        return text[:max_chars] or "[PDF 无可提取文字（可能是扫描件）]"

    # ---------- Word ----------
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            return "[需要安装: pip install python-docx]"
        doc = Document(p)
        text = "\n".join(par.text for par in doc.paragraphs)
        return text[:max_chars] or "[文档中无段落文字]"

    # ---------- 图片：返回基本信息 ----------
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
        try:
            from PIL import Image
        except ImportError:
            return "[需要安装: pip install pillow]"
        img = Image.open(p)
        return f"[图片] 尺寸: {img.size[0]}x{img.size[1]}, 模式: {img.mode}, 格式: {img.format}, 大小: {p.stat().st_size} 字节"

    # ---------- 未知/二进制 ----------
    if ext not in {""}:
        return f"[不支持解析 .{ext} 的内容，仅显示信息] 文件大小: {p.stat().st_size} 字节"
    return "[文件无扩展名，无法判断类型]"


def _read_text(p: Path, max_chars: int) -> str:
    """文本文件按编码读取：优先 UTF-8，失败退回 GBK。"""
    for enc in ("utf-8", "gbk"):
        try:
            text = p.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:  # 都失败就忽略错误读
        text = p.read_text(encoding="utf-8", errors="ignore")
    return text[:max_chars]


def _read_table(p: Path, max_chars: int) -> str:
    try:
        import pandas as pd
    except ImportError:
        return "[需要安装: pip install pandas openpyxl]"

    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p, nrows=50)          # 只读前50行，防大文件卡死
    else:
        df = pd.read_excel(p, nrows=50)

    out = io.StringIO()
    df.head(20).to_string(buf=out)             # 前20行预览
    summary = f"表格: {df.shape[0]} 行 × {df.shape[1]} 列（预览前20行）\n\n{out.getvalue()}"
    return summary[:max_chars]
