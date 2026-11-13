# AUDIT-0002：对照 Modern Web Guidance 的现代 Web 平台能力升级

**被审计范围**：[ash-marble-demo.html](../../examples/ash-marble-demo.html)、[ash-marble-demo.css](../../examples/ash-marble-demo.css)、[ash-marble.css](../../examples/ash-marble.css)、[ash-marble-demo.js](../../examples/ash-marble-demo.js)、[DESIGN_PARADIGM.md](../DESIGN_PARADIGM.md)、[ASH_MARBLE.md](../ASH_MARBLE.md)

**关联前序审计**：[AUDIT-0001](AUDIT-0001-ash-marble-2026-10-09.md)

**审计与实施日期**：2026-11-13

## 1. 结论与边界

**PASS：完成全部 5 类现代 Web 平台改进项与跨浏览器回退策略，且保持 v1.0.0 核心 token 基线不变。**

- `modern-web-guidance` 的 `legacy-scan`（覆盖约 20% 确定性静态规则库，33 篇指南 / 35 条规则）扫描结果为 **0 项旧版违规**。
- 人工对照其余 ~80% 指南库识别出的 5 类架构与可访问性改进项已全部落地并验证。
- `tokens/design-tokens.json` 仍与提交 `8fd7d2de97d508cc030be289ea33d92cc7835645` 除版本号外完全一致。本记录不构成全浏览器/真实设备/读屏软件的 WCAG 认证。

## 2. 改进项与回退闭环

| 编号 | 领域与指南 ID | 实施内容 | 浏览器兼容与回退策略 |
|---|---|---|---|
| M-1 | 相对排版与系统字号缩放（`typography`、`respect-os-text-scale`、`visually-stable-mixed-fonts`、`improve-text-layout-and-legibility`） | 全站字号与趋势图高度改为 `rem`（不覆盖 `:root`/`html` 字号），`<head>` 增加 `<meta name="text-scale" content="scale">`；字体栈启用 `font-size-adjust: from-font`；短标题启用 `text-wrap: balance`，段落与表题启用 `text-wrap: pretty`；视口断点改用 `em`。 | `<meta name="text-scale">` 在不支持浏览器中自然回退至 16px 默认根字号；`font-size-adjust` 配 `@supports not (font-size-adjust: from-font)` 行高兜底；`text-wrap` 为纯渐进增强。 |
| M-2 | 原生双色方案、无脚本深浅色与多标签同步（`dark-mode`、`dark-mode-toggle`） | `<head>` 声明 `<meta name="color-scheme" content="light dark">`，移除 `<html>` 硬编码的 `data-resolved-theme="light"`，`:root` 保持 `color-scheme: light dark`；Sage 基础色接入 `light-dark()`，JS 同步 `<meta>` 并在 `storage` 事件中跨标签页同步。 | 保留 `@media (prefers-color-scheme: dark)` 与 `@media (prefers-color-scheme: light)` 完整 CSS 变量兜底，确保不支持 `light-dark()` 的浏览器及禁用脚本（No-JS）场景下均能跟随系统深浅色。 |
| M-3 | 复合工具栏、触控目标与吸顶焦点保护（`toolbar`、`form-factor-adaptation`、`state-aware-sticky-headers`、`accessibility`） | `.filters` 升级为 `role="toolbar" focusgroup="toolbar wrap"` 单 Tab 停靠点，组间使用边框绘制 `role="separator"`（兼容 `forced-colors`）；不生效的色调/材质按钮在脚本启用后改用 `aria-disabled="true"` 保持方向键可达与原位焦点；`pointer: coarse` 下目标最小尺寸由 `24px` 提升至 `44px`；`:hover` 限定于 `@media (hover: hover)`；`html` 设置 `scroll-padding-top: 4.5rem`，吸顶栏启用 `scroll-state(stuck: top)` 底边提示。 | 无脚本初始态保留原生 `disabled`；不支持原生 `focusgroup` 的浏览器自动启用漫游 `tabindex` + `ArrowLeft/Right`（含 RTL 翻转）+ `Home/End` 回退；不支持 `scroll-state` 时保持基础 `position: sticky`。 |
| M-4 | CSS 级联层、逻辑属性与容器查询（`css`、`css-layout`、`size-aware-styling`、`card`） | 移除 `*` 全局重置，建立 `@layer base, theme, components, utilities;`；方向相关边距/边框/对齐改为逻辑属性，`.metric:not(:first-child)` 替代覆盖清零；卡片根节点改为 `<article>`，启用命名 `@container`（`dashboard`、`card`、`data-table`）及 `@scope` 嵌套平面背景防护。 | 为不支持容器查询的旧浏览器保留 `@supports not (container-type: inline-size)` 的 `em` 视口断点回退；同时保留后代 `:is(...)` 选择器兼容无 `@scope` 环境。 |
| M-5 | 粘性表头与横向可滚动边缘提示（`responsive-table`、`scrollability-affordance-hints`） | 明细表改用 `border-collapse: separate; border-spacing: 0`，`thead` 与 `tbody th` 配置不透明 `position: sticky`；滚动区通过 `aria-labelledby` 关联可见 `<caption>`，并基于 `@property` + `mask` + `animation-timeline: scroll(self inline)` 提供不遮挡焦点环的横向渐变提示。 | 不支持 `animation-timeline: scroll()` 的浏览器自动启用零净宽哨兵节点的 `IntersectionObserver`（`.more-start` / `.more-end`）回退；`prefers-reduced-motion: reduce` 下关闭滚动动画。 |

## 3. 验证记录

```bash
pnpx modern-web-guidance@latest legacy-scan /opt/sage_design_paradigm --json
python3 scripts/validate_ash_marble.py .
ASH_MARBLE_CHROMIUM=/usr/bin/google-chrome python3 tests/test_ash_marble_browser.py
node --check examples/ash-marble-demo.js
git diff --check
```

- `legacy-scan`：`totalFindings: 0`。
- `validate_ash_marble.py`：v1.0.0 token 基线一致性、全部颜色与石纹对比度上界（苍白最低 `4.508:1`、苍灰最低 `4.845:1`）、`@layer` 声明、零 `px` 字号、零 `*` 全局重置、`<meta>` 与 `toolbar` 属性、Markdown 链接与锚点全部通过。
- `test_ash_marble_browser.py`（Chromium `156.0.8078.79`）：全部 6 组测试通过，覆盖 48 种主题状态 × 5 种视口宽度（240 种布局）、无脚本浅色/深色系统跟随、150% 根字号 `rem` 缩放、200% 整页/文本放大、粗指针 `44px` 触控目标、跨标签 `storage` 同步，以及原生与模拟禁用 `focusGroup` / `animation-timeline` 的回退路径。
