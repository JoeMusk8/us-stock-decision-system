# Phase 5E-2B 真实数据客户端运行时安全闸门

## 1. 本阶段说明

本阶段只把 `runtime_flags` 接入真实数据源客户端。

本阶段没有接入真实 API。

本阶段没有调用外部网络。

本阶段没有拉取真实行情。

## 2. 运行时闸门

* `allow_external_network=false` 时必须禁止联网。
* `allow_real_market_data=false` 时必须禁止真实行情。
* `allow_real_data_to_ui=false` 时真实数据不得进入 UI。
* `allow_auto_verified_status=false` 时真实数据不得自动标记为“已验证”。

## 3. 当前配置状态

`selected_source` 仍然为 `null`。

所有候选源仍然 `enabled=false`。

运行时安全开关不能绕过真实数据源配置草案中的禁用状态。

## 4. 安全边界

市场环境结论不是交易指令。

本系统不自动交易，不自动下单。

本模块不做个股推荐。

当前阶段不会返回真实行情 records，不会生成真实市场环境结论。
