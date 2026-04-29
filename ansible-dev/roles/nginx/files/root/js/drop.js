const dropZone = document.getElementById("drop-zone");

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");

  const files = [...e.dataTransfer.files]; // ← 複数ファイル対応
  console.log("Dropped files:", files);

  // ここでアップロード処理へ渡す
  // uploadFiles(files)
});
