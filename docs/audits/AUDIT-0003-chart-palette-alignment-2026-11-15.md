# AUDIT-0003：Ash Marble 双灰色调柱状条及关联配色对齐审查

**被审计范围**：[ash-marble.json](../../tokens/ash-marble.json)、[ash-marble.css](../../examples/ash-marble.css)、[ash-marble-demo.css](../../examples/ash-marble-demo.css)、[ash-marble-demo.html](../../examples/ash-marble-demo.html)、[ASH_MARBLE.md](../ASH_MARBLE.md)、[validate_ash_marble.py](../../scripts/validate_ash_marble.py)、[test_ash_marble_browser.py](../../tests/test_ash_marble_browser.py)

**关联前序审计**：[AUDIT-0001](AUDIT-0001-ash-marble-2026-10-09.md)、[AUDIT-0002](AUDIT-0002-modern-web-guidance-2026-11-13.md)

**审查与实施日期**：2026-11-15

## 1. 结论与边界

**PASS：完成 `pale`（苍白）与 `gray`（苍灰）双色调下柱状条、分类横条轨道、连续／热力色阶及强制颜色回退的视觉对齐与门禁固化，保持 v1.0.0 核心 `tokens/design-tokens.json` 基线不变。**

- 苍白与苍灰两档的 `--s1..5` 与 `--other` 在卡片纯底（`surface-1`）、保守石纹叠底及横条轨道（`surface-2`）上的非文本对比度均达到 **≥ 3.0:1**（苍白最低 `3.062:1`，苍灰最低 `3.398:1`）。
- 趋势图“上期 vs 本期”由原先四边细碎低对比虚线改为“退底描边柱（1px 实线高对比描边）vs 主色实心柱”（内部与描边／两期填充亮度比均 ≥ 3.0:1），并在 `@media (forced-colors: active)` 下回退为 `Canvas` 虚线框与 `Highlight` 实心条，兼顾浅深双主题语义准确性、低装饰统一感与非颜色可辨识性。
- 补齐 Ash Marble 专属 `--seq-0..7`（矿物蓝）与 `--heat-0..7`（矿物灰青）8 档单调递减色阶，消除原基线 `#b8c2ab` 鼠尾草绿零档与高饱和皇家蓝在冷灰石材界面上的串色隐患。

## 2. 发现与修正闭环

| 编号 | 原问题 | 修正方案 | 验证门禁 |
|---|---|---|---|
| C-3.1 | `pale` 与 `gray` 共用同一套数据色，`gray` 下 `other` 对轨道仅 `1.62:1`、`s5` 仅 `2.33:1`、`priorPeriod` 对卡片仅 `1.78:1`，尾端边界发虚；`s5`（`#8196A5`）与 `other` 同处 `203°–205°` 蓝灰轴易混淆 | 在 `ash-marble.json` 新增 `dataColors.byTone.{pale,gray}` 并在 `ash-marble.css`（含无脚本 `prefers-color-scheme: light` 兜底）按色调分档覆盖；重构冷石材协调序列（矿物蓝 `s1`、灰青 `s2`、石板靛 `s3`、风化褐 `s4`、赤铁灰紫 `s5`、冷锡灰 `other`） | `validate_ash_marble.py` 校验全部 6 个槽位对 `surface-1`、石纹保守底及 `surface-2` 均 `≥ 3.0:1`；Playwright 遍历 48 状态核对计算色 |
| C-3.2 | `pale` 下横条底槽 `surface-2`（`#EDF0F1`）对卡片 `#F9FAFB` 对比仅 `1.10:1`，`100%` 分母槽几近隐形 | 将 `pale.surface-2` 微调为 `#E4E9EC`（对卡片 `1.17:1`，与 `gray` 的 `1.17:1` 一致；`ink-2` 对其对比度仍达 `5.07:1`） | 门禁校验双色调 `contrast(surface-2, surface-1) ≥ 1.15` 且控件正文 `≥ 4.5:1` |
| C-3.3 | 上期柱 `#A9B9C2` 蓝度偏高且四边 `1px dashed` 细碎毛躁（描边对填充仅 `1.86:1`）；`forced-colors` 下分布横条与底槽无系统色边界 | 改为低彩度浅石底（`#D5DFE4` / `#C7D2D7`）配高对比 `1px solid` 石板描边（`#687780` / `#5D6B74`，对卡片 `4.43:1` / `4.86:1`）；`forced-colors: active` 下显式指定上期 `Canvas` + `dashed CanvasText`、本期 `Highlight`、横条 `.track` `1px solid CanvasText` + `.fill` `Highlight` | 门禁校验 `priorBorder` 对卡片与填充、`currentPeriod` 对上期填充均 `≥ 3.0:1`；Playwright 验证常规与 `forced-colors` 下边框／轮廓状态 |
| C-3.4 | 未覆盖 `--seq-*` / `--heat-*`，接入 `meter` 或热力组件时会暴露 `#b8c2ab` 鼠尾草绿和高饱和蓝 | 为 `pale` 与 `gray` 分别提供零档对齐 `surface-2` 的 8 档 `--seq-0..7` 与 `--heat-0..7` | 门禁校验 8 档长度、零档等于 `surface-2`、亮度严格单调递减，以及 `seq-5` 对卡片和 `seq-1` 均 `≥ 3.0:1` |
| C-3.5 | `.chart-scroll` 横向滚动容器触发纵向裁切，趋势图顶部 `25,000` 刻度上半截被截断 | 为 `.trend-visual` 补充 `padding-block-start: 0.5rem`，随根字号等比缩放且不改变 `.plot` 绘图区高度 | Playwright 校验首刻度 `top >= scroller.top` 及 150% `rem` 缩放下 `.plot` 高度不变 |

## 3. 验证记录

```bash
python3 scripts/validate_ash_marble.py .
ASH_MARBLE_CHROMIUM=/usr/bin/google-chrome python3 tests/test_ash_marble_browser.py
node --check examples/ash-marble-demo.js
git diff --check
```
