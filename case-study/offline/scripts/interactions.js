document.documentElement.classList.add("js");

document.querySelectorAll("[data-tabs]").forEach((group) => {
  const tabs = [...group.querySelectorAll('[role="tab"]')];
  const setPanelState = (tab, active) => {
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
    const panel = document.getElementById(tab.getAttribute("aria-controls"));
    if (panel) panel.hidden = !active;
  };
  const activate = (tab) => {
    tabs.forEach((item) => setPanelState(item, item === tab));
    tab.focus();
  };
  tabs.forEach((tab, index) => {
    setPanelState(tab, tab.getAttribute("aria-selected") === "true");
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
      event.preventDefault();
      const offset = event.key === "ArrowRight" ? 1 : -1;
      activate(tabs[(index + offset + tabs.length) % tabs.length]);
    });
  });
});
