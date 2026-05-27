class ToggleMenu extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });

    shadow.innerHTML = `
      <style>
        :host {
          display: inline-block;
        }

        button,
        button span {
          display: inline-block;
          box-sizing: border-box;
        }

        button {
          --scale: 1;

          position: relative;
          width: 50px;
          height: 44px;
          background: none;
          border: none;
          appearance: none;
          cursor: pointer;
          transition: 0.6s cubic-bezier(0.68, -0.5, 0.32, 1.6);
          transform: scale(var(--scale));
          transform-origin: center center;
        }

        button span {
          position: absolute;
          width: 100%;
          height: 4px;
          background: #fff;
          border-radius: 4px;
          transition: 0.3s 0.2s;
        }

        button span:nth-of-type(1) { top: 0; }
        button span:nth-of-type(2) { top: 20px; }
        button span:nth-of-type(3) { bottom: 0; }

        button.active {
          transform: scale(var(--scale)) rotate(180deg);
        }

        button.active span:nth-of-type(1) {
          transform: translateY(20px) rotate(-45deg);
        }

        button.active span:nth-of-type(2) {
          transform: translateY(0) rotate(45deg);
        }

        button.active span:nth-of-type(3) {
          opacity: 0;
        }

        /* サイズ */
        :host([size="small"]) button { --scale: 0.3; }
        :host([size="normal"]) button { --scale: 0.5; }
        :host([size="large"]) button { --scale: 1; }
      </style>

      <button>
        <span></span>
        <span></span>
        <span></span>
      </button>
    `;

    this.button = shadow.querySelector("button");
  }

  connectedCallback() {
    this.button.addEventListener("click", () => {
      this.button.classList.toggle("active");

      // 親の wa-page を探す
      const page = this.closest("wa-page");
      if (!page) return;

      // nav-state を open / closed で切り替え
      const current = page.getAttribute("nav-state");
      const next = current === "open" ? "closed" : "open";
      page.setAttribute("nav-state", next);
    });
  }
}

customElements.define("toggle-menu", ToggleMenu);
