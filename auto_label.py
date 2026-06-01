"""
游戏玩家客诉反馈 —— 批量情感打标脚本
使用 DeepSeek API 对玩家反馈进行情感分类（正面 / 负面）
"""

import json
import time
import requests
import pandas as pd

# 导入本地的 App Store 评论抓取模块
from fetch_reviews import fetch_genshin_reviews

# ============================================================
# 1. 数据源：从 App Store RSS 动态抓取真实玩家评论
# ============================================================
# 不再使用写死的假数据 —— 改为调用 fetch_reviews 模块
# 抓取《原神》前 20 条最新评论
REVIEW_LIMIT = 20  # 可调节抓取条数

# ============================================================
# 2. API 配置
# ============================================================
API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = "sk-3843242ce0ae436e88185306e1fe1496"  # ⚠️ 请替换为你的真实 API Key
MODEL_NAME = "deepseek-chat"

# 系统提示词：严格限定 AI 只输出"正面"或"负面"
SYSTEM_PROMPT = (
    "你是一个数据清洗专家。你的任务是对游戏玩家的反馈进行情感分析。"
    "请严格只输出两个字：正面 或 负面。"
    "不要包含任何解释、标点、换行或其他额外信息。"
)


# ============================================================
# 3. 单条调用函数
# ============================================================
def analyze_sentiment(feedback_text: str) -> str:
    """
    调用 DeepSeek API 对单条反馈进行情感分析。

    参数:
        feedback_text: 玩家原始反馈文本

    返回:
        "正面" 或 "负面"
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": feedback_text},
        ],
        "temperature": 0.0,  # 设为 0 确保输出稳定、无随机性
        "max_tokens": 10,     # 只需返回两个字，token 数给到最小即可
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # 非 200 状态码自动抛异常

        data = response.json()
        # 提取模型回复，去除首尾空白
        sentiment = data["choices"][0]["message"]["content"].strip()
        return sentiment

    except requests.exceptions.RequestException as e:
        print(f"[网络错误] 请求失败: {e}")
        return "调用失败"
    except (KeyError, IndexError) as e:
        print(f"[解析错误] 返回数据结构异常: {e}")
        return "解析失败"


# ============================================================
# 4. 一体化流水线：抓取 → AI 打标 → 保存 JSON → 导出 Excel
# ============================================================
def main():
    # --- 第 0 步：从 App Store 抓取真实玩家评论 ---
    print("=" * 55)
    print("🚀 一体化流水线启动：抓取 → AI 打标 → Excel 报告")
    print("=" * 55)

    reviews = fetch_genshin_reviews(limit=REVIEW_LIMIT)

    if not reviews:
        print("❌ 未抓取到评论数据，流水线终止。")
        return

    # 统计评分分布
    rating_dist = {}
    for r in reviews:
        rating_dist[r["rating"]] = rating_dist.get(r["rating"], 0) + 1
    print(f"\n📋 评分分布: {dict(sorted(rating_dist.items()))}")

    # --- 第 1 步：AI 批量情感打标 ---
    results = []

    print(f"\n{'=' * 55}")
    print("开始批量 AI 情感分析...")
    print("=" * 55)

    for idx, review in enumerate(reviews, start=1):
        content_preview = review["content"][:40].replace("\n", " ")
        print(f"\n[{idx}/{len(reviews)}] 正在分析: {content_preview}...")

        sentiment = analyze_sentiment(review["content"])

        result_item = {
            "id": idx,
            "review_id": review["review_id"],       # App Store 原始 ID
            "玩家评论": review["content"],
            "评分": review["rating"],
            "作者": review["author"],
            "日期": review["date"],
            "AI情感标签": sentiment,
        }
        results.append(result_item)

        print(f"  → AppStore评分: {review['rating']}/5  |  AI情感: {sentiment}")

        # 礼貌性延时，避免触发 API 频率限制
        if idx < len(reviews):
            time.sleep(0.5)

    # --- 第 2 步：保存原始结果为 JSON ---
    output_path = "result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 55}")
    print(f"✅ AI 打标完成！结果已保存至: {output_path}")
    print(f"共处理 {len(results)} 条反馈")
    print("=" * 55)

    # --- 第 3 步：商业报告导出 JSON → DataFrame → Excel ---
    print("\n📊 正在生成 Excel 业务报告...")

    # 从 result.json 读取并转为 DataFrame
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # 列名美化为中文表头
    df.columns = [
        "序号", "AppStore评论ID", "玩家反馈原文",
        "AppStore评分", "评论作者", "评论日期", "AI情感标签",
    ]

    # 添加评分对照列（方便业务人员直观对比）
    # 1-2 星 = 低分，3 星 = 中性，4-5 星 = 高分
    df["评分档位"] = df["AppStore评分"].apply(
        lambda x: "低分(1-2)" if int(x) <= 2 else ("中性(3)" if int(x) == 3 else "高分(4-5)")
    )

    # 导出为 Excel 文件
    excel_path = "情感分析业务报告.xlsx"
    df.to_excel(excel_path, index=False, engine="openpyxl")

    print(f"✅ Excel 报告已生成: {excel_path}")
    print(f"   包含 {len(df)} 条记录")
    print(f"   AI 判为正面: {len(df[df['AI情感标签'] == '正面'])} 条")
    print(f"   AI 判为负面: {len(df[df['AI情感标签'] == '负面'])} 条")

    # 交叉分析：AI 标签 vs 用户评分
    cross = pd.crosstab(df["评分档位"], df["AI情感标签"])
    print(f"\n📈 评分档位 × AI 情感 交叉表:\n{cross.to_string()}")
    print("=" * 55)


if __name__ == "__main__":
    main()