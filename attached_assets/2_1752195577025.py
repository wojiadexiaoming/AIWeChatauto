import requests
import json
import os
from datetime import datetime

class WeChatMaterialUploader:
    def __init__(self, access_token):
        self.access_token = access_token
    
    def upload_article_image(self, image_path):
        """
        上传图文消息内的图片获取URL
        :param image_path: 图片文件路径
        :return: 图片URL
        """
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self.access_token}"
        
        try:
            with open(image_path, 'rb') as f:
                files = {'media': (os.path.basename(image_path), f)}
                response = requests.post(url, files=files)
                response.raise_for_status()
                result = response.json()
                
                if 'url' in result:
                    return result['url']
                else:
                    print(f"上传图文消息图片失败，错误码: {result.get('errcode')}, 错误信息: {result.get('errmsg')}")
                    return None
        except Exception as e:
            print(f"上传图文消息图片时发生异常: {e}")
            return None
    
    def add_permanent_material(self, file_path, material_type, description=None):
        """
        新增永久素材
        :param file_path: 文件路径
        :param material_type: 素材类型(image/voice/video/thumb)
        :param description: 视频素材描述(仅视频素材需要)
        :return: 素材media_id和URL(图片素材)
        """
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type={material_type}"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f)}
                data = None
                
                if material_type == 'video' and description:
                    if isinstance(description, dict):
                        description = json.dumps(description, ensure_ascii=False)
                    files['description'] = (None, description)
                
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()
                result = response.json()
                
                if 'media_id' in result:
                    return result
                else:
                    print(f"上传永久素材失败，错误码: {result.get('errcode')}, 错误信息: {result.get('errmsg')}")
                    return None
        except Exception as e:
            print(f"上传永久素材时发生异常: {e}")
            return None
    
    def save_result_to_file(self, result, operation_type, filename="upload_result.json"):
        """
        将上传结果保存到文件
        :param result: 上传结果
        :param operation_type: 操作类型
        :param filename: 保存的文件名
        """
        try:
            result_info = {
                "operation_type": operation_type,
                "result": result,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_info, f, ensure_ascii=False, indent=4)
            
            print(f"上传结果已保存到文件: {filename}")
        except Exception as e:
            print(f"保存上传结果时发生错误: {e}")

def main():
    # 用户输入
    access_token = input("请输入您的access_token: ")
    uploader = WeChatMaterialUploader(access_token)
    
    print("\n请选择要执行的操作:")
    print("1. 上传图文消息内的图片获取URL")
    print("2. 新增永久素材")
    choice = input("请输入您的选择(1/2): ")
    
    if choice == '1':
        # 上传图文消息图片
        image_path = input("请输入要上传的图片路径: ")
        result = uploader.upload_article_image(image_path)
        
        if result:
            print(f"\n上传成功，图片URL: {result}")
            uploader.save_result_to_file({"url": result}, "upload_article_image")
    elif choice == '2':
        # 新增永久素材
        file_path = input("请输入要上传的文件路径: ")
        material_type = input("请输入素材类型(image/voice/video/thumb): ")
        
        description = None
        if material_type == 'video':
            title = input("请输入视频标题(不超过30字): ")
            introduction = input("请输入视频简介: ")
            description = {
                "title": title,
                "introduction": introduction
            }
        
        result = uploader.add_permanent_material(file_path, material_type, description)
        
        if result:
            print("\n上传成功:")
            print(f"media_id: {result.get('media_id')}")
            if 'url' in result:
                print(f"图片URL: {result.get('url')}")
            uploader.save_result_to_file(result, "add_permanent_material")
    else:
        print("无效的选择")

if __name__ == "__main__":
    main()