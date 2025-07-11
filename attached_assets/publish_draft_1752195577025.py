import requests
import json

# 从控制台读取access_token
access_token = input("请输入access_token: ")

# 硬编码草稿ID
draft_id = "MEH-ro_tay7nl2G5RPAwQx3cvxkYSLoXHLJj2VFX4UM8g_Tlhbn9k4KVu1oyqIxC"  # 替换为实际的草稿ID

# 调用微信接口发布草稿
url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
payload = {
    "media_id": draft_id
}
response = requests.post(url, json=payload)
result = response.json()

print("发布草稿结果:", json.dumps(result, indent=2, ensure_ascii=False))