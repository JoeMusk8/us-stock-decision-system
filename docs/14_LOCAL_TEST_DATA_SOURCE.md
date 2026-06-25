# Phase 3E 本地测试数据源

## 1. 说明

* 本阶段只读取本地示例文件。
* 本阶段没有接入真实 API。
* 本阶段没有真实行情、真实财务、真实宏观数据。
* `data/evidence_items.example.json` 只是示例结构。
* 示例数据不能进入事实区。
* 只有 `data_status=已验证` 且有 `evidence_id` 且非 KOL / 社交媒体线索的数据，才可以进入事实区。
* 当前阶段用于测试数据读取和证据校验流程。

## 2. 本地读取范围

当前唯一允许读取的测试数据源：

* `data/evidence_items.example.json`

本阶段不读取真实 URL，不调用外部网络，不接入任何真实行情、财务或宏观数据源。

## 3. 工具函数

`core/local_data_loader.py` 提供：

* `load_json_file(file_path)`
* `load_evidence_items(file_path="data/evidence_items.example.json")`
* `validate_loaded_evidence(records)`
* `get_fact_allowed_records(records)`

## 4. 事实区规则

示例数据不能进入事实区。

KOL / 社交媒体线索不能进入事实区。

缺少 `evidence_id` 的记录不能进入事实区。

`data_status` 不是 `已验证` 的记录不能进入事实区。

## 5. 当前阶段限制

* 不接 API。
* 不调用外部网络。
* 不生成真实行情数据。
* 不生成真实财务数据。
* 不生成真实宏观数据。
* 不生成真实公司结论。
* 不写真实公司名、真实股票代码或真实 URL。
* 不修改 UI。
* 不输出投资建议或交易建议。
* 不自动交易，不自动下单。
