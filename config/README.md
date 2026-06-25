# 数据源配置说明

`config/data_sources.example.json` 是数据源配置示例。

当前没有真实数据源。
当前没有 API 接入。
未来真实 API Key 不得提交到代码仓库。
所有数据接入必须遵守 `docs/05_NO_HALLUCINATION_RULES.md`。

重要规则：

* 示例配置中的所有数据源默认 `enabled=false`。
* 示例配置中的所有数据源默认 `data_status=待配置`。
* 示例配置不得写入真实 API Key、真实 token 或真实账号凭据。
* 社交媒体 / KOL 数据只能作为线索，不能直接作为事实结论。
* 事实性结论必须绑定 `evidence_id`。
