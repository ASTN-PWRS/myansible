def extract_md_images(md_text: str):
    """
    Markdown の画像リンクを抽出
    返り値: [{"alt": "...", "path": "..."}]
    """
    pattern = re.compile(r"!

\[(.*?)\]

\((.*?)\)")
    images = []

    for alt, path in pattern.findall(md_text):
        images.append({
            "alt": alt.strip(),
            "path": path.strip()
        })

    return images
