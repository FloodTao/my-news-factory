import os
import requests
import feedparser  # <--- 这是别人的成熟代码零件
from datetime import datetime

# 订阅源 (Sources)
FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Nature": "https://www.nature.com/nature.rss"
}

def translate_by_ai(text):
    """调用 Gemini 翻译官"""
    key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    prompt = f"请将以下标题翻译成中文：\n{text}"
    
    try:
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=data, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return text

def run_factory():
    items = []
    for name, url in FEEDS.items():
        # 这里使用了别人的成熟代码零件，它能自动处理所有抓取细节
        feed = feedparser.parse(url)
        
        # 遍历前 3 条信息
        for entry in feed.entries[:3]:
            cn_title = translate_by_ai(entry.title)
            items.append(f"<li>[{name}] <a href='{entry.link}'>{cn_title}</a></li>")

    # 生成网页
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"<html><body><ul>{''.join(items)}</ul></body></html>")

if __name__ == "__main__":
    run_factory()
