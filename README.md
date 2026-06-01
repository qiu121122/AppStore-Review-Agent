# 🎮 App Store Review Sentiment Analysis Pipeline

> 基于大模型 API 的 App Store 真实玩家评论抓取 → AI 情感打标 → 商业报表导出，一站式自动化流水线。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek--Chat-536DFE.svg)](https://platform.deepseek.com/)
[![Pandas](https://img.shields.io/badge/Export-Pandas%20%2B%20Excel-brightgreen.svg)](https://pandas.pydata.org/)

---

## 📖 项目简介

对于游戏运营团队而言，App Store 用户评论是宝贵的舆情金矿。但面对海量多语种评论，人工逐一标注情感不仅低效，而且难以规模化。

本项目提供了一条**端到端的自动化情感分析流水线**：

1. 🕸️ **自动抓取** App Store 任意游戏的官方 RSS 评论数据
2. 🤖 **调用 DeepSeek 大模型** 对每条评论进行情感二分类（正面 / 负面）
3. 📊 **使用 Pandas 导出** 结构化 Excel 业务报告，包含评分与情感的交叉分析

以一个命令即可将原始玩家反馈转化为可量化的商业洞察，帮助团队快速识别用户情绪趋势、定位版本口碑危机。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔄 **实时 RSS 抓取** | 基于苹果官方公开 RSS 接口，无需爬虫、无需登录，合法合规 |
| 🛡️ **容灾缓存兜底** | 当 Apple 接口触发频率限制时，自动降级为本地缓存，**流水线永不中断** |
| 🧠 **大模型自动化打标** | 基于 DeepSeek-Chat，配合精细化 System Prompt，严格输出「正面 / 负面」 |
| 📈 **商业 Excel 报表** | 使用 Pandas + openpyxl 导出 `.xlsx`，包含评分档位 × AI 情感交叉分析 |
| 🌍 **多语种覆盖** | 不限制评论语言，大模型可处理中英日韩俄等多语种反馈 |
| 🔌 **易于扩展** | App ID 配置表已预留 3 款游戏，换游戏只需改一行 |

### 容灾机制亮点

```
实时 RSS 请求
    ├── 成功 → 提取评论 → 同时刷新本地缓存 review_cache.json
    └── 失败 → 自动读取本地缓存 → 流水线继续执行（零中断）
```

> 这是生产环境级别的工程设计：**外部依赖不可靠时，系统优雅降级而非崩溃**。

---

## 🏗️ 工作流架构

```
┌─────────────────────────────────────────────────────────┐
│                   🚀 一体化流水线                         │
├──────────────┬──────────────┬──────────────┬─────────────┤
│  ① RSS 抓取  │  ② 缓存兜底   │  ③ AI 打标   │ ④ Excel 导出 │
│              │              │              │             │
│  App Store   │  review_     │  DeepSeek    │  Pandas     │
│  官方 RSS    │  cache.json  │  API         │  DataFrame  │
│  ───────────►│  ───────────►│  ───────────►│  ───────────►│
│              │              │              │             │
│  50 条/页    │  实时抓取失败  │  System      │  情感分析    │
│  多语种评论   │  自动降级读取  │  Prompt:     │  业务报告    │
│              │  本地缓存     │  只输出正/负面 │  .xlsx      │
└──────────────┴──────────────┴──────────────┴─────────────┘
```

### 项目文件结构

```
.
├── fetch_reviews.py          # 数据抓取层：App Store RSS → 结构化评论
├── auto_label.py             # AI 打标 + 导出层：全流水线编排
├── .gitignore                # 忽略虚拟环境、缓存、报表
├── README.md                 # 本文件
│
├── review_cache.json         # [运行时生成] 本地评论缓存（已 gitignore）
├── result.json               # [运行时生成] AI 打标原始结果
└── 情感分析业务报告.xlsx      # [运行时生成] 商业 Excel 报表
```

---

## 🚀 快速开始

### 前置要求

- Python 3.9+
- [DeepSeek API Key](https://platform.deepseek.com/api_keys)（免费注册即送额度）

### 1. Clone 项目

```bash
git clone <your-repo-url>
cd 01_API_Batch_Label
```

### 2. 创建并激活虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install requests pandas openpyxl
```

### 4. 配置 API Key

打开 `auto_label.py`，将第 25 行的占位符替换为你的真实 Key：

```python
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 你的 DeepSeek API Key
```

> ⚠️ **安全提示**：请勿将含真实 API Key 的代码提交到公开仓库。建议使用环境变量：
> ```python
> import os
> API_KEY = os.getenv("DEEPSEEK_API_KEY")
> ```

### 5. 运行

```bash
python auto_label.py
```

### 6. 查看结果

运行完成后，当前目录将生成：

| 文件 | 说明 |
|------|------|
| `result.json` | 每条评论的 ID、原文、评分、作者、日期、AI 情感标签 |
| `情感分析业务报告.xlsx` | 含中文表头、评分档位、交叉分析表的 Excel 报表 |

终端还会实时打印每条评论的处理进度和最终的评分 × 情感交叉分析。

---

## 🔧 进阶用法

### 更换目标游戏

编辑 `auto_label.py` 第 19、90 行，或直接修改 `fetch_reviews.py` 中的 `APP_STORE_CONFIG`：

```python
APP_STORE_CONFIG = {
    "原神": 1517783697,
    "崩坏星穹铁道": 1606357176,
    "绝区零": 6479244777,
}
```

然后在 `auto_label.py` 的 `main()` 中调用对应函数，或直接在 `fetch_reviews.py` 中：

```python
from fetch_reviews import fetch_app_reviews

reviews = fetch_app_reviews(app_id=1606357176, limit=50)  # 抓取崩坏星穹铁道 50 条
```

### 调整抓取数量

修改 `auto_label.py` 第 19 行：

```python
REVIEW_LIMIT = 50  # 一次抓取 50 条
```

### 更换大模型

修改 `auto_label.py` 第 24-26 行，支持任意 OpenAI 兼容接口：

```python
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "sk-your-openai-key"
MODEL_NAME = "gpt-4o"
```

---

## 📊 示例输出

```
=======================================================
🚀 一体化流水线启动：抓取 → AI 打标 → Excel 报告
=======================================================
🌐 正在请求 App Store RSS 接口...
✅ 成功抓取 20 条评论

📋 评分分布: {'1': 15, '3': 1, '4': 2, '5': 2}

[1/20] 正在分析: Difficult system to earn the heros...
  → AppStore评分: 1/5  |  AI情感: 负面
[2/20] 正在分析: Pity system ahhh...
  → AppStore评分: 1/5  |  AI情感: 负面
...
✅ AI 打标完成！共处理 20 条反馈
✅ Excel 报告已生成: 情感分析业务报告.xlsx

📈 评分档位 × AI 情感 交叉表:
AI情感标签   正面  负面
评分档位
低分(1-2)     0   15
中性(3)       0    1
高分(4-5)     3    1
```

---

## 🛠️ 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 数据源 | App Store RSS (iTunes RSS Feed) | 苹果官方公开接口 |
| HTTP 请求 | `urllib.request` (标准库) | 避免 requests 库的兼容性问题 |
| AI 推理 | DeepSeek-Chat API | 成本极低，情感分类准确率高 |
| 数据处理 | Pandas | DataFrame 转换、交叉分析 |
| Excel 导出 | openpyxl | 支持中文、多列宽格式 |

---

## 📄 License

MIT License — 自由使用、修改、分发。

---

## 🤝 贡献

欢迎提 Issue 和 PR。如有任何问题或建议，请在 GitHub 上开 Issue 讨论。
