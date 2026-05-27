class HumburgerMenu extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });

    shadow.innerHTML = `
      <style>
        /* 基本（menu05 の元サイズ） */
        .menu-trigger,
        .menu-trigger span {
          display: inline-block;
          box-sizing: border-box;
        }

        .menu-trigger {
          --scale: 0.5; /* デフォルト normal */

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

        .menu-trigger span {
          position: absolute;
          width: 100%;
          height: 4px;
          background: #fff;
          border-radius: 4px;
          transition: 0.3s 0.2s;
        }

        /* 3本線の位置（元のまま） */
        .menu-trigger span:nth-of-type(1) {
          top: 0;
          left: 0;
        }
        .menu-trigger span:nth-of-type(2) {
          top: 20px;
          left: 0;
        }
        .menu-trigger span:nth-of-type(3) {
          bottom: 0;
          left: 0;
        }

        /* active 時 */
        .menu-trigger.active {
          transform: scale(var(--scale)) rotate(180deg);
        }

        .menu-trigger.active span:nth-of-type(1) {
          transform: translateY(20px) rotate(-45deg);
        }

        .menu-trigger.active span:nth-of-type(2) {
          transform: translateY(0) rotate(45deg);
        }

        .menu-trigger.active span:nth-of-type(3) {
          opacity: 0;
        }

        /* サイズバリエーション（scale だけ変更） */
        :host(.small) .menu-trigger {
          --scale: 0.3;
        }

        :host(.normal) .menu-trigger {
          --scale: 0.5; /* デフォルト */
        }

        :host(.large) .menu-trigger {
          --scale: 1;
        }
      </style>

      <button class="menu-trigger">
        <span></span>
        <span></span>
        <span></span>
      </button>
    `;
  }

  connectedCallback() {
    const btn = this.shadowRoot.querySelector(".menu-trigger");

    btn.addEventListener("click", () => {
      btn.classList.toggle("active");

      this.dispatchEvent(
        new CustomEvent("toggle", {
          detail: { active: btn.classList.contains("active") },
        }),
      );
    });
  }
}

customElements.define("humburger-menu", HumburgerMenu);
