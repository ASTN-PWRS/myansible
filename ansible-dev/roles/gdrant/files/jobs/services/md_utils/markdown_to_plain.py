import markdown2
import re

def markdown_to_plain(md_text: str):
    """
    Markdown → HTML → プレーンテキスト
    """
    # markdown2 で HTML に変換
    html = markdown2.markdown(md_text)

    # HTMLタグを除去してプレーンテキスト化
    plain = _strip_html_tags(html)

    return plain


def _strip_html_tags(html: str):
    """HTMLタグを除去してプレーンテキスト化"""
    # 改行を残しつつタグ除去
    text = re.sub(r"<[^>]+>", "", html)
    # 余計な空白を整形
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text.strip()
