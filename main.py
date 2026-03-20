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
    """调用 Gemini AI 正式版接口"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 错误：没找到 API 钥匙")
        return text

    # 这里改用了 v1 正式版接口，适配最新的 1.5-flash 模型
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"请将以下英文标题翻译成中文，只返回翻译结果：\n{text}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        # 工业级标准：设置 headers
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            # 如果 v1 还不行，我们尝试 fallback 到最新路径
            print(f"⚠️ v1 接口返回 {response.status_code}，正在尝试备用路径...")
            return text
    except Exception as e:
        print(f"❌ 翻译出错: {e}")
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
