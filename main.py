import os
import feedparser
from google import genai # 注意：这是最新的引入方式
from datetime import datetime

# 订阅源
FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Nature": "https://www.nature.com/nature.rss"
}

def translate_text(text):
    """使用 2026 最新版 google-genai 客户端"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return text

    # 初始化新一代客户端
    client = genai.Client(api_key=api_key)
    
    try:
        # 新版 SDK 会自动处理版本和路径，极其稳健
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"请将这段英文标题翻译成中文，只返回翻译结果：\n{text}"
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ 最新零件反馈报错: {e}")
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
