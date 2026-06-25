# UI 提示词索引

本文件用于保存项目 UI 图片生成提示词的索引。
所有 UI 图片提示词必须遵守本文件的全局规则。

## 全局 UI 风格

UI 风格参考 Gemini：

* 高级
* 简洁
* 优雅
* 大面积留白
* 浅灰背景
* 白色主卡片
* 圆角卡片
* 轻微阴影
* 淡蓝 / 淡紫渐变点缀
* 中文界面
* 桌面端 Web App
* 16:9 比例

## 禁止事项

* 不使用原始示意图中的蓝色、黄色、绿色大色块
* 不生成真实股票
* 不生成真实公司
* 不生成真实财务数据
* 不生成真实交易结论
* 不生成投资建议
* 不生成自动交易功能
* 不生成“立即买入”“立即卖出”“保证盈利”等内容

## UI 图片数量

1. 范式创新监控模块：7 张 UI 图片
2. 基础投研 / 产业链图谱 / 候选股雷达模块：6 张 UI 图片
3. 深度投研模块：11 张 UI 图片
4. 重点跟踪池 / 量化策略标注模块：10 张 UI 图片
5. 市场环境监控模块：6 张 UI 图片

## 文件说明

完整提示词分别保存在：

* docs/ui_prompts/01_paradigm_monitor_ui_prompt.md
* docs/ui_prompts/02_basic_research_ui_prompt.md
* docs/ui_prompts/03_deep_research_ui_prompt.md
* docs/ui_prompts/04_tracking_pool_ui_prompt.md
* docs/ui_prompts/05_market_monitor_ui_prompt.md

每个文件先写入：

* 模块名称
* 需要生成的 UI 图片数量
* 页面清单
* 全局风格引用
* 禁止事项
