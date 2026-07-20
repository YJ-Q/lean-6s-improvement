const summary = window.SYNTHETIC_TEST_SUMMARY;

if (summary) {
  document.querySelectorAll("[data-bar-condition]").forEach((bar) => {
    const condition = bar.dataset.barCondition;
    const value = Number(summary.condition_scores[condition]);
    const max = 16;
    const percent = Math.max(0, Math.min(100, (value / max) * 100));
    bar.dataset.barValue = String(value);
    bar.dataset.barMax = String(max);
    bar.style.setProperty("--bar-percent", `${percent}%`);
    bar.setAttribute("aria-label", `${bar.dataset.barLabel}: ${value} / ${max}`);
    const valueNode = document.querySelector(`[data-score-value="${condition}"]`);
    if (valueNode) valueNode.textContent = `${value.toFixed(2)} / ${max}`;
  });
}
