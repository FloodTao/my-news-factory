import os
import requests
import feedparser  # 调用成熟的 RSS 专家零件
from datetime import datetime

# 1. 订阅源配置 (Sources Configuration)
# 你可以在这里增加任何你感兴趣的一手英文站
FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Nature": "https://www.nature.com/nature.rss",
    "Reuters": "https://rsshub.app/reuters/world"
}

def translate_text(text):
    """调用 Gemini AI 翻译 (AI Translation)"""
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # 工业级 Prompt（提示词）：要求 AI 保持简洁
    prompt = f"Translate this news title to Chinese, return only the result: {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # 设置 15 秒超时保护，防止程序死锁
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return text # 失败则返回原文 (Fallback to original)

def start_process():
    items_html = ""
    for name, url in FEEDS.items():
        # 使用 feedparser 解析。它是成熟的代码，能处理复杂的 XML 结构
        feed = feedparser.parse(url)
        print(f"Processing: {name}")
        
        # 只取前 3 条最热的新闻
        for entry in feed.entries[:3]:
            translated_title = translate_text(entry.title)
            items_html += f"<li>[{name}] <a href='{entry.link}'>{translated_title}</a></li>"

    # 生成最终的 HTML 页面
    html_template = f"<html><meta charset='utf-8'><body><h1>今日全球资讯</h1><ul>{items_html}</ul></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    start_process()
