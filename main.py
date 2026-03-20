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
    """调用 Gemini AI 翻译，并详细记录错误"""
    api_key = os.getenv("GEMINI_API_KEY")
    # 检查钥匙是否成功拿到
    if not api_key:
        print("❌ 错误：在 GitHub Secrets 中没有找到 GEMINI_API_KEY！")
        return text

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"Translate this news title to Chinese, return only the result: {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        # 如果返回码不是 200 (成功)，打印出原因
        if response.status_code != 200:
            print(f"⚠️ 翻译请求失败，状态码：{response.status_code}")
            print(f"响应详情：{response.text}")
            return text
            
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"❌ 发生网络或代码错误: {e}")
        return text

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
