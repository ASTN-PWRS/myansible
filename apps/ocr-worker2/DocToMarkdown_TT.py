class DocToMarkdown_TT:
    def __init__(self):
        self.converter = MixedImageToMarkdown()

    def run(self, input_path, output_path, tmp_dir="/tmp/doc2md"):
        os.makedirs(tmp_dir, exist_ok=True)

        # 1. 画像抽出
        if input_path.endswith(".docx"):
            images = extract_images_from_docx(input_path, tmp_dir)
        elif input_path.endswith(".pdf"):
            images = extract_images_from_pdf(input_path, tmp_dir)
        else:
            raise ValueError("Unsupported file type")

        # 2. 各画像を Markdown に変換
        md_all = []
        for img in images:
            md = self.converter.convert(img)
            md_all.append(md)

        # 3. 結合
        final_md = "\n\n---\n\n".join(md_all)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_md)

        return output_path
