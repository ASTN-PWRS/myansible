class ThemeToggle extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    this.root = document.documentElement;

    const saved = localStorage.getItem("theme");
    if (saved === "light") {
      this.root.classList.remove("wa-dark");
      this.root.classList.add("wa-light");
    } else {
      this.root.classList.remove("wa-light");
      this.root.classList.add("wa-dark");
    }

    this.render();
  }

  connectedCallback() {
    this.shadowRoot
      .querySelector("wa-button")
      .addEventListener("click", () => this.toggle());
  }

  toggle() {
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

    this.render();
  }

  render() {
    const isDark = this.root.classList.contains("wa-dark");
    const label = isDark ? "☀️ Light" : "🌙 Dark";

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: inline-block;
        }
      </style>

      <wa-button appearance="plain">${label}</wa-button>
    `;
  }
}

customElements.define("theme-toggle", ThemeToggle);
