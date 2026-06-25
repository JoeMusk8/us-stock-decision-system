# 美股交易决策系统

## 当前状态

* 本项目是 Streamlit Web App
* 当前入口文件是 app.py
* 当前已完成五个模块 UI
* 当前已完成市场环境模块 yfinance 读取逻辑
* 本地环境因为网络/代理问题可能无法安装 yfinance
* 建议通过 Streamlit Cloud 部署，由云端安装 requirements.txt

## 运行方式

本地运行：

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud 部署

部署入口文件：

```text
app.py
```

Python 依赖文件：

```text
requirements.txt
```

## 模块

1. 范式创新监控
2. 基础投研 / 产业链图谱 / 候选股雷达
3. 深度投研
4. 重点跟踪池 / 量化策略标注
5. 市场资金 / 情绪 / 宏观监控

## 数据说明

* 市场环境模块优先读取 QQQ、纳斯达克指数、比特币、VIX
* 数据状态默认待人工确认或数据不足
* 本项目不自动交易
* 本项目不自动下单
