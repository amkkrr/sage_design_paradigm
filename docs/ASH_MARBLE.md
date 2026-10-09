# Ash Marble · 苍白／苍灰可选主题

> 可选视觉扩展，版本 1.1.0。压缩包中的看板概念是视觉方向，**不是原 cc-usage-viewer / disk-usage 的已实现能力，也不是可直接运行的生产组件库**。原 Sage light / dark token 除版本号外全部原样保留。
>
> 基线：[DESIGN_PARADIGM.md](DESIGN_PARADIGM.md)；接入契约：[ADOPTION_TEMPLATE.md](ADOPTION_TEMPLATE.md)；来源边界：[EXTRACTION_NOTES.md](EXTRACTION_NOTES.md)；本次审查：[AUDIT-0001](audits/AUDIT-0001-ash-marble-2026-10-09.md)。

## 1. 视觉意图与不变约束

以冷灰白为背景，使用极低对比度、稀疏灰色石脉增加材质感。画布保持纯色；大卡片的纹理是装饰，不是信息层级。**每个指标区至多一个主要 KPI** 可用矿物蓝 `#345F78`；其余数字使用 `ink-1`。强调色、实体色和状态色仍是三个独立维度，不把增长染成“成功”。

苍白优先，苍灰为稍深的可选背景；图表用矿物蓝／灰青。不得复制概念稿中的营销句、大 banner、人物侧栏或固定卡片数量。数据优先、轻边框、无卡片投影、数字层级、状态范围与诚实的数据表达全部沿用基线。原规范的“核心／默认／可选／适配”分类不因增加材质而放宽。

## 2. 主题、色调和材质契约

| 维度 | 合法值 / 默认值 | 作用范围 |
|---|---|---|
| palette | `sage`（项目默认）/ `ash-marble` | 是否使用可选浅色 overlay；离线示例为演示而初始选择 Ash |
| mode | `auto`（默认）/ `light` / `dark` | 保持 `auto → light → dark → auto` 循环 |
| resolved mode | `light` / `dark` | 应用解析 mode 与系统偏好后设置 `data-resolved-theme` |
| tone | `pale`（默认）/ `gray` | 仅 Ash + 有效浅色生效；切回后保留选择 |
| material | `marble`（默认）/ `flat` | 仅 Ash + 有效浅色的大卡片生效；不影响色调、业务数据或分母 |

- 自动模式跟随系统变化；手动模式优先。存储 key 必须项目独立；回到自动模式删除显式 mode 覆盖。存储不可用不得阻断页面。
- 在样式加载前解析已有设置，避免错误的首帧主题。非法存储值回退到各维度默认值。
- 深色沿用原 Sage dark，**禁用石纹**，主 KPI 回到原 `ink-1`；不反色、不继承浅色矿物蓝或浅色图表颜色。
- Sage palette、深色或 forced-colors 下 tone / material 不生效；示例禁用相应按钮但保留选择，并在状态文字中说明。主题变化不重绘业务数据或改变图表轴、统计范围；通常保留焦点。如果系统变化导致当前 tone/material 按钮被禁用，将焦点移到主题按钮且不滚动页面。
- CSS recipe 只负责样式，不负责系统偏好、存储、状态机或业务组件。示例 JS 演示上述状态机，但不是目标应用的实现保证。

### 浅色板

| Token | Pale 苍白 | Gray 苍灰 | 用途 |
|---|---|---|---|
| page | `#F1F2F3` | `#E1E4E5` | 纯色画布 |
| surface-1 | `#F9FAFB` | `#F0F1F1` | 主卡片底色 |
| surface-2 | `#EDF0F1` | `#DCE1E2` | 次级控件底色 |
| ink-1 | `#313A41` | `#30383E` | 大多数数字与正文 |
| ink-2 | `#55636C` | `#505F68` | 次级文字 |
| ink-3 | `#646F76` | `#5A656D` | 辅助文字，须检查实际叠层 |
| hairline | `#D9DFE2` | `#CBD1D3` | 细描边 |
| accent-hero | `#345F78` | 同左 | 单个主要 KPI 的层级强调 |
| accent-secondary | `#376C67` | 同左 | 可选视觉身份，不是成功色 |

完整值见 [ash-marble.json](../tokens/ash-marble.json)，recipe 见 [ash-marble.css](../examples/ash-marble.css)。原 [design-tokens.json](../tokens/design-tokens.json) 是基线，新文件是普通 JSON **overlay**，不是 DTCG 或自动合并器。

