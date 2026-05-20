import Panzoom from "@panzoom/panzoom";

export async function loadImageToView(url) {
  const res = await fetch(url);
  const blob = await res.blob();

  const base64 = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
  const view = document.getElementById("imageview");
  const wrap = document.getElementById("panzoom-wrap");
  wrap.innerHTML = "";

  const img = document.createElement("img");
  img.src = base64;
  wrap.appendChild(img);

  let panzoom = null;
  let initialized = false;

  const ro = new ResizeObserver(() => {
    const rect = wrap.getBoundingClientRect();

    // 初期倍率が 0 → 0 以外になった瞬間に初期化
    if (!initialized && rect.width > 0) {
      initialized = true;
      initPanzoom(rect);
      const view = document.getElementById("imageview");
      const viewRect = view.getBoundingClientRect();
      // 表示領域に対する縦横の縮小率
      const scaleW = viewRect.width / img.naturalWidth;
      const scaleH = viewRect.height / img.naturalHeight;

      console.log("div width:", viewRect.width);
      console.log("div height:", viewRect.height);
      console.log("img width:", img.naturalWidth);
      console.log("img height:", img.naturalHeight);
      console.log(scaleW, scaleH);
      return;
    }

    // 初期化済み → リサイズ時は再初期化
    if (initialized) {
      initPanzoom(rect);
    }
  });

  ro.observe(wrap);

  function initPanzoom() {
    const view = document.getElementById("imageview");
    const viewRect = view.getBoundingClientRect();

    // 表示領域に対する縦横の縮小率
    const scaleW = viewRect.width / img.naturalWidth;
    const scaleH = viewRect.height / img.naturalHeight;

    // 小さい方のスケールを採用
    let scale = Math.min(scaleW, scaleH);

    // 初期スケールが 1 以上なら 1 に固定
    if (scale >= 1) scale = 1;

    console.log("div width:", viewRect.width);
    console.log("div height:", viewRect.height);
    console.log("img width:", img.naturalWidth);
    console.log("img height:", img.naturalHeight);
    console.log(scaleW, scaleH, scale);
    // Panzoom 再初期化
    panzoom = Panzoom(img, {
      minScale: scale,
      maxScale: scale * 5,
      startScale: scale,
      contain: "outside",
    });

    wrap.addEventListener("wheel", panzoom.zoomWithWheel);
  }
}
