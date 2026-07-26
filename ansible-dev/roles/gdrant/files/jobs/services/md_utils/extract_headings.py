import re

def extract_headings(md_text: str):
    """
    Markdown の見出し (#, ##, ###...) を抽出して
    ["H1: タイトル", "H2: 概要", ...] の形式で返す
    """
    headings = []
    pattern = re.compile(r"^(#{1,6})\s+(.*)", flags=re.MULTILINE)

    for hashes, title in pattern.findall(md_text):
        level = len(hashes)
        clean_title = title.strip()
        headings.append(f"H{level}: {clean_title}")

    return headings
