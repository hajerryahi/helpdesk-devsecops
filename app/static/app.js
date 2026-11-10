// HelpDesk - animations de l'interface
(function () {
  "use strict";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Apparition en cascade au defilement
  const reveal = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      e.target.querySelectorAll(".ring").forEach((r) => r.classList.add("go"));
      const num = e.target.querySelector("[data-count]");
      if (num) countUp(num);
      reveal.unobserve(e.target);
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach((el) => reveal.observe(el));

  // Compteurs animes
  function countUp(el) {
    const target = parseInt(el.dataset.count, 10) || 0;
    if (reduced || target === 0) { el.textContent = target; return; }
    const duration = 1100;
    const start = performance.now();
    function tick(now) {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * eased);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // Effet d'onde sur les boutons
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn");
    if (!btn || reduced) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const dot = document.createElement("span");
    dot.className = "ripple";
    dot.style.width = dot.style.height = size + "px";
    dot.style.left = e.clientX - rect.left - size / 2 + "px";
    dot.style.top = e.clientY - rect.top - size / 2 + "px";
    btn.appendChild(dot);
    setTimeout(() => dot.remove(), 650);
  });

  // Halo qui suit la souris sur les cartes de ticket
  document.querySelectorAll(".tcard").forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty("--mx", e.clientX - r.left + "px");
      card.style.setProperty("--my", e.clientY - r.top + "px");
    });
  });

  // Notifications : fermeture auto
  document.querySelectorAll(".toast").forEach((toast, i) => {
    const close = () => { toast.classList.add("out"); setTimeout(() => toast.remove(), 400); };
    toast.querySelector(".toast-close").addEventListener("click", close);
    setTimeout(close, 4200 + i * 400);
  });

  // Afficher / masquer le mot de passe
  document.querySelectorAll(".pw-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.parentElement.querySelector("input");
      input.type = input.type === "password" ? "text" : "password";
    });
  });

  // Nom du fichier choisi pour l'import YAML
  document.querySelectorAll(".drop input[type=file]").forEach((input) => {
    input.addEventListener("change", () => {
      const label = input.parentElement;
      if (input.files.length) {
        label.classList.add("has-file");
        label.querySelector("span").textContent = "📄 " + input.files[0].name;
      }
    });
  });
})();
