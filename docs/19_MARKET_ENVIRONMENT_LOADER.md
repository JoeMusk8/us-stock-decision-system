# Phase 4D 市场环境数据读取与校验函数

## 1. 说明

* 本阶段只读取本地 mock 数据。
* 本阶段没有接入真实 API。
* 本阶段没有真实行情数据。
* mock 数据不能进入真实市场结论。
* 只有 `data_status=已验证` 的数据才允许进入市场环境结论。
* 当前 mock 数据 `data_status=示例数据`，因此不能进入真实市场结论。
* 市场环境结论不是交易指令。
* 本系统不自动交易，不自动下单。
* 市场资金字段只允许 20日均线、50日均线。
* 禁止使用 20日与50日的涨跌幅。

## 2. 新增函数

`core/market_environment_loader.py` 提供：

* `load_market_environment_mock(file_path="data/market_environment_mock.example.json")`
* `validate_market_fund_record(record)`
* `validate_market_sentiment_record(record)`
* `validate_market_environment_data(data)`
* `can_enter_market_conclusion(record)`

## 3. 读取边界

当前只读取：

* `data/market_environment_mock.example.json`

不接 API，不调用外部网络，不读取真实行情源。

## 4. 结论闸门

`can_enter_market_conclusion(record)` 只允许 `data_status=已验证` 的记录进入市场环境结论。

以下状态必须返回不能进入：

* 示例数据
* 待配置
* 数据不足
* 待人工确认

## 5. 安全边界

* 不输出投资建议。
* 不输出交易建议。
* 不自动交易。
* 不自动下单。
* 不生成真实行情数据。
* 不生成真实宏观数据。