接入时先提供基线 CSS 变量，再按有效模式加载 overlay。recipe 覆盖 `--page`、`--surface-*`、`--ink-*`、网格/轴/边框/hover/focus，以及基线命名的 `--s1..5` / `--other`；`--data-s1..5` / `--data-other` 是对应别名。`--data-prior-period` / `--data-current-period` 用于示例两期比较。其余状态色、seq、heat、几何、排版、层级和动效继承基线，**继承不代表已经适合所有新背景**，目标项目必须复测实际图形、状态文字和控件。

## 3. 纹理适用范围与对比度

- 可用：大型分析卡片、趋势面板、大型洞察或活动区。只对指定容器显式加 `ash-marble-card`。
- 禁用：画布、直接摆在画布上的 KPI、按钮、输入框、Seg、下拉、Tooltip、Dialog、小控件、表格单元。recipe 防护常见错误的 opt-in，不能替代容器语义审查。
- [ash-marble.svg](../assets/textures/ash-marble.svg) 为透明、可缩放的本地示例。`cover / no-repeat`；不要随机旋转多个版本或平铺整个页面。
- 伪元素在容器的 isolated stacking context 内使用 `z-index:-1` 位于内容底层、`pointer-events:none`、沿用圆角，不裁掉焦点或浮层，不重写子元素的 position/z-index。嵌套控件、summary、菜单、提示、dialog 和精确值表格必须有**不透明纯色底**；只写 `background-image:none` 不能阻止祖先石纹透出。
- 默认叠层透明度为 **0.12**。原包的 0.38 在苍白板的最强单条石脉上会把辅助文字对比度降到约 4.47:1；下调后用 SVG 所有线条完全重叠的保守上界校验。素材、颜色或透明度变化必须重新计算并做实际背景检查，不能随意提高透明度。
- 深色和 forced-colors 禁用纹理；flat 只关纹理、不改变色调。禁止黑石脉、强渐变、玻璃拟态、厚阴影、彩色侧条和小控件纹理。卡片仍为 radius8、1px hairline、无投影。

## 4. 几何、字体与组件

沿用 1240px 居中容器、默认 padding28/32/64、12 列、gap16、7/5 大卡片、card padding16/18/14、980/600 默认断点。示例是四格而非五格 KPI：`minmax(260px,1.15fr) repeat(3,minmax(0,1fr))`，不补空占位；≤980px 首格通栏、其余两列，卡片通栏；≤600px 卡片横向 padding14。52/600 主数字、24/600 次数字、17/600 页题、14/600 卡片题、原 Seg 和 Ghost Button 几何均保留。

英文／数字以 **Space Grotesk** 为首选，中文 **Noto Sans SC**，代码／路径按需使用 **Space Mono**。本仓库不打包、不下载字体，写字体名不代表已加载。项目自行合法获取并本地托管字体，验收实际加载和 fallback。示例明确仅用本机 fallback；所有可比较数字使用 `tabular-nums`，不把所有 KPI 强制改为等宽。

示例 Seg 用原生按钮 + `aria-pressed` 即时反馈，额外用中性下划线标记选中标签，避免只依赖轻边框或背景差异；保留原默认几何。共享滑动底板是基线的**可选渐进增强**，示例未实现，不宣称动效已验证。非必要动画不新增；reduced-motion 下取消过渡/动画。选中、禁用、焦点、图表精确值与强制颜色替代入口都必须可辨。

## 5. 接入与回退

```html
<html data-palette="ash-marble" data-resolved-theme="light" data-ash-tone="pale" data-ash-material="marble">
  <!-- 页面保持纯色；只给大型内容卡片加材质类。 -->
  <section class="ash-marble-card" aria-labelledby="trend-title">
    <h2 id="trend-title">Usage Trend</h2>
    <!-- 真实数据与可访问精确值入口由项目提供。 -->
  </section>
</html>
```

1. 先填写[项目适配契约](ADOPTION_TEMPLATE.md)，提供基线主题变量和组件。
2. 加载 overlay；按实际打包路径修正纹理 `url(...)`，依法加载字体。
3. 实现各维度状态和存储策略，明确有效模式；不要把两个 JSON 盲目合并为一个全局浅色主题。
4. 显式列出哪些大卡片 opt-in；检查其中的控件、精确值表格和焦点，不因装饰改动数据。
5. 回退为 `data-palette="sage"` 或移除 Ash 属性/class 和 overlay；基线无需迁移。仅切材质时选 flat。

