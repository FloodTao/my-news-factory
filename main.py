import os
import feedparser
import google.generativeai as genai # 引入官方原厂零件
from datetime import datetime

# 1. 订阅源
FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Nature": "https://www.nature.com/nature.rss"
}

def translate_text(text):
    """使用 Google 官方 SDK 进行翻译"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return text

    # 配置原厂驱动
    genai.configure(api_key=api_key)
    # 使用目前最稳定的 1.5-flash 模型
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # 官方标准的调用方式
        response = model.generate_content(f"请将这段英文标题翻译成中文，只返回翻译结果：\n{text}")
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ 官方零件反馈：{e}")
        return text

def start_process():
    items_html = ""
    for name, url in FEEDS.items():
        feed = feedparser.parse(url)
        print(f"正在处理: {name}")
        for entry in feed.entries[:3]:
            translated = translate_text(entry.title)
            items_html += f"<li>[{name}] <a href='{entry.link}'>{translated}</a></li>"

    html_template = f"<html><meta charset='utf-8'><body><h1>全球前沿快讯</h1><ul>{items_html}</ul></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    start_process()
