class ThemeToggle extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: inline-block;
        }
        wa-icon {
          font-size: 1.2rem;
        }
      </style>

      <wa-button id="btn" variant="neutral" appearance="plain">
        <wa-icon id="icon" name="sun"></wa-icon>
      </wa-button>
    `;
  }

  connectedCallback() {
    this.btn = this.shadowRoot.getElementById("btn");
    this.icon = this.shadowRoot.getElementById("icon");
    this.root = document.documentElement;

    // 初期化
    const saved = localStorage.getItem("theme");
    if (saved === "light") {
      this.root.classList.remove("wa-dark");
      this.root.classList.add("wa-light");
    } else {
      this.root.classList.remove("wa-light");
      this.root.classList.add("wa-dark");
    }

    this.updateIcon();

    this.btn.addEventListener("click", () => {
      const isDark = this.root.classList.contains("wa-dark");

      if (isDark) {
        this.root.classList.remove("wa-dark");
        this.root.classList.add("wa-light");
        localStorage.setItem("theme", "light");
      } else {
        this.root.classList.remove("wa-light");
        this.root.classList.add("wa-dark");
        localStorage.setItem("theme", "dark");
      }

      this.updateIcon();
    });
  }

  updateIcon() {
    const isDark = this.root.classList.contains("wa-dark");

    if (isDark) {
      this.icon.name = "sun";
      this.icon.style.color = "red"; // ← sun のとき赤
    } else {
      this.icon.name = "moon";
      this.icon.style.color = "yellow"; // ← moon のとき黄色
    }
  }
}

customElements.define("theme-toggle", ThemeToggle);
