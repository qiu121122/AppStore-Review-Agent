"""
App Store 真实玩家评论抓取模块
使用苹果官方 RSS 接口获取游戏评论数据
（使用 urllib 标准库，避免 requests 库在 Apple 接口上的兼容性问题）
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict


# ============================================================
# 配置：App ID 对照表（方便后续扩展其他游戏）
# ============================================================
APP_STORE_CONFIG = {
    "原神": 1517783697,
    "崩坏星穹铁道": 1606357176,
    "绝区零": 6479244777,
}

# RSS 接口 URL 模板
RSS_URL_TEMPLATE = (
    "https://itunes.apple.com/rss/customerreviews"
    "/page={page}/id={app_id}/sortby=mostrecent/json"
)


def fetch_app_reviews(
    app_id: int,
    page: int = 1,
    limit: int = 20,
    timeout: int = 30,
) -> List[Dict[str, str]]:
    """
    从 App Store RSS 接口抓取指定游戏的玩家评论。

    参数:
        app_id   : App Store 应用 ID
        page     : 评论页码（默认第 1 页）
        limit    : 最大返回条数（默认 20）
        timeout  : 请求超时时间（秒）

    返回:
        [
            {
                "review_id": "14126696822",
                "content"  : "Difficult system to earn the heros...",
                "rating"   : "1",
                "title"    : "Criticism",
                "author"   : "Zeta flower",
                "date"     : "2026-05-31T03:04:33-07:00",
            },
            ...
        ]
    """
    url = RSS_URL_TEMPLATE.format(page=page, app_id=app_id)

    print(f"🌐 正在请求 App Store RSS 接口...")
    print(f"   URL: {url}")

    # 关键：必须带上浏览器 UA，否则 Apple 可能返回空数据
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.URLError as e:
        print(f"❌ 网络请求失败: {e}")
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"❌ 数据解析失败: {e}")
        return []

    # 提取 entry 列表（每条 entry 即一条评论）
    entries: List[dict] = data.get("feed", {}).get("entry", [])

    if not entries:
        print("⚠️  未获取到任何评论数据，请检查 app_id 或页码是否正确。")
        return []

    reviews: List[Dict[str, str]] = []
    for entry in entries:
        try:
            review = {
                "review_id": entry.get("id", {}).get("label", ""),
                "content": entry.get("content", {}).get("label", ""),
                "rating": entry.get("im:rating", {}).get("label", ""),
                "title": entry.get("title", {}).get("label", ""),
                "author": entry.get("author", {}).get("name", {}).get("label", ""),
                "date": entry.get("updated", {}).get("label", ""),
            }
            reviews.append(review)
        except Exception:
            # 单条解析异常，跳过继续
            continue

    # 截取指定条数
    reviews = reviews[:limit]

    print(f"✅ 成功抓取 {len(reviews)} 条评论")
    return reviews


def fetch_genshin_reviews(limit: int = 20) -> List[Dict[str, str]]:
    """
    快捷函数：抓取《原神》最新评论。
    优先请求实时 RSS 接口；若 Apple 频率限制导致空返回，
    则自动降级为本地缓存的真实评论数据。
    """
    app_id = APP_STORE_CONFIG["原神"]
    reviews = fetch_app_reviews(app_id=app_id, limit=limit)

    if reviews:
        # 实时抓取成功，顺便更新本地缓存
        _save_cache(reviews)
        return reviews

    # 实时抓取失败，启用本地缓存兜底
    print("⚠️  实时 RSS 接口暂时不可用（频率限制），启用本地评论缓存。")
    cached = _load_cache(limit)
    if cached:
        print(f"✅ 从本地缓存加载 {len(cached)} 条真实评论")
    return cached


# ============================================================
# 本地缓存：应对 Apple RSS 频率限制
# ============================================================
import os as _os

_CACHE_PATH = "review_cache.json"


def _save_cache(reviews: List[Dict[str, str]]) -> None:
    """将抓取到的评论保存为本地缓存。"""
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 缓存写入失败不影响主流程


def _load_cache(limit: int) -> List[Dict[str, str]]:
    """从本地缓存加载评论数据。"""
    if not _os.path.exists(_CACHE_PATH):
        print("❌ 本地缓存文件不存在，无法兜底。")
        return []
    try:
        with open(_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[:limit]
    except Exception as e:
        print(f"❌ 缓存读取失败: {e}")
        return []


# ============================================================
# 独立测试入口
# ============================================================
if __name__ == "__main__":
    reviews = fetch_genshin_reviews(limit=5)
    for i, r in enumerate(reviews, 1):
        print(f"\n--- 评论 {i} ---")
        print(f"  ID    : {r['review_id']}")
        print(f"  评分  : {r['rating']} / 5")
        print(f"  作者  : {r['author']}")
        print(f"  标题  : {r['title']}")
        print(f"  内容  : {r['content'][:80]}...")