## 6. 离线示例的数据和能力边界

[示例 HTML](../examples/ash-marble-demo.html)、[示例 CSS](../examples/ash-marble-demo.css)、[示例 JS](../examples/ash-marble-demo.js) 是本地、无构建依赖的演示，允许主题/材质切换和原生 details 精确值展开；不采集、不刷新、不提供写操作、URL 查询、异步请求、Tooltip、Dialog、分页或搜索。它们不是该范式所有可选业务组件的实现。

固定模拟样本：本期 2026-10-01—10-07，上期 2026-09-24—09-30；均为 UTC 自然日。模拟快照为 2026-10-08 00:00 UTC，不代表真实数据更新时间。

| 指标 | 模拟数据 / 公式 | 展示规则 |
|---|---|---|
| 已完成请求 | 本期日数列 `[14000,17000,18000,16000,20000,21000,22430]`，合计 128430；上期 `[12000,15000,16000,14000,18000,19000,20000]`，合计 114000 | 整数千分位；增长 `(128430/114000-1)*100 = 12.7%`（1位）；方向中性 |
| 输入 / 输出 token | 本期累计 8420000 / 2170000，和请求属于同一模拟范围 | M = 1000000；紧凑值 8.42M / 2.17M，另附精确整数 |
| 成功率 | 127402 成功 / 128430 已完成请求；失败 1028 | 99.2%（1位），分子/分母可见，不冒充完整性或健康认证 |
| 分类占比 | code 54711、analysis 36346、docs 23631、other 13742；互斥完整且总和 128430 | 分母固定为全部已完成请求，1位小数；实体 ID 固定映射 s1/s2/s3/other |

趋势为零基线、固定 25000 上限、七组本期/上期对应日；图例用虚/实边框及标签区分，不能仅依赖颜色。图表有名称、摘要及原生 details 中的精确表格；表头 scope、数值右对齐。图形和长表仅在自己的容器横滚，页面不整体溢出。样本无缺失/零分母；不得拿该固定样本覆盖目标项目的异常验收。脚本不可用时明确缺失，而非填零。

示例存储使用 `sage-ash-marble-demo:{palette,mode,tone,material}`；mode 回到 auto 删除其 key。tone/material 在非 Ash 浅色或 forced-colors 时禁用但保留；模式切换保留已展开的精确表格，失效控件的焦点按第 2 节回退。无字体下载、外部服务或动态 HTML 拼接。

## 7. 验证与接入验收

本仓库可运行的检查：

```bash
python3 scripts/validate_ash_marble.py .
# 可选开发检查：需已安装 Python playwright 与本地 Chromium；不属于应用运行依赖。
ASH_MARBLE_CHROMIUM=/usr/bin/google-chrome python3 tests/test_ash_marble_browser.py
node --check examples/ash-marble-demo.js
git diff --check
```

本次执行结果及完整 15 节覆盖矩阵见[审查记录](audits/AUDIT-0001-ash-marble-2026-10-09.md)。以下仍是**每个目标项目自己的验收项**，不能因示例通过而默认勾选：

- [ ] 基线 light/dark 的全部 token 未变；未选择 Ash 的旧组件不受影响。
- [ ] 所有 palette / auto/light/dark / pale/gray / flat/marble 组合和回退；存储失效、非法值、首帧及系统偏好变化。
- [ ] 每个文本、状态、非文本控件、图表颜色在真实背景与石纹上的对比度，颜色不是唯一编码。
- [ ] 1440/980/600/390/320px、文本放大、长标签、表格局部横滚；无被裁的焦点和弹层。
- [ ] 实际字体文件加载、许可与 fallback；不能用字体栈声明替代验证。
- [ ] 键盘操作、焦点保留、ARIA 名称/状态、reduced-motion、forced-colors、触摸入口。
- [ ] 真实指标口径、时间/时区、零/缺失/异常、实体颜色稳定、分母、聚合/排序/分页和异步竞态。
- [ ] 按采用组件完成 Tooltip/Dialog/复制/通知/搜索/日期等基线要求；未采用模块明确写 N/A，不伪装成已实现。
- [ ] 记录读屏和跨浏览器实测范围，不将 Chromium 示例检查、token 对比度或规范声明当作 WCAG 认证。

未完成：实际字体加载、概念图像素级复刻、生产应用集成、Firefox/WebKit 实测、读屏与触摸设备实测、全组件可访问性认证。这些需要目标项目独立完成。
