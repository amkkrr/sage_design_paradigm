# Sage Design Paradigm

面向数据密集型工具的通用设计范式：**鼠尾草绿画布、墨绿文字、数字优先、紧凑布局、中性控件、诚实的数据表达**。

从 `cc-usage-viewer` 与 `disk-usage` 的设计文档中提取共同语言，去除业务绑定，并将差异保留为可选模式。适用于统计看板、资源分析、运维工具、用量报告与只读快照浏览器；不是面向所有产品类型的万能 UI 规范。

## 文档入口

| 文件 | 用途 |
|---|---|
| [DESIGN_PARADIGM.md](docs/DESIGN_PARADIGM.md) | 核心规范、组件、交互、数据契约、响应式与验收要求 |
| [design-tokens.json](tokens/design-tokens.json) | 框架无关的主题、排版、几何与动效默认值 |
| [Ash Marble 可选主题](docs/ASH_MARBLE.md) | 苍白／苍灰配色、石纹适用范围、矿物蓝 KPI 强调 |
| [ash-marble.json](tokens/ash-marble.json) | 可选配色及材质 Token overlay |
| [Ash Marble CSS 示例](examples/ash-marble.css) | 接入项目时可移植的 CSS recipe 与纹理素材 |
| [Ash Marble 离线预览](examples/ash-marble-demo.html) | 固定演示数据、双主题／配色／材质切换及精确值表格 |
| [Ash Marble 审查记录](docs/audits/AUDIT-0001-ash-marble-2026-10-09.md) | 对照全部 15 节范式的发现、修正、验证证据与未测边界 |
| [ADOPTION_TEMPLATE.md](docs/ADOPTION_TEMPLATE.md) | 接入新项目时填写的业务与实现契约 |
| [EXTRACTION_NOTES.md](docs/EXTRACTION_NOTES.md) | 来源、提取方法、差异取舍与验证边界 |

## 使用方法

1. 阅读通用范式，先确定信息层级与数据口径，再选择组件。
2. 将适配模板复制到目标项目，填写指标、分母、筛选范围、刷新方式、状态持久化及验收矩阵。
3. 将 JSON token 映射为 CSS 变量或所用框架的主题配置；它是普通 JSON，**不是 DTCG 格式或可直接运行的组件库**。
4. 在目标项目实现组件和交互，并完成实际浏览器、键盘及主题验证。
5. 将目标项目的例外写入本地设计文档，不用业务规则反向污染通用核心。

### 给 Agent 的使用提示

```text
遵循 docs/DESIGN_PARADIGM.md 与 tokens/design-tokens.json 的 Sage 设计语言。
先填写 docs/ADOPTION_TEMPLATE.md 所列的数据和交互契约。
保留数字优先、中性控件、双主题、轻边框和清晰统计口径。
按业务选择可选组件，不照搬来源项目的卡片数量、分页大小、指标公式或路径。
明确区分规范要求、已实现行为和未验证能力；不得把本仓库当成已完成的 UI 实现。
```

## 可选主题：Ash Marble（1.1）

默认 Sage green light / dark 保持不变。若项目需要更冷、更苍白的灰白界面，可按 [Ash Marble](docs/ASH_MARBLE.md) 使用 `pale`（苍白）或 `gray`（苍灰）浅色调；大卡片可按需叠加低对比大理石纹理，按钮和输入框始终无纹理。单个主要 KPI 可用矿物蓝强化层级，不能把强调色当作成功／异常状态。字体仍以 Space Grotesk + Noto Sans SC 为准，仓库不分发字体文件。

[离线示例](examples/ash-marble-demo.html) 演示 Sage/Ash 配色、自动/浅色/深色、两种浅色调和纹理切换；附精确值表格与明确的模拟数据口径。示例不加载字体文件，使用本机 fallback；不代表来源应用已实现该主题。命令行验证方法和实测边界见[扩展规范](docs/ASH_MARBLE.md#7-验证与接入验收)。

## 范围

本仓库交付**规范、配置参考与独立演示源码**，不包含生产应用、通用组件库、字体二进制、实时数据、原始快照或来源项目的完整文档副本。没有新增前端框架、图表库或构建依赖；字体接入时由项目自行检查许可并本地托管。静态验证仅需 Python 标准库；可选无头浏览器测试需要开发环境已有的 Python Playwright 与 Chromium，不属于应用运行依赖。

通用版本：`1.1.0`（新增可选主题，1.0.0 核心值不变）。提取基线及内容指纹见[来源说明](docs/EXTRACTION_NOTES.md)。
