# 数据结构规约

本文件是项目数据结构的唯一事实源。后续实现数据库前必须读取本文件。

重要规则：

1. 第一版允许使用示例数据，但必须标记为“示例数据”。
2. 不得用示例数据冒充真实数据。
3. 数据不足时必须显示“数据不足”。
4. AI草稿不能当作事实。
5. 所有事实、Claim、结论必须预留 evidence_id。
6. 没有 evidence_id 的 Claim 不能进入事实区。

## 1. evidence_items

用途：
全系统证据库，保存所有模块引用的证据。

字段：

* id
* evidence_id
* source_type
* source_name
* title
* summary
* url
* related_module
* related_ticker
* related_theme
* evidence_level
* data_status
* created_at
* updated_at

说明：
evidence_level 可为 A/B/C/D。
X/KOL 信息只能作为线索，不得直接作为事实。

## 2. paradigm_items

用途：
保存范式创新监控模块的信息流。

字段：

* id
* source_type
* title
* summary
* ai_label
* source_confidence
* truth_check_status
* impact_industries
* human_status
* evidence_id
* data_status
* created_at

说明：
用于范式创新初筛，不用于直接选股或交易。

## 3. industries

用途：
保存基础投研中用户输入的行业。

字段：

* id
* industry_name
* status
* data_status
* created_at
* updated_at

说明：
最多支持 3 个当前分析行业。

## 4. industry_nodes

用途：
保存产业链图谱节点。

字段：

* id
* industry_id
* layer_name
* node_name
* core_level
* score
* evidence_status
* evidence_id
* data_status
* created_at

说明：
layer_name 必须属于 6 层产业链：
上游资源 / 原材料、核心零部件、关键设备、系统集成、基础设施建设、下游应用 / 客户。

## 5. candidate_stocks

用途：
保存基础投研输出的候选股雷达结果。

字段：

* id
* industry_id
* ticker
* stock_name
* related_node
* score
* evidence_status
* evidence_id
* human_status
* data_status
* created_at

说明：
候选股最多 5 只。
候选股不是买入信号，只代表进入深度投研候选。

## 6. research_tasks

用途：
保存深度投研任务。

字段：

* id
* ticker
* stock_name
* theme
* source
* status
* evidence_count
* claim_count
* research_level
* data_status
* created_at
* updated_at

说明：
深度投研必须绑定“股票 + 主题”。
最多支持手动填写 15 只股票。

## 7. claims

用途：
保存深度投研中的 Claim 验证。

字段：

* id
* research_task_id
* claim_text
* claim_label
* support_status
* evidence_id
* human_status
* data_status
* created_at

说明：
claim_label 可为：事实、推断、假设、待验证。
support_status 可为：已证实、部分支持、证据不足、被反证。
没有 evidence_id 的 Claim 不能进入事实区。

## 8. tracking_items

用途：
保存重点跟踪池中的高质量标的。

字段：

* id
* ticker
* stock_name
* theme
* tracking_level
* research_level
* tracking_status
* freshness_status
* quant_status
* buy_price
* take_profit_price
* stop_loss_price
* data_status
* created_at
* updated_at

说明：
买入价格、止盈价格、止损价格只是策略标注字段，不是交易指令。
系统不自动交易，不自动下单。

## 9. tracking_variables

用途：
保存重点跟踪池的核心变量。

字段：

* id
* tracking_item_id
* variable_type
* variable_name
* current_status
* change_direction
* last_updated
* need_review
* evidence_id
* data_status
* created_at

说明：
variable_type 包括：
主题变量、公司变量、财务变量、催化剂变量、风险变量、数据新鲜度变量。

## 10. market_indicators

用途：
保存市场环境监控模块的指标。

字段：

* id
* category
* indicator_name
* asset_name
* current_value
* ma20
* ma50
* ma20_direction
* ma50_direction
* volume
* relative_volume
* status
* data_status
* updated_at

说明：
市场资金监控必须使用 20日均线、50日均线。
禁止使用 20日涨跌幅、50日涨跌幅。

## 11. review_tasks

用途：
保存复查任务。

字段：

* id
* ticker
* reason
* source
* priority
* status
* related_module
* created_at
* updated_at

说明：
新证据、新风险、数据过期、财报更新、主题退潮、策略标注失效都可以触发复查任务。

## 通用字段说明

data_status 可为：

* 示例数据
* 待配置
* 数据不足
* 已验证

created_at：
创建时间。

updated_at：
更新时间。

evidence_id：
证据编号，用于连接 evidence_items。
