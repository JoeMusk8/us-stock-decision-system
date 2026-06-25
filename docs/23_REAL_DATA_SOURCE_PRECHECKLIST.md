# Phase 5B 真实数据源接入前安全检查清单

## 1. 本阶段结论

本阶段只创建真实数据源接入前安全检查清单，不接 API，不调用外部网络，不生成真实行情数据。

下一阶段如果进入真实数据源配置，也必须先通过本清单。

## 2. 数据源基本检查

每个候选数据源接入前必须检查：

* 数据源名称
* 官方网站
* 数据覆盖范围
* 是否覆盖 QQQ
* 是否覆盖纳斯达克指数
* 是否覆盖比特币
* 是否覆盖 VIX
* 是否需要 API Key
* 是否收费
* 是否有频率限制
* 是否允许个人项目使用
* 是否允许缓存
* 是否允许展示到本地 UI
* 是否稳定
* 是否有字段文档

## 3. 安全检查

必须检查：

* API Key 不得写入代码
* API Key 不得写入 GitHub
* API Key 只能通过环境变量读取
* 不得提交 .env 文件
* 请求失败不得用假数据补齐
* 字段缺失必须显示“数据不足”
* 数据异常必须显示“数据不足”
* 首次接入数据必须标记为“待人工确认”
* 人工确认前不得标记为“已验证”

## 4. 字段映射检查

真实数据必须能映射到以下字段：

市场资金字段：

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

市场情绪字段：

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

## 5. 错误处理检查

必须覆盖：

* 网络失败
* 数据源不可用
* 返回空数据
* 字段缺失
* 日期异常
* 数值异常
* 价格为 0
* 均线无法计算
* 成交量缺失
* 比特币数据源异常
* VIX 数据源异常

所有错误场景必须显示：
数据不足

不得用假数据填充。

## 6. 输出边界检查

必须确认：

* 行情数据不能生成买入建议
* 行情数据不能生成卖出建议
* 行情数据不能生成目标价
* 行情数据不能生成保证盈利结论
* 市场环境结论不是交易指令
* 本系统不自动交易
* 本系统不自动下单
* 本模块不做个股推荐

## 7. 接入前人工确认清单

创建检查表：

* 数据源使用条款已确认
* API Key 安全方式已确认
* 字段覆盖已确认
* 频率限制已确认
* 错误处理已确认
* data_status 流程已确认
* 不输出交易建议已确认
* 不自动交易已确认
* 不自动下单已确认

## 8. Phase 5C 建议任务

Phase 5C：真实数据源配置文件草案，状态：未开始
