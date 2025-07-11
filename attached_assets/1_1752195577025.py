import requests
import json
import time
from datetime import datetime

def get_access_token(appid, appsecret):
    """
    获取微信access_token
    :param appid: 公众号的AppID
    :param appsecret: 公众号的AppSecret
    :return: 返回access_token和过期时间(秒)
    """
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        result = response.json()
        
        if 'access_token' in result:
            return result['access_token'], result['expires_in']
        else:
            print(f"获取access_token失败，错误码: {result.get('errcode')}, 错误信息: {result.get('errmsg')}")
            return None, None
    except Exception as e:
        print(f"请求发生异常: {e}")
        return None, None

def save_token_to_file(token_info, filename="access_token_info.json"):
    """
    将token信息保存到文件
    :param token_info: 包含token信息的字典
    :param filename: 保存的文件名
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(token_info, f, ensure_ascii=False, indent=4)
        print(f"access_token信息已保存到文件: {filename}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

def main():
    # 用户需要在此处填写自己的AppID和AppSecret
    appid = input("请输入您的AppID: ")
    appsecret = input("请输入您的AppSecret: ")
    
    # 获取access_token
    access_token, expires_in = get_access_token(appid, appsecret)
    
    if access_token:
        # 计算过期时间戳
        expire_time = int(time.time()) + expires_in
        expire_time_str = datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # 准备保存的信息
        token_info = {
            "access_token": access_token,
            "expires_in": expires_in,
            "expire_time": expire_time,
            "expire_time_str": expire_time_str,
            "appid": appid,
            "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存到文件
        save_token_to_file(token_info)
        
        # 打印结果
        print("\n获取access_token成功:")
        print(f"access_token: {access_token}")
        print(f"有效期(秒): {expires_in}")
        print(f"过期时间: {expire_time_str}")
    else:
        print("\n获取access_token失败，请检查AppID和AppSecret是否正确，以及服务器IP是否在白名单中。")

if __name__ == "__main__":
    main()