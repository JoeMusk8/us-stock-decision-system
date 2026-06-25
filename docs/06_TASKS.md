# 任务阶段

Phase 0：项目初始化，状态：已完成
Phase 1：项目规约文件，状态：已完成
Phase 2A：正式 Streamlit 项目代码骨架，状态：已完成
Phase 2B：五个正式 UI 模块，状态：已完成
Phase 2C：全局验收并冻结当前 UI 版本，状态：已完成

Phase 3：数据源规划，状态：已完成
Phase 3A：数据源规划，状态：已完成
Phase 3B：数据源配置文件结构，状态：已完成
Phase 3C：创建 evidence_items 本地数据结构，状态：已完成
Phase 3D：创建数据状态与证据状态工具函数，状态：已完成
Phase 3E：只接入一个低风险测试数据源，状态：已完成
Phase 3F：全局数据源验收，状态：已完成

Phase 4：数据源接入，状态：已完成
Phase 4A：第一个真实低风险数据源接入规划，状态：已完成
Phase 4B：市场环境数据字段规范，状态：已完成
Phase 4C：创建本地 mock 市场环境数据结构，状态：已完成
Phase 4D：创建市场环境数据读取与校验函数，状态：已完成
Phase 4E：只在本地 mock 数据上联通 UI，状态：已完成
Phase 4F：本地 mock UI 验收，状态：已完成

Phase 5：测试与部署，状态：进行中
Phase 5A：真实外部数据源接入方案选择，状态：已完成
Phase 5B：真实数据源接入前安全检查清单，状态：已完成
Phase 5C：真实数据源配置文件草案，状态：已完成
Phase 5D：真实数据源字段映射函数草案，状态：已完成
Phase 5E-1：真实数据源只读接入骨架，状态：已完成
Phase 5E-2A：真实数据启用开关与运行边界，状态：已完成
Phase 5E-2B：真实数据客户端运行时安全闸门，状态：已完成
Phase 5E-2C：手动启用一个真实低风险数据源，状态：未开始
Phase 5E-Market-Minimal：市场环境真实行情最小闭环，状态：已完成

UI-REFINE-1：全局 UI 重构，状态：已完成

DEPLOY-1：GitHub / Streamlit Cloud 部署准备，状态：已完成
DEPLOY-2：上传 GitHub，状态：已完成
DEPLOY-3：Streamlit Cloud 部署，状态：已完成
DEPLOY-4：Streamlit Cloud 云端验收，状态：进行中

DEPLOY-4 验收项：

* 云端 App 可以打开
* app.py 位于仓库根目录
* requirements.txt 位于仓库根目录
* 云端可以安装 streamlit / pandas / plotly / yfinance
* 市场环境模块可以访问
* 市场资金监控页可以展示 QQQ / ^IXIC / BTC-USD
* 市场情绪监控页可以展示 ^VIX
* 如果真实行情拉取失败，页面显示“数据不足”
* 首次真实行情 data_status 默认为“待人工确认”
* 不输出投资建议
* 不自动交易
* 不自动下单

PHASE-6A：市场环境真实行情结论规则化，状态：已完成
PHASE-7A：重点跟踪池 / 量化策略标注 MVP，状态：已完成
PHASE-7B：深度投研模块可用化 MVP，状态：已完成
PHASE-7C：深度投研 → 重点跟踪池联动闭环，状态：已完成
PHASE-7D：基础投研 / 候选股雷达 → 深度投研联动闭环，状态：已完成
PHASE-7E：范式创新监控 → 基础投研联动闭环，状态：已完成
PHASE-7F：清理 UI 重复提示文案，状态：已完成
PHASE-8A：全局工作区 JSON 导出 / 导入，状态：已完成
