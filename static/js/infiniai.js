(() => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector("#site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }
  document.querySelectorAll(".message").forEach((node, index) => {
    window.setTimeout(() => {
      node.style.opacity = "0";
      node.style.transform = "translateY(-6px)";
      window.setTimeout(() => node.remove(), 320);
    }, 5200 + index * 500);
  });
  const intake = document.querySelector("[data-intake]");
  if (intake) {
    const required = [...intake.querySelectorAll("[required]")];
    intake.addEventListener("submit", (event) => {
      const firstInvalid = required.find((field) => !field.value.trim());
      if (firstInvalid) { event.preventDefault(); firstInvalid.focus(); }
    });
  }
})();