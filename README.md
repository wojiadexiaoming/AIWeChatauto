
# AIWeChatauto - 微信公众号AI内容创作与自动发布平台

> 🚀 一站式AI写作、智能配图、极致排版、自动发布，助力新媒体人高效运营公众号！

---
<img width="1115" height="628" alt="图片" src="https://github.com/user-attachments/assets/f8474d29-af77-4f24-8b8f-fee88abe30b8" />


## ✨ 项目亮点

- **多模型支持**：Gemini、DeepSeek、阿里云百炼等主流大模型一键切换
- **智能配图**：Pexels图库/AI生图，自动适配微信防盗链
- **极致排版**：自动内联样式，完美适配微信，支持多主题模板
- **草稿/历史/一键发布**：全流程自动化，支持草稿管理与历史追溯
- **本地/云端/容器化部署**：支持Windows、Mac、Docker一键部署
- **开放API**：可对接uniapp等前端，支持二次开发

---

## 🚀 功能总览

### 🌟 一站式AI内容创作与自动发布

- **多平台热点采集与智能选题**
  - 支持抖音、快手、B站、微博、X（推特）、TikTok、YouTube、知乎等主流平台，一键抓取行业最新热点。
  - 自动分析平台热榜，结合行业趋势，AI智能生成爆款标题，助力内容精准选题。
    
<img width="621" height="652" alt="wechat_2025-07-25_092906_078" src="https://github.com/user-attachments/assets/ba407b20-4eac-4174-9e32-21c13e1194cf" />

- **多模型AI写作引擎**
  - 集成 Gemini、DeepSeek、阿里云百炼等顶级大模型，随心切换，满足不同风格与场景需求。
  - 高级 Prompt 工程，深度定制公众号内容生成，支持自定义模板、字数、风格等参数。

- **智能配图与极致排版**
  - 支持 Pexels 图库、AI生图，自动适配微信防盗链，图片风格可选，视觉效果专业。
  - 内置多套精美排版模板，自动内联样式，完美适配微信 Webview，提升阅读体验。
    
<img width="605" height="539" alt="wechat_2025-07-25_092841_758" src="https://github.com/user-attachments/assets/a8cac394-9fd9-4ff7-861d-285196e0a1e4" />

- **全流程自动化：草稿、历史、定时、一键发布**
  - 草稿管理、历史追溯、定时发布、自动推送，极致提升内容生产与运营效率。
  - 支持一键发布到微信公众号，自动处理图片上传、封面生成、摘要提取等繁琐环节。

- **可视化配置与前端交互**
  - 前端支持多平台、多行业选择，支持自定义行业输入，所见即所得。
  - 配置管理、模型测试、历史记录、内容预览等一应俱全，操作简单易用。

- **开放API与二次开发友好**
  - 完善的接口设计，支持对接 uniapp、小程序、第三方平台，灵活扩展。
  - 代码结构清晰，便于二次开发和个性化定制。

- **安全合规与多端部署**
  - 支持本地、云端、Docker一键部署，兼容 Windows/Mac/Linux。
  - 重要信息本地存储，支持多平台API Key灵活配置，保障数据安全。

---

## 🏆 为什么选择 AIWeChatauto？

- **极致自动化**：从选题、写作、配图到发布，全流程一键完成，释放你的内容生产力。
- **智能选题引擎**：行业+平台热榜智能分析，AI生成爆款标题，内容更有传播力。
- **多模型加持**：主流大模型随心切换，写作风格百变，满足不同内容需求。
- **专业排版与配图**：自动适配微信生态，图片、样式、模板一站式搞定。
- **开源免费，持续更新**：完全开源，永久免费，社区活跃，功能持续进化。
- **开发者友好**：接口开放，易于集成和二次开发，助力你的内容生态升级。

---

## 🛠️ 适用场景

- 自媒体人/内容创业者/企业新媒体团队
- 需要高频、批量、自动化生成和发布公众号内容的场景
- 需要AI辅助写作、智能配图、自动排版的内容生产者

---

## 🖥️ Windows 一键安装体验

无需 Python 环境，零配置一键安装！
已提供 Windows 平台专用的 exe 安装包，下载后双击即可完成部署，无需手动安装 Python、依赖或命令行操作。
安装完成后，桌面会自动生成启动快捷方式，点击即可直接打开 AIWeChatauto 系统，极致便捷。
适合所有 Windows 用户，尤其是新媒体运营、内容创作者、企业团队等非技术人群。
安装步骤：
前往 Releases 页面 下载最新版安装包（.exe）。
双击运行，按提示完成安装。
桌面快捷方式启动，浏览器自动打开系统首页。
按照页面提示完成公众号、AI平台等配置，即可开始智能创作！


---


## ⚡ 快速体验

### 1. 本地开发模式【适用于第一版】
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


打赏支持《感谢ღ( ´･ᴗ･` )比心》：

<img width="335" height="457" alt="微信图片_2025-07-13_185602_630" src="https://github.com/user-attachments/assets/8cbe8d7b-a5ba-4d3c-bc3b-dd449743e22b" /> ![微信图片_2025-07-13_185558_797](https://github.com/user-attachments/assets/fdb26494-4b49-4c01-b5cf-d415a2e5c8db)




