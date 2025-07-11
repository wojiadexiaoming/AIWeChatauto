import requests
import json

# 从控制台读取access_token
access_token = input("请输入access_token: ")

# 硬编码草稿内容
draft_data = {
    "articles": [
        {
            "title": "AI时代：探索机器学习的未来",
            "author": "AI笔记",
            "content": "<h2>什么是机器学习？</h2>\n<p>机器学习是人工智能的核心技术之一，通过算法让计算机从数据中学习规律，并做出预测或决策。</p>\n<h2>机器学习的应用场景</h2>\n<p>从自动驾驶到医疗诊断，机器学习正在改变我们的生活。</p>\n<p><img src=\"http://mmbiz.qpic.cn/sz_mmbiz_png/fx7icJdX4F6OXB3lyHQKGpQWfGSzKznLjsKA5khz0DGyksgfcQVfRPj2qUrqQuYqAKh4iaevUx8Odic7Qoibq2ugqQ/0?wx_fmt=png\" alt=\"AI技术\"></p>\n<blockquote>“机器学习是未来十年最重要的技术趋势。” —— 李开复</blockquote>",
            "digest": "探索机器学习的奥秘，了解AI如何改变世界。",
            "thumb_media_id": "MEH-ro_tay7nl2G5RPAwQxgBRfDweToNx8JfF8cpmvBeob9e1Q0XNVwBx5GnsHub",
            "content_source_url": "https://example.com/ai-notes", # 替换为实际的图文消息URL
            "show_cover_pic": 1
        }
    ]
}

# 调用微信接口新增草稿
url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
headers = {"Content-Type": "application/json; charset=utf-8"}
response = requests.post(url, data=json.dumps(draft_data, ensure_ascii=False), headers=headers)
result = response.json()

print("新增草稿结果:", json.dumps(result, indent=2, ensure_ascii=False))