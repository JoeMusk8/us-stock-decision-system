# 数据状态与证据工具函数说明

本文件说明 Phase 3D 新增的本地工具函数。
当前阶段没有接入真实数据，没有调用外部网络，也没有生成真实公司结论。

## 1. data_status 工具函数用途

`core/data_status.py` 用于统一处理 `data_status`。

包含：

* `VALID_DATA_STATUSES`
* `is_valid_data_status(status)`
* `normalize_data_status(status)`
* `is_data_usable_for_fact(status)`
* `get_data_status_label(status)`

允许的数据状态为：

* 待配置
* 示例数据
* 数据不足
* 已验证
* 待人工确认

## 2. evidence_utils 工具函数用途

`core/evidence_utils.py` 用于检查 evidence record 和 Claim 是否满足进入事实区的最低规则。

包含：

* `VALID_EVIDENCE_LEVELS`
* `has_evidence_id(record)`
* `is_valid_evidence_level(level)`
* `is_social_or_kol_clue(record)`
* `can_enter_fact_zone(record)`
* `validate_evidence_record(record)`
* `claim_can_enter_fact_zone(claim)`

## 3. 为什么只有“已验证”数据能进入事实区

事实区必须保存可追溯、可复查、已完成核验的数据。

`待配置`、`示例数据`、`数据不足`、`待人工确认` 都不能证明数据已经完成来源核验和人工确认，因此不能进入事实区。

## 4. 为什么 KOL / 社交媒体只能作为线索

KOL / 社交媒体信息噪声高、传播快、上下文不稳定，不能直接证明公司事实、财务事实、订单事实或宏观事实。

因此，`source_type=social_kol_clue` 或 `clue_only=true` 的记录只能作为线索，必须返回不能进入事实区。

## 5. 为什么没有 evidence_id 的 Claim 不能进入事实区

没有 `evidence_id` 的 Claim 无法追溯来源，无法核验，无法复查，也无法判断是事实、推断、假设还是待验证内容。

因此，Claim 必须同时满足：

* 有 `evidence_id`
* `claim_label=事实`
* `support_status=已证实`

否则不能进入事实区。

## 6. 当前阶段限制

* 不接 API。
* 不调用外部网络。
* 不生成真实行情数据。
* 不生成真实财务数据。
* 不生成真实宏观数据。
* 不生成真实公司结论。
* 不修改 UI。
* 不输出投资建议或交易建议。
* 不自动交易，不自动下单。
