document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.body.classList.add("js-ready");
  requestAnimationFrame(function () {
    document.body.classList.add("page-ready");
  });

  const motionSelectors = [
    ".page-shell > *",
    ".section-head > *",
    ".choice",
    ".service-row",
    ".process-step",
    ".retainer-row",
    ".price-band",
    ".proof-table tr",
    ".form-stack > *",
    ".summary-rail > *",
    ".list-item",
    ".callout > *",
    ".footer-grid > *",
    ".about-grid > *",
    ".about-services > *",
    ".legal-copy > *"
  ];

  const motionItems = [];
  motionSelectors.forEach(function (selector) {
    document.querySelectorAll(selector).forEach(function (el, index) {
      if (!el.classList.contains("motion-item")) {
        el.classList.add("motion-item");
        el.style.setProperty("--motion-order", String(index % 8));
        motionItems.push(el);
      }
    });
  });

  if (!reduced && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -6% 0px" });

    motionItems.forEach(function (el) { observer.observe(el); });
    document.querySelectorAll(".reveal").forEach(function (el) { observer.observe(el); });
  } else {
    motionItems.forEach(function (el) { el.classList.add("is-visible"); });
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-visible"); });
  }

  document.querySelectorAll(".route-list li").forEach(function (item, index) {
    item.style.setProperty("--route-order", String(index));
  });

  document.querySelectorAll("[data-dismiss-message]").forEach(function (el) {
    window.setTimeout(function () {
      el.classList.add("message-leave");
      window.setTimeout(function () { el.remove(); }, 260);
    }, 5000);
  });
});
