(() => {
  const links = [...document.querySelectorAll(".chapter-nav a[href^='#']")];
  const sections = links
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);
  if (!("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      links.forEach((link) => {
        const active = link.getAttribute("href") === `#${visible.target.id}`;
        link.setAttribute("aria-current", String(active));
      });
    },
    { rootMargin: "-20% 0px -65%", threshold: [0.1, 0.4, 0.7] },
  );
  sections.forEach((section) => observer.observe(section));
})();
