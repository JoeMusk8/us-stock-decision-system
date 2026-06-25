# Phase 5A 真实外部数据源接入方案选择

## 1. 本阶段结论

本阶段只做真实外部数据源接入方案选择，不接 API，不调用外部网络，不生成真实行情数据。

第一阶段真实数据源仍然只服务于：

市场资金 / 情绪 / 宏观监控模块

优先覆盖：

* QQQ
* 纳斯达克指数
* 比特币
* VIX

暂不覆盖：

* 个股推荐
* 公司财报
* SEC 文件
* 政府合同
* X / KOL 数据
* 自动交易
* 自动下单

## 2. 候选数据源清单

本阶段只是列出候选，不确认可用性，不接入，不联网验证。
所有候选源在真实接入前都必须再次人工验证可用性、使用条款、频率限制、字段覆盖和稳定性。

| candidate_id | candidate_name | possible_coverage | auth_required | possible_cost | stability_risk | legal_or_terms_risk | data_quality_risk | implementation_difficulty | recommended_priority | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_001 | yfinance / Yahoo Finance 相关数据源 | QQQ、纳斯达克指数、VIX、部分加密资产 | 可能不需要 | 可能免费 | 中 | 中 | 中 | 低 | P1 | 只作为候选，真实接入前必须人工验证可用性和使用条款。 |
| candidate_002 | Stooq 等公开行情数据源 | ETF、指数、部分市场行情 | 可能不需要 | 可能免费 | 中 | 中 | 中 | 低到中 | P2 | 覆盖范围和字段稳定性需要接入前验证。 |
| candidate_003 | Alpha Vantage 等需要 API Key 的数据源 | ETF、指数、部分数字资产或指标 | 需要 | 可能免费或付费 | 中 | 中 | 中 | 中 | P1 | 需要 API Key，但不得提交真实 key 或 token。 |
| candidate_004 | Polygon / Nasdaq Data Link 等专业数据源 | ETF、指数、行情、部分市场指标 | 需要 | 可能付费 | 低到中 | 中 | 低到中 | 中到高 | P2 | 稳定性可能较好，但成本和授权条款必须人工确认。 |
| candidate_005 | 加密货币专用数据源 | 比特币 | 可能需要 | 可能免费或付费 | 中 | 中 | 中 | 中 | P2 | 需要处理股票数据源与加密资产数据源口径不一致问题。 |
| candidate_006 | CBOE / FRED / 官方宏观或市场指标数据源 | VIX、宏观或市场指标 | 可能需要 | 可能免费或付费 | 低到中 | 中 | 低到中 | 中 | P1 | VIX 和宏观指标优先考虑官方或权威来源，但接入前必须验证条款。 |

## 3. 第一阶段建议方案

第一阶段优先选择“市场环境基础行情数据源”，只验证：

* QQQ
* 纳斯达克指数
* 比特币
* VIX

不得直接接入个股财报、SEC、政府合同、X/KOL。

第一阶段目标不是获取最完整数据，而是验证真实外部数据接入流程是否安全可控。

## 4. 字段映射要求

未来真实数据必须映射到 `docs/17_MARKET_ENVIRONMENT_DATA_SCHEMA.md` 中定义的字段。

市场资金字段包括：

* symbol
* asset_name
* asset_type
* current_price
* ma_20
* ma_50
* ma_20_direction
* ma_50_direction
* volume
* relative_volume
* above_ma20
* above_ma50
* stronger_than_benchmark
* risk_appetite_spread
* source_name
* source_type
* data_status
* updated_at

市场情绪字段包括：

* indicator_id
* indicator_name
* indicator_type
* current_value
* current_status
* risk_meaning
* direction
* source_name
* source_type
* data_status
* updated_at

特别规则：
市场资金监控只允许使用 20日均线、50日均线。
禁止使用 20日与50日的涨跌幅。

## 5. 数据状态流程

真实数据接入后，不得直接进入“已验证”。

流程必须是：

1. 拉取数据
2. 字段映射
3. 字段完整性检查
4. 异常值检查
5. 标记为“待人工确认”
6. 人工确认后，才允许变成“已验证”

错误或缺失时必须显示：

数据不足

不得用假数据填充。

## 6. 安全边界

* 行情数据不能直接生成买入建议。
* 行情数据不能直接生成卖出建议。
* 行情数据不能生成目标价。
* 行情数据不能生成保证盈利结论。
* 市场环境结论不是交易指令。
* 本系统不自动交易。
* 本系统不自动下单。
* 本模块不做个股推荐。

## 7. Phase 5B 建议任务

Phase 5B：真实数据源接入前安全检查清单
Phase 5C：真实数据源配置文件草案
Phase 5D：真实数据源字段映射函数草案
Phase 5E：只读模式接入一个真实低风险数据源
Phase 5F：真实数据源接入验收
