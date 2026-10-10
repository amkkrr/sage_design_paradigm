/* Display-only demo. Fixed, invented data; no requests, collection or business writes. */
(() => {
  "use strict";
  const root = document.documentElement;
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  const forcedColors = window.matchMedia("(forced-colors: active)");
  const choices = {
    palette: ["sage", "ash-marble"],
    mode: ["auto", "light", "dark"],
    tone: ["pale", "gray"],
    material: ["marble", "flat"]
  };
  const defaults = { palette: "ash-marble", mode: "auto", tone: "pale", material: "marble" };
  const labels = { sage: "Sage", "ash-marble": "Ash Marble", auto: "自动", light: "浅色", dark: "深色", pale: "苍白", gray: "苍灰", marble: "石纹", flat: "纯色" };
  const key = dimension => "sage-ash-marble-demo:" + dimension;
  let storageAvailable = true;
  const state = {};
  for (const dimension of Object.keys(choices)) {
    let saved;
    try { saved = window.localStorage.getItem(key(dimension)); }
    catch { storageAvailable = false; }
    state[dimension] = choices[dimension].includes(saved) ? saved : defaults[dimension];
  }
  let ready = false;
  const resolveMode = () => state.mode === "auto" ? (systemTheme.matches ? "dark" : "light") : state.mode;
  function applyDisplay() {
    const resolved = resolveMode();
    root.dataset.palette = state.palette;
    root.dataset.themeMode = state.mode;
    root.dataset.resolvedTheme = resolved;
    root.dataset.ashTone = state.tone;
    root.dataset.ashMaterial = state.material;
    if (!ready) return;
    const activeAsh = state.palette === "ash-marble" && resolved === "light" && !forcedColors.matches;
    const focused = document.activeElement;
    const moveFocus = !activeAsh && focused && focused.matches("[data-tone-choice],[data-material-choice]");
    for (const dimension of ["palette", "tone", "material"]) {
      for (const button of document.querySelectorAll("[data-" + dimension + "-choice]")) {
        button.setAttribute("aria-pressed", String(button.dataset[dimension + "Choice"] === state[dimension]));
        button.disabled = dimension !== "palette" && !activeAsh;
      }
    }
    const modeButton = document.getElementById("theme-mode");
    modeButton.disabled = false;
    const next = choices.mode[(choices.mode.indexOf(state.mode) + 1) % choices.mode.length];
    modeButton.textContent = "主题：" + labels[state.mode];
    modeButton.setAttribute("aria-label", "主题模式：" + labels[state.mode] + "，当前" + labels[resolved] + "；切换为" + labels[next]);
    const detail = forcedColors.matches ? "强制颜色模式，浅色调和石纹停用" : activeAsh ? labels[state.tone] + " · " + labels[state.material] : (resolved === "dark" ? "沿用 Sage 深色，石纹禁用" : "原 Sage 浅色，石纹禁用");
    document.getElementById("display-status").textContent = labels[state.palette] + " · " + labels[state.mode] + "（" + labels[resolved] + "） · " + detail + (storageAvailable ? "" : " · 存储不可用，仅当前页面生效");
    // A system preference can disable the currently focused tone/material button.
    if (moveFocus) modeButton.focus({ preventScroll: true });
  }
  function select(dimension, value) {
    if (!choices[dimension].includes(value)) return;
    state[dimension] = value;
    try {
      if (dimension === "mode" && value === "auto") window.localStorage.removeItem(key(dimension));
      else window.localStorage.setItem(key(dimension), value);
    } catch { storageAvailable = false; }
    applyDisplay();
  }
  // Synchronous initial resolution, before CSS: avoid a wrong initial theme.
  applyDisplay();
  systemTheme.addEventListener("change", () => { if (state.mode === "auto") applyDisplay(); });
  forcedColors.addEventListener("change", applyDisplay);

  const sample = {
    current: [14000, 17000, 18000, 16000, 20000, 21000, 22430],
    prior: [12000, 15000, 16000, 14000, 18000, 19000, 20000],
    currentDates: ["2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07"],
    priorDates: ["2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30"],
    inputTokens: 8420000,
    outputTokens: 2170000,
    successes: 127402,
    categories: [
      { id: "code", label: "代码生成", count: 54711, color: "s1" },
      { id: "analysis", label: "数据分析", count: 36346, color: "s2" },
      { id: "docs", label: "文档处理", count: 23631, color: "s3" },
      { id: "other", label: "其他", count: 13742, color: "other" }
    ]
  };
  const total = sample.current.reduce((a, b) => a + b, 0);
  const priorTotal = sample.prior.reduce((a, b) => a + b, 0);
  const integer = new Intl.NumberFormat("en-US");
  const percent = value => value.toFixed(1) + "%";
  const text = (id, value) => { document.getElementById(id).textContent = value; };
  function element(tag, value, className) {
    const node = document.createElement(tag);
    if (value !== undefined) node.textContent = value;
    if (className) node.className = className;
    return node;
  }
  function metricWithUnit(id, value, unit) {
    const target = document.getElementById(id);
    target.textContent = value;
    target.append(element("span", " " + unit, "units"));
  }
  function renderSample() {
    text("total-calls", integer.format(total));
    text("change-calls", "↑ " + percent((total / priorTotal - 1) * 100) + " 较上期；变化方向不表示好坏");
    metricWithUnit("input-tokens", (sample.inputTokens / 1000000).toFixed(2), "M");
    metricWithUnit("output-tokens", (sample.outputTokens / 1000000).toFixed(2), "M");
    metricWithUnit("success-rate", (sample.successes / total * 100).toFixed(1), "%");
    text("input-exact", integer.format(sample.inputTokens));
    text("output-exact", integer.format(sample.outputTokens));
    text("success-exact", integer.format(sample.successes));
    text("completed-exact", integer.format(total));
    text("trend-current-total", integer.format(total));
    text("trend-prior-total", integer.format(priorTotal));
    text("distribution-total", integer.format(total));

    const ceiling = 25000;
    for (let i = 0; i < sample.current.length; i++) {
      const column = element("div", undefined, "column");
      for (const period of ["prior", "current"]) {
        const bar = element("div", undefined, "bar " + period);
        bar.style.setProperty("--h", (sample[period][i] / ceiling * 100) + "%");
        column.append(bar);
      }
      document.getElementById("trend-bars").append(column);
      document.getElementById("trend-dates").append(element("span", sample.currentDates[i].slice(5)));
      const row = element("tr");
      const date = element("th", sample.currentDates[i]);
      date.scope = "row";
      row.append(date, element("td", sample.priorDates[i]), element("td", integer.format(sample.current[i]), "numeric"), element("td", integer.format(sample.prior[i]), "numeric"));
      document.getElementById("trend-rows").append(row);
    }
    for (const category of sample.categories) {
      const share = category.count / total * 100;
      const group = element("div");
      group.dataset.categoryId = category.id;
      const header = element("div", undefined, "dist-head");
      header.append(element("span", category.label), element("span", percent(share)));
      const track = element("div", undefined, "track");
      const fill = element("div", undefined, "fill");
      fill.style.setProperty("--value", share + "%");
      fill.style.setProperty("--series", "var(--" + category.color + ")");
      track.setAttribute("aria-hidden", "true");
      track.append(fill);
      group.append(header, track);
      document.getElementById("distribution-bars").append(group);
      const row = element("tr");
      const label = element("th", category.label);
      label.scope = "row";
      row.append(label, element("td", integer.format(category.count), "numeric"), element("td", percent(share), "numeric"));
      document.getElementById("distribution-rows").append(row);
    }
  }
  document.addEventListener("DOMContentLoaded", () => {
    renderSample();
    ready = true;
    for (const dimension of ["palette", "tone", "material"]) {
      for (const button of document.querySelectorAll("[data-" + dimension + "-choice]")) {
        button.addEventListener("click", () => {
          if (!button.disabled) select(dimension, button.dataset[dimension + "Choice"]);
        });
      }
    }
    document.getElementById("theme-mode").addEventListener("click", () => {
      select("mode", choices.mode[(choices.mode.indexOf(state.mode) + 1) % choices.mode.length]);
    });
    applyDisplay();
  });
})();
