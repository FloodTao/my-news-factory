import os
import feedparser
from google import genai
from datetime import datetime

# 订阅源
FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Nature": "https://www.nature.com/nature.rss"
}

def translate_text(text, client):
    """工业级翻译模块：强制锁定正式版，并使用最新模型"""
    try:
        # 升级为 gemini-2.0-flash
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=f"请将这段英文标题翻译成中文，只返回翻译结果，不要废话：\n{text}"
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ 翻译失败。标题：{text}")
        print(f"❌ 具体错误详情: {e}")
        return text # 失败依然返回原文，保证报纸能印出来

def start_process():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 致命错误：找不到 GEMINI_API_KEY。")
        return

    # ---------------------------------------------------------
    # 【核心修复区：谷歌工厂标准】
    # 强行给官方零件下指令：必须走 v1 正式版通道，不准用默认的 v1beta
    # ---------------------------------------------------------
    client = genai.Client(
        api_key=api_key, 
        http_options={'api_version': 'v1'} 
    )

    items_html = ""
    for name, url in FEEDS.items():
        # feedparser 非常成熟，无需修改
        feed = feedparser.parse(url)
        print(f"正在抓取并翻译: {name}")
        
        for entry in feed.entries[:3]:
            translated = translate_text(entry.title, client)
            items_html += f"<li>[{name}] <a href='{entry.link}'>{translated}</a></li>"

    # 生成网页
    html_template = f"<html><meta charset='utf-8'><body><h1>今日全球资讯</h1><ul>{items_html}</ul></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✅ 所有资讯处理完毕，网页已生成！")

if __name__ == "__main__":
    start_process()
