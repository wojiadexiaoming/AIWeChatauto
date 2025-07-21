<<<<<<< HEAD
# AIWeChatauto - 微信公众号AI内容创作与自动发布平台

> 🚀 一站式AI写作、智能配图、极致排版、自动发布，助力新媒体人高效运营公众号！

---

## ✨ 项目亮点

- **多模型支持**：Gemini、DeepSeek、阿里云百炼等主流大模型一键切换
- **智能配图**：Pexels图库/AI生图，自动适配微信防盗链
- **极致排版**：自动内联样式，完美适配微信，支持多主题模板
- **草稿/历史/一键发布**：全流程自动化，支持草稿管理与历史追溯
- **本地/云端/容器化部署**：支持Windows、Mac、Docker一键部署
- **开放API**：可对接uniapp等前端，支持二次开发

---

## 🛠️ 适用场景

- 自媒体人/内容创业者/企业新媒体团队
- 需要高频、批量、自动化生成和发布公众号内容的场景
- 需要AI辅助写作、智能配图、自动排版的内容生产者

---

## ⚡ 快速体验

### 1. 本地开发模式
```bash
git clone https://github.com/wojiadexiaoming/AIWeChatauto.git
cd CodeStash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python main.py
```
- 访问 [http://127.0.0.1:5000][公网ip]（需要将公网ip添加到自己公众号的ip白名单才可以）



### 2. 配置说明
- 复制 `config/config_template.json` 为 `config.json`，填写公众号、AI平台等信息
- 支持多模型API Key、作者信息、图片模型等灵活配置

---

## 🧩 主要配置项说明

| 配置项                | 说明                         |
|----------------------|------------------------------|
| wechat_appid         | 公众号AppID                  |
| wechat_appsecret     | 公众号AppSecret              |
| gemini_api_key       | Gemini API Key               |
| deepseek_api_key     | DeepSeek API Key             |
| dashscope_api_key    | 阿里云百炼API Key            |
| pexels_api_key       | Pexels图库API Key            |
| author               | 文章作者名                   |
| image_model          | 配图模型（gemini/pexels等）  |
| ...                  | 更多详见 config.json         |

---

## 💡 常见问题

- **图片防盗链/不显示？**  
  已内置图片代理和微信图片上传，公众号内外均可正常显示。
- **AI接口报错？**  
  检查API Key、网络，或切换备用模型。
- **草稿/发布失败？**  
  检查公众号配置、图片素材、封面图片是否有效。
- **IP白名单/接口权限？**  
  需将服务器公网IP加入公众号后台白名单。

---

## 🏆 贡献与交流

- 欢迎提交 Issue、PR，或加入交流群共同完善项目！
- 商业授权/定制开发请联系：**[ming7466464@gmail.com/1576129288@qq.com]**

---

## 📜 License

MIT License

> 如需商业授权或盈利性服务，请参见 [LICENSE-CN.md](LICENSE-CN.md)

---

如需更详细的功能演示、模板预览、二次开发文档等，可随时联系作者！ 

打赏支持：
=======
# AIWeChatauto - 微信公众号AI内容创作与自动发布平台

> 🚀 一站式AI写作、智能配图、极致排版、自动发布，助力新媒体人高效运营公众号！

---

## ✨ 项目亮点

- **多模型支持**：Gemini、DeepSeek、阿里云百炼等主流大模型一键切换
- **智能配图**：Pexels图库/AI生图，自动适配微信防盗链
- **极致排版**：自动内联样式，完美适配微信，支持多主题模板
- **草稿/历史/一键发布**：全流程自动化，支持草稿管理与历史追溯
- **本地/云端/容器化部署**：支持Windows、Mac、Docker一键部署
- **开放API**：可对接uniapp等前端，支持二次开发

---

## 🛠️ 适用场景

- 自媒体人/内容创业者/企业新媒体团队
- 需要高频、批量、自动化生成和发布公众号内容的场景
- 需要AI辅助写作、智能配图、自动排版的内容生产者

---

## ⚡ 快速体验

### 1. 本地开发模式
```bash
git clone https://github.com/wojiadexiaoming/AIWeChatauto.git
cd CodeStash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python main.py
```
- 访问 [http://127.0.0.1:5000][公网ip]（需要将公网ip添加到自己公众号的ip白名单才可以）



### 2. 配置说明
- 复制 `config/config_template.json` 为 `config.json`，填写公众号、AI平台等信息
- 支持多模型API Key、作者信息、图片模型等灵活配置

---

## 🧩 主要配置项说明

| 配置项                | 说明                         |
|----------------------|------------------------------|
| wechat_appid         | 公众号AppID                  |
| wechat_appsecret     | 公众号AppSecret              |
| gemini_api_key       | Gemini API Key               |
| deepseek_api_key     | DeepSeek API Key             |
| dashscope_api_key    | 阿里云百炼API Key            |
| pexels_api_key       | Pexels图库API Key            |
| author               | 文章作者名                   |
| image_model          | 配图模型（gemini/pexels等）  |
| ...                  | 更多详见 config.json         |

---

## 💡 常见问题

- **图片防盗链/不显示？**  
  已内置图片代理和微信图片上传，公众号内外均可正常显示。
- **AI接口报错？**  
  检查API Key、网络，或切换备用模型。
- **草稿/发布失败？**  
  检查公众号配置、图片素材、封面图片是否有效。
- **IP白名单/接口权限？**  
  需将服务器公网IP加入公众号后台白名单。

---

## 🏆 贡献与交流

- 欢迎提交 Issue、PR，或加入交流群共同完善项目！
- ![微信图片_2025-07-13_190348_328](https://github.com/user-attachments/assets/9bb6bd37-6be1-467d-923d-c464e43640a4)

- 商业授权/定制开发请联系：**[ming7466464@gmail.com/1576129288@qq.com]**

---

## 📜 License

MIT License

> 如需商业授权或盈利性服务，请参见 [LICENSE-CN.md](LICENSE-CN.md)

---

如需更详细的功能演示、模板预览、二次开发文档等，可随时联系作者！ 
![微信图片_2025-07-13_190348_328](https://github.com/user-attachments/assets/49ec38ff-2321-4c07-953f-59d685b2f682)


打赏支持：

<img width="335" height="457" alt="微信图片_2025-07-13_185602_630" src="https://github.com/user-attachments/assets/8cbe8d7b-a5ba-4d3c-bc3b-dd449743e22b" />

![微信图片_2025-07-13_185558_797](https://github.com/user-attachments/assets/fdb26494-4b49-4c01-b5cf-d415a2e5c8db)




>>>>>>> 4939a71745bd4c2b6983a54b58451f6e8eb98712
