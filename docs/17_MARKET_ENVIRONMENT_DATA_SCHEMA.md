# Phase 4B 市场环境数据字段规范

## 1. 本阶段目标

本阶段只定义市场环境数据字段，不接入真实 API，不生成真实数据。

## 2. 覆盖范围

第一阶段只覆盖：

* QQQ
* 纳斯达克指数
* 比特币
* VIX

暂不覆盖：

* 个股
* 公司财报
* SEC 文件
* 政府合同
* X / KOL 数据
* 自动交易数据

## 3. 市场资金数据字段

字段必须包括：

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

字段说明：

* symbol：资产代码或资产标识。
* asset_name：资产中文名称。
* asset_type：资产类型，例如 ETF、指数、加密资产。
* current_price：当前价格字段。字段存在不代表已经接入真实行情。
* ma_20：20日均线。
* ma_50：50日均线。
* ma_20_direction：20日均线方向，例如 向上 / 向下 / 走平 / 数据不足。
* ma_50_direction：50日均线方向，例如 向上 / 向下 / 走平 / 数据不足。
* volume：成交量。
* relative_volume：相对成交量。
* above_ma20：是否站上 20日均线。
* above_ma50：是否站上 50日均线。
* stronger_than_benchmark：是否强于基准。
* risk_appetite_spread：是否出现风险偏好扩散。
* source_name：数据来源名称。
* source_type：数据来源类型。
* data_status：数据状态。
* updated_at：数据更新时间。

特别规则：
市场资金监控只允许使用 20日均线、50日均线。
不得使用 20日涨跌幅、50日涨跌幅。

## 4. 市场情绪数据字段

字段必须包括：

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

字段说明：

* indicator_id：情绪指标 ID。
* indicator_name：情绪指标名称。
* indicator_type：情绪指标类型。
* current_value：当前指标值字段。字段存在不代表已经接入真实数据。
* current_status：当前状态，例如 低风险 / 中性 / 高风险 / 数据不足。
* risk_meaning：风险含义说明。
* direction：变化方向，例如 上升 / 下降 / 走平 / 数据不足。
* source_name：数据来源名称。
* source_type：数据来源类型。
* data_status：数据状态。
* updated_at：数据更新时间。

第一阶段只覆盖：

* VIX

Put / Call 和 X 社交情绪留到后续阶段。

## 5. data_status 规则

允许状态：

* 待配置
* 数据不足
* 待人工确认
* 已验证

规则：

* 刚接入的数据不能直接标记为已验证。
* 首次接入后必须先标记为待人工确认。
* 字段缺失时必须标记为数据不足。
* 无法计算均线时必须标记为数据不足。
* 不得用假数据补齐缺失字段。

## 6. 错误处理规则

必须覆盖：

* 数据源不可用
* 网络失败
* 返回空数据
* 字段缺失
* 日期异常
* 数值异常
* 价格为 0
* 均线无法计算
* 成交量缺失
* VIX 数据源不可用

错误时必须显示：
数据不足

不得显示假数据。

## 7. 安全边界

* 市场环境数据不产生个股推荐。
* 市场环境数据不产生买入建议。
* 市场环境数据不产生卖出建议。
* 市场环境数据不产生目标价。
* 市场环境结论不是交易指令。
* 本系统不自动交易。
* 本系统不自动下单。

## 8. 下一阶段

Phase 4C：创建本地 mock 市场环境数据结构，状态：未开始
