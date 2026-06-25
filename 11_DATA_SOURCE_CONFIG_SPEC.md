# 数据源配置文件规约

本文件说明 `config/data_sources.example.json` 的字段含义。
当前阶段只创建配置结构，不接入真实 API，不生成真实数据。

## 1. 顶层字段

* version：配置文件版本。
* stage：当前项目阶段。
* description：配置文件说明。
* rules：全局数据源规则。
* source_layers：数据源分层定义。
* sources：具体数据源占位配置。

## 2. rules 字段

* no_real_data：为 true 表示当前配置不得包含真实数据。
* no_api_connected：为 true 表示当前尚未接入 API。
* all_sources_disabled_by_default：为 true 表示所有数据源默认关闭。
* social_media_as_clue_only：为 true 表示社交媒体只能作为线索。
* evidence_id_required_for_facts：为 true 表示事实结论必须绑定证据。

## 3. source_layers 的 5 层定义

### 3.1 official_disclosure

官方披露数据。
用于公司公告、SEC 文件、财报、管理层披露和风险披露。
可信度较高，但仍需要人工确认解释关系。

### 3.2 market_data

市场行情数据。
用于 QQQ、纳斯达克指数、比特币、VIX、Put / Call 等市场环境数据规划。
不同供应商可能存在口径、延迟和授权差异。

### 3.3 macro_data

宏观数据。
用于核心利率、核心通胀、核心就业、核心GDP、原油等宏观环境数据规划。
宏观数据可能滞后或修正，不能直接生成交易结论。

### 3.4 news_contracts_government

新闻 / 公告 / 政府合同数据。
用于政府资金流向、政府合同、拨款、政策事件、公司公告和新风险线索。
政府合同和拨款不得被伪造成真实订单或确定收入。

### 3.5 social_kol_clues

社交媒体 / KOL 线索数据。
只能作为线索，不能直接作为事实结论。
必须人工确认后才可进入后续研究流程。

## 4. source_layers 字段定义

* layer_id：数据源层级 ID。
* layer_name：数据源层级中文名称。
* purpose：该层数据用途。
* credibility：数据可信度。
* requires_human_review：是否需要人工确认。
* risk_note：风险说明。

## 5. sources 字段定义

* source_id：数据源唯一 ID。
* source_name：数据源名称。
* source_type：数据源类型。
* layer_id：所属数据源层级。
* covered_modules：可能覆盖的模块。
* priority：数据源优先级，使用 P0 / P1 / P2 / P3。
* enabled：是否启用。
* auth_required：未来真实接入时是否可能需要鉴权。
* api_key_env：未来环境变量名称占位；当前必须为空字符串或 null。
* data_status：数据状态。
* refresh_frequency：刷新频率占位。
* requires_human_review：是否需要人工确认。
* evidence_id_required：是否要求事实结论绑定证据。
* clue_only：是否只能作为线索。
* notes：备注。

## 6. 关键字段规则

`enabled=false` 表示尚未启用。

`data_status=待配置` 表示还没有真实数据。

`clue_only=true` 表示只能作为线索。

`evidence_id_required=true` 表示事实结论必须绑定证据。

## 7. 禁止事项

* 不得在配置文件中写入真实 API Key。
* 不得在配置文件中写入真实 token。
* 不得把示例配置当作真实数据源。
* 不得通过配置文件绕过人工确认。
* 不得把 X / KOL / 社交媒体线索直接写成事实结论。
