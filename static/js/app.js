/**
 * 微信公众号AI发布系统 - 前端JavaScript
 */

// 工具类
class Utils {
    static showToast(message, type = 'info', delay = 3000) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            Utils.createToastContainer();
        }
        
        const toast = Utils.createToast(message, type);
        document.getElementById('toast-container').appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            delay: delay,
            autohide: true
        });
        bsToast.show();
        
        // 自动移除toast元素
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    static createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    static createToast(message, type) {
        const toastTypes = {
            'success': 'text-bg-success',
            'error': 'text-bg-danger', 
            'warning': 'text-bg-warning',
            'info': 'text-bg-info'
        };
        
        const toastElement = document.createElement('div');
        toastElement.className = `toast ${toastTypes[type] || toastTypes.info}`;
        toastElement.setAttribute('role', 'alert');
        toastElement.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">系统提示</strong>
                <small>刚刚</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        return toastElement;
    }
    
    static addLog(message, level = 'info') {
        const timestamp = new Date().toLocaleString('zh-CN');
        const logEntry = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
        console.log(logEntry);
    }
    
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    static updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString('zh-CN');
        }
    }
}

// API客户端类
class ApiClient {
    static async request(url, options = {}) {
        try {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || '请求失败');
            }
            
            return data;
        } catch (error) {
            Utils.addLog(`API请求失败: ${error.message}`, 'error');
            throw error;
        }
    }
    
    static async get(url) {
        return this.request(url, { method: 'GET' });
    }
    
    static async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
}

// 配置管理类
class ConfigManager {
    static async loadConfig() {
        try {
            const response = await ApiClient.get('/api/config');
            if (response.success) {
                this.fillConfigForm(response.data);
                Utils.addLog('配置加载成功');
            }
        } catch (error) {
            Utils.showToast('加载配置失败: ' + error.message, 'error');
        }
    }
    
    static async saveConfig() {
        try {
            const configData = this.getConfigFormData();
            Utils.addLog(`准备保存配置: ${JSON.stringify(configData)}`);
            console.log('配置数据:', configData);
            
            const response = await ApiClient.post('/api/config', configData);
            console.log('保存响应:', response);
            
            if (response.success) {
                Utils.showToast('配置保存成功', 'success');
                Utils.addLog('配置保存成功');
                
                // 重新加载配置以确认保存成功
                await this.loadConfig();
            } else {
                Utils.showToast('保存失败: ' + response.message, 'error');
                Utils.addLog(`保存失败: ${response.message}`, 'error');
                console.error('保存失败:', response);
            }
        } catch (error) {
            Utils.showToast('保存配置失败: ' + error.message, 'error');
            Utils.addLog(`保存配置异常: ${error.message}`, 'error');
            console.error('保存配置异常:', error);
        }
    }
    
    static getConfigFormData() {
        const wechat_appid = document.getElementById('wechat-appid')?.value || '';
        const wechat_appsecret = document.getElementById('wechat-appsecret')?.value || '';
        const gemini_api_key = document.getElementById('gemini-api-key')?.value || '';
        const gemini_model = document.getElementById('gemini-model')?.value || 'gemini-2.5-flash';
        const deepseek_api_key = document.getElementById('deepseek-api-key')?.value || '';
        const deepseek_model = document.getElementById('deepseek-model')?.value || 'deepseek-chat';
        const dashscope_api_key = document.getElementById('dashscope-api-key')?.value || '';
        const dashscope_model = document.getElementById('dashscope-model')?.value || 'qwen-turbo';
        const pexels_api_key = document.getElementById('pexels-api-key')?.value || '';
        const coze_token = document.getElementById('coze_token')?.value || '';
        const coze_workflow_id = document.getElementById('coze_workflow_id')?.value || '';
        const author = document.getElementById('author-name')?.value || 'AI笔记';
        const content_source_url = document.getElementById('content-source-url')?.value || '';
        
        return {
            wechat_appid,
            wechat_appsecret,
            gemini_api_key,
            gemini_model,
            deepseek_api_key,
            deepseek_model,
            dashscope_api_key,
            dashscope_model,
            pexels_api_key,
            coze_token,
            coze_workflow_id,
            author,
            content_source_url
        };
    }
    
    static fillConfigForm(config) {
        if (document.getElementById('wechat-appid')) {
            document.getElementById('wechat-appid').value = config.wechat_appid || '';
        }
        if (document.getElementById('wechat-appsecret')) {
            document.getElementById('wechat-appsecret').value = config.wechat_appsecret || '';
        }
        if (document.getElementById('gemini-api-key')) {
            document.getElementById('gemini-api-key').value = config.gemini_api_key || '';
        }
        if (document.getElementById('gemini-model')) {
            document.getElementById('gemini-model').value = config.gemini_model || 'gemini-2.5-flash';
        }
        if (document.getElementById('deepseek-api-key')) {
            document.getElementById('deepseek-api-key').value = config.deepseek_api_key || '';
        }
        if (document.getElementById('deepseek-model')) {
            document.getElementById('deepseek-model').value = config.deepseek_model || 'deepseek-chat';
        }
        if (document.getElementById('dashscope-api-key')) {
            document.getElementById('dashscope-api-key').value = config.dashscope_api_key || '';
        }
        if (document.getElementById('dashscope-model')) {
            document.getElementById('dashscope-model').value = config.dashscope_model || 'qwen-turbo';
        }
        if (document.getElementById('pexels-api-key')) {
            document.getElementById('pexels-api-key').value = config.pexels_api_key || '';
        }
        if (document.getElementById('coze_token')) {
            document.getElementById('coze_token').value = config.coze_token || '';
        }
        if (document.getElementById('coze_workflow_id')) {
            document.getElementById('coze_workflow_id').value = config.coze_workflow_id || '';
        }
        if (document.getElementById('author-name')) {
            document.getElementById('author-name').value = config.author || 'AI笔记';
        }
        if (document.getElementById('content-source-url')) {
            document.getElementById('content-source-url').value = config.content_source_url || '';
        }
    }
    
    static async testWeChatConnection() {
        try {
            Utils.addLog('开始测试微信连接');
            console.log('测试微信连接...');
            
            const response = await ApiClient.post('/api/test-wechat', {});
            console.log('微信测试响应:', response);
            Utils.addLog(`微信测试响应: ${JSON.stringify(response)}`);
            
            const statusElement = document.getElementById('wechat-status');
            
            if (response.success) {
                Utils.showToast('微信连接测试成功', 'success');
                if (statusElement) {
                    statusElement.textContent = '连接正常';
                    statusElement.className = 'badge bg-success';
                }
            } else {
                Utils.showToast('微信连接测试失败: ' + response.message, 'error');
                if (statusElement) {
                    statusElement.textContent = '连接失败';
                    statusElement.className = 'badge bg-danger';
                }
                // 打印调试信息
                if (response.debug_info) {
                    console.log('调试信息:', response.debug_info);
                    Utils.addLog(`调试信息: ${JSON.stringify(response.debug_info)}`);
                }
            }
        } catch (error) {
            Utils.showToast('测试连接失败: ' + error.message, 'error');
            Utils.addLog(`微信测试异常: ${error.message}`, 'error');
            console.error('微信测试异常:', error);
        }
    }
    
    static async testGeminiConnection() {
        try {
            Utils.addLog('开始测试Gemini连接');
            console.log('测试Gemini连接...');
            
            const response = await ApiClient.post('/api/test-gemini', {});
            console.log('Gemini测试响应:', response);
            Utils.addLog(`Gemini测试响应: ${JSON.stringify(response)}`);
            
            const statusElement = document.getElementById('gemini-status');
            
            if (response.success) {
                Utils.showToast('Gemini连接测试成功', 'success');
                if (statusElement) {
                    statusElement.textContent = '连接正常';
                    statusElement.className = 'badge bg-success';
                }
            } else {
                // 特殊处理配额超限错误
                if (response.error_type === 'quota_exceeded') {
                    Utils.showToast('API配额已用完，建议切换模型或等待配额重置', 'warning');
                    if (statusElement) {
                        statusElement.textContent = '配额超限';
                        statusElement.className = 'badge bg-warning';
                    }
                    // 显示详细错误信息
                    if (response.details) {
                        console.log('配额详情:', response.details);
                        Utils.addLog(`配额详情: ${response.details}`);
                    }
                } else if (response.error_type === 'invalid_key') {
                    Utils.showToast('API密钥无效，请检查密钥是否正确', 'error');
                    if (statusElement) {
                        statusElement.textContent = '密钥无效';
                        statusElement.className = 'badge bg-danger';
                }
            } else {
                Utils.showToast('Gemini连接测试失败: ' + response.message, 'error');
                if (statusElement) {
                    statusElement.textContent = '连接失败';
                    statusElement.className = 'badge bg-danger';
                }
                }
                
                // 打印调试信息
                if (response.debug_info) {
                    console.log('调试信息:', response.debug_info);
                    Utils.addLog(`调试信息: ${JSON.stringify(response.debug_info)}`);
                }
            }
        } catch (error) {
            Utils.showToast('测试连接失败: ' + error.message, 'error');
            Utils.addLog(`Gemini测试异常: ${error.message}`, 'error');
            console.error('Gemini测试异常:', error);
        }
    }
    
    static async loadGeminiModels() {
        try {
            Utils.addLog('开始加载Gemini模型列表');
            console.log('加载Gemini模型列表...');
            
            const response = await ApiClient.get('/api/gemini-models');
            console.log('Gemini模型列表响应:', response);
            Utils.addLog(`Gemini模型列表响应: ${JSON.stringify(response)}`);
            
            const modelSelect = document.getElementById('gemini-model');
            if (!modelSelect) {
                Utils.addLog('模型选择下拉框未找到', 'error');
                return;
            }
            
            if (response.success && response.data.models && response.data.models.length > 0) {
                // 清空现有选项
                modelSelect.innerHTML = '';
                
                // 添加新选项
                response.data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = this.formatModelName(model);
                    modelSelect.appendChild(option);
                });
                
                // 设置当前选中的模型
                if (response.data.current_model) {
                    modelSelect.value = response.data.current_model;
                }
                
                Utils.addLog(`成功加载 ${response.data.models.length} 个模型`);
                Utils.showToast(`成功加载 ${response.data.models.length} 个可用模型`, 'success');
            } else {
                Utils.addLog('加载模型列表失败: ' + (response.message || '未知错误'), 'error');
                Utils.showToast('加载模型列表失败: ' + (response.message || '未知错误'), 'error');
            }
        } catch (error) {
            Utils.showToast('加载模型列表失败: ' + error.message, 'error');
            Utils.addLog(`加载模型列表异常: ${error.message}`, 'error');
            console.error('加载模型列表异常:', error);
        }
    }
    
    static formatModelName(modelName) {
        // 格式化模型名称显示
        const modelMap = {
            'gemini-2.5-flash': 'Gemini 2.5 Flash (快速)',
            'gemini-2.5-pro': 'Gemini 2.5 Pro (专业版)',
            'gemini-2.0-flash-preview-image-generation': 'Gemini 2.0 Flash (图像生成)',
            'gemini-1.5-flash': 'Gemini 1.5 Flash',
            'gemini-1.5-pro': 'Gemini 1.5 Pro'
        };
        
        return modelMap[modelName] || modelName;
    }
    
    static async testDeepSeekConnection() {
        try {
            Utils.addLog('开始测试DeepSeek连接');
            console.log('测试DeepSeek连接...');
            
            const response = await ApiClient.post('/api/test-deepseek', {});
            console.log('DeepSeek测试响应:', response);
            Utils.addLog(`DeepSeek测试响应: ${JSON.stringify(response)}`);
            
            const statusElement = document.getElementById('deepseek-status');
            
            if (response.success) {
                Utils.showToast('DeepSeek连接测试成功', 'success');
                if (statusElement) {
                    statusElement.textContent = '连接正常';
                    statusElement.className = 'badge bg-success';
                }
            } else {
                // 特殊处理配额超限错误
                if (response.error_type === 'quota_exceeded') {
                    Utils.showToast('API配额已用完，建议切换模型或等待配额重置', 'warning');
                    if (statusElement) {
                        statusElement.textContent = '配额超限';
                        statusElement.className = 'badge bg-warning';
                    }
                    // 显示详细错误信息
                    if (response.details) {
                        console.log('配额详情:', response.details);
                        Utils.addLog(`配额详情: ${response.details}`);
                    }
                } else if (response.error_type === 'invalid_key') {
                    Utils.showToast('API密钥无效，请检查密钥是否正确', 'error');
                    if (statusElement) {
                        statusElement.textContent = '密钥无效';
                        statusElement.className = 'badge bg-danger';
                    }
                } else {
                    Utils.showToast('DeepSeek连接测试失败: ' + response.message, 'error');
                    if (statusElement) {
                        statusElement.textContent = '连接失败';
                        statusElement.className = 'badge bg-danger';
                    }
                }
                
                // 打印调试信息
                if (response.debug_info) {
                    console.log('调试信息:', response.debug_info);
                    Utils.addLog(`调试信息: ${JSON.stringify(response.debug_info)}`);
                }
            }
        } catch (error) {
            Utils.showToast('测试连接失败: ' + error.message, 'error');
            Utils.addLog(`DeepSeek测试异常: ${error.message}`, 'error');
            console.error('DeepSeek测试异常:', error);
        }
    }
    
    static async loadDeepSeekModels() {
        try {
            Utils.addLog('开始加载DeepSeek模型列表');
            console.log('加载DeepSeek模型列表...');
            
            const response = await ApiClient.get('/api/deepseek-models');
            console.log('DeepSeek模型列表响应:', response);
            Utils.addLog(`DeepSeek模型列表响应: ${JSON.stringify(response)}`);
            
            const modelSelect = document.getElementById('deepseek-model');
            if (!modelSelect) {
                Utils.addLog('DeepSeek模型选择下拉框未找到', 'error');
                return;
            }
            
            if (response.success && response.data.models && response.data.models.length > 0) {
                // 清空现有选项
                modelSelect.innerHTML = '';
                
                // 添加新选项
                response.data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = this.formatDeepSeekModelName(model);
                    modelSelect.appendChild(option);
                });
                
                // 设置当前选中的模型
                if (response.data.current_model) {
                    modelSelect.value = response.data.current_model;
                }
                
                Utils.addLog(`成功加载 ${response.data.models.length} 个DeepSeek模型`);
                Utils.showToast(`成功加载 ${response.data.models.length} 个可用DeepSeek模型`, 'success');
            } else {
                Utils.addLog('加载DeepSeek模型列表失败: ' + (response.message || '未知错误'), 'error');
                Utils.showToast('加载DeepSeek模型列表失败: ' + (response.message || '未知错误'), 'error');
            }
        } catch (error) {
            Utils.showToast('加载DeepSeek模型列表失败: ' + error.message, 'error');
            Utils.addLog(`加载DeepSeek模型列表异常: ${error.message}`, 'error');
            console.error('加载DeepSeek模型列表异常:', error);
        }
    }
    
    static formatDeepSeekModelName(modelName) {
        // 格式化DeepSeek模型名称显示
        const modelMap = {
            'deepseek-chat': 'DeepSeek Chat (通用对话)',
            'deepseek-coder': 'DeepSeek Coder (代码生成)',
            'deepseek-chat-instruct': 'DeepSeek Chat Instruct (指令对话)',
            'deepseek-reasoner': 'DeepSeek Reasoner (推理模型)'
        };
        
        return modelMap[modelName] || modelName;
    }
    
    static async testDashScopeConnection() {
        try {
            Utils.addLog('开始测试阿里云百炼连接');
            console.log('测试阿里云百炼连接...');
            
            const response = await ApiClient.post('/api/test-dashscope', {});
            console.log('阿里云百炼测试响应:', response);
            Utils.addLog(`阿里云百炼测试响应: ${JSON.stringify(response)}`);
            
            const statusElement = document.getElementById('dashscope-status');
            
            if (response.success) {
                Utils.showToast('阿里云百炼连接测试成功', 'success');
                if (statusElement) {
                    statusElement.textContent = '连接正常';
                    statusElement.className = 'badge bg-success';
                }
            } else {
                // 特殊处理配额超限错误
                if (response.error_type === 'quota_exceeded') {
                    Utils.showToast('API配额已用完，建议切换模型或等待配额重置', 'warning');
                    if (statusElement) {
                        statusElement.textContent = '配额超限';
                        statusElement.className = 'badge bg-warning';
                    }
                } else if (response.error_type === 'invalid_key') {
                    Utils.showToast('API密钥无效，请检查密钥是否正确', 'error');
                    if (statusElement) {
                        statusElement.textContent = '密钥无效';
                        statusElement.className = 'badge bg-danger';
                    }
                } else {
                    Utils.showToast('阿里云百炼连接测试失败: ' + response.message, 'error');
                    if (statusElement) {
                        statusElement.textContent = '连接失败';
                        statusElement.className = 'badge bg-danger';
                    }
                }
                
                // 打印调试信息
                if (response.debug_info) {
                    console.log('调试信息:', response.debug_info);
                    Utils.addLog(`调试信息: ${JSON.stringify(response.debug_info)}`);
                }
            }
        } catch (error) {
            Utils.showToast('测试连接失败: ' + error.message, 'error');
            Utils.addLog(`阿里云百炼测试异常: ${error.message}`, 'error');
            console.error('阿里云百炼测试异常:', error);
        }
    }
    
    static async loadDashScopeModels() {
        try {
            Utils.addLog('开始加载阿里云百炼模型列表');
            console.log('加载阿里云百炼模型列表...');
            
            const response = await ApiClient.get('/api/dashscope-models');
            console.log('阿里云百炼模型列表响应:', response);
            Utils.addLog(`阿里云百炼模型列表响应: ${JSON.stringify(response)}`);
            
            // 检查响应状态
            if (!response) {
                Utils.addLog('阿里云百炼模型列表响应为空', 'error');
                Utils.showToast('获取模型列表失败：响应为空', 'error');
                return;
            }
            
            const modelSelect = document.getElementById('dashscope-model');
            if (!modelSelect) {
                Utils.addLog('阿里云百炼模型选择下拉框未找到', 'error');
                return;
            }
            
            if (response.success && response.data.models && response.data.models.length > 0) {
                // 清空现有选项
                modelSelect.innerHTML = '';
                
                // 添加模型选项，优先显示description，如果没有则显示id
                response.data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    // 优先显示description，如果没有则显示id
                    option.textContent = model.description || model.id;
                    modelSelect.appendChild(option);
                });
                
                // 设置当前选中的模型
                if (response.data.current_model) {
                    modelSelect.value = response.data.current_model;
                }
                
                Utils.addLog(`成功加载 ${response.data.models.length} 个阿里云百炼模型`);
                Utils.showToast(`成功加载 ${response.data.models.length} 个可用阿里云百炼模型`, 'success');
            } else {
                Utils.addLog('加载阿里云百炼模型列表失败: ' + (response.message || '未知错误'), 'error');
                Utils.showToast('加载阿里云百炼模型列表失败: ' + (response.message || '未知错误'), 'error');
            }
        } catch (error) {
            Utils.showToast('加载阿里云百炼模型列表失败: ' + error.message, 'error');
            Utils.addLog(`加载阿里云百炼模型列表异常: ${error.message}`, 'error');
            console.error('加载阿里云百炼模型列表异常:', error);
        }
    }
}

// 文章生成类
class ArticleGenerator {
    static async generateArticle() {
        const titleElement = document.getElementById('article-title');
        if (!titleElement) {
            Utils.showToast('页面元素未找到', 'error');
            return;
        }
        
        const title = titleElement.value.trim();
        if (!title) {
            Utils.showToast('请输入文章标题', 'warning');
            return;
        }
        
        // 获取AI模型选择
        const aiModelElement = document.getElementById('ai-model-select');
        const ai_model = aiModelElement ? aiModelElement.value : 'gemini';
        
        // 获取生图模型选择
        const imageModelElement = document.getElementById('image-model-select');
        const image_model = imageModelElement ? imageModelElement.value : 'gemini';
        
        // 获取自定义生图提示词
        const customImagePromptElement = document.getElementById('custom-image-prompt');
        const custom_image_prompt = customImagePromptElement ? customImagePromptElement.value.trim() : '';
        
        // 新增：获取字数和配图数量
        const wordCountElement = document.getElementById('article-word-count');
        const imageCountElement = document.getElementById('article-image-count');
        const word_count = wordCountElement ? parseInt(wordCountElement.value) : 5000;
        const image_count = imageCountElement ? parseInt(imageCountElement.value) : 3;
        // 新增：获取参考元素HTML模板
        const formatTemplateElement = document.getElementById('format-template');
        const format_template = formatTemplateElement ? formatTemplateElement.value : '';

        // 新增：阿里云百炼高级参数
        let dashscope_params = undefined;
        if (image_model === 'dashscope') {
            const dashscopeImageModelValue = document.getElementById('dashscope-image-model-value').value;
            if (!dashscopeImageModelValue) {
                Utils.showToast('请选择阿里云百炼具体生图模型', 'warning');
                return;
            }
            const positive_prompt = document.getElementById('dashscope-positive-prompt').value.trim();
            const negative_prompt = document.getElementById('dashscope-negative-prompt').value.trim();
            const size = document.getElementById('dashscope-image-ratio').value.trim();
            const steps = document.getElementById('dashscope-steps').value.trim();
            dashscope_params = {
                model_name: dashscopeImageModelValue,
                positive_prompt,
                negative_prompt,
                size,
                steps: steps ? parseInt(steps) : undefined
            };
        }
        
        try {
            this.showGenerationProgress();
            Utils.addLog(`开始生成文章: ${title}，使用AI模型: ${ai_model}`);
            
            // 新增：将字数和配图数量传递到后端
            const response = await ApiClient.post('/api/generate-article', { 
                title, 
                word_count, 
                image_count, 
                format_template, 
                ai_model,
                image_model,
                custom_image_prompt, // 新增
                dashscope_params // 新增
            });
            
            if (response.success) {
                Utils.showToast('文章生成成功', 'success');
                this.showGenerationResult(response.data);
                ArticlePreview.showPreview(response.data);
                Utils.addLog('文章生成完成');
            } else {
                Utils.showToast('生成失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('生成文章失败: ' + error.message, 'error');
        } finally {
            this.hideGenerationProgress();
        }
    }
    
    static showGenerationProgress() {
        const progressElement = document.getElementById('generation-progress');
        if (progressElement) {
            progressElement.style.display = 'block';
            this.updateProgress(0, '正在接收生成需求...');
            
            // 获取用户设置的配图数量
            const imageCountElement = document.getElementById('image-count');
            const imageCount = imageCountElement ? parseInt(imageCountElement.value) || 10 : 10;
            
            // 根据实际日志分析的工作流程定义基础步骤
            const baseSteps = [
                { progress: 5, text: '正在发送需求到AI服务...' },
                { progress: 15, text: '正在生成文章内容...' },
                { progress: 25, text: '正在生成文章摘要...' },
                { progress: 35, text: '正在开始生成配图...' }
            ];
            
            // 动态生成配图步骤
            const imageSteps = [];
            const imageProgressStart = 35;
            const imageProgressEnd = 94;
            const progressPerImage = (imageProgressEnd - imageProgressStart) / imageCount;
            
            for (let i = 0; i < imageCount; i++) {
                const progress = imageProgressStart + (i + 1) * progressPerImage;
                imageSteps.push({
                    progress: Math.min(progress, imageProgressEnd),
                    text: `正在生成配图...`
                });
            }
            
            // 完成步骤
            const finalSteps = [
                { progress: 96, text: '正在插入图片到文章...' },
                { progress: 98, text: '正在优化文章内容...' },
                { progress: 99, text: '正在保存生成结果...' }
            ];
            
            // 合并所有步骤
            const generationSteps = [...baseSteps, ...imageSteps, ...finalSteps];
            
            let currentStep = 0;
            const interval = setInterval(() => {
                if (currentStep < generationSteps.length) {
                    const step = generationSteps[currentStep];
                    this.updateProgress(step.progress, step.text);
                    currentStep++;
                } else {
                    clearInterval(interval);
                    this.updateProgress(99, '即将完成...');
                }
            }, 8000); // 每800ms更新一个步骤，根据实际耗时调整
            
            // 保存interval引用，以便后续清除
            this.progressInterval = interval;
        }
    }
    
    static hideGenerationProgress() {
        // 清除进度更新interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        const progressElement = document.getElementById('generation-progress');
        if (progressElement) {
            this.updateProgress(100, '生成完成！');
            setTimeout(() => {
                progressElement.style.display = 'none';
            }, 1500); // 显示完成状态1.5秒
        }
    }
    
    static updateProgress(percent, text) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
        if (progressText) {
            progressText.textContent = text;
        }
    }
    
    static showGenerationResult(data) {
        // 更新统计
        const totalElement = document.getElementById('total-articles');
        if (totalElement) {
            const current = parseInt(totalElement.textContent) || 0;
            totalElement.textContent = current + 1;
        }
        
        // 刷新历史记录显示
        HistoryManager.loadGenerationHistory();
    }
}

// 历史记录管理类
class HistoryManager {
    static async loadGenerationHistory() {
        try {
            const response = await ApiClient.get('/api/generation-history');
            if (response.success) {
                this.displayGenerationHistory(response.data);
            } else {
                Utils.showToast('加载历史记录失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('加载历史记录失败: ' + error.message, 'error');
        }
    }
    
    static async loadPublishHistory() {
        try {
            const response = await ApiClient.get('/api/publish-history');
            if (response.success) {
                this.displayPublishHistory(response.data);
            } else {
                Utils.showToast('加载发布历史失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('加载发布历史失败: ' + error.message, 'error');
        }
    }
    
    static displayGenerationHistory(history) {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;
        
        if (history.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-clock-history"></i>
                    <h6>暂无历史记录</h6>
                    <p>生成的文章将在这里显示</p>
                </div>
            `;
            return;
        }
        
        historyList.innerHTML = '';
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const statusBadge = this.getStatusBadge(item.status);
            const actions = this.getHistoryActions(item);
            // 新增定时发布标记
            let scheduleInfo = '';
            if (item.publish_time && item.status !== 'published') {
                scheduleInfo = `<span class='badge bg-info ms-2'>已定时: ${item.publish_time}</span>`;
                // 如果有群发设置，显示群发标记
                if (item.enable_mass_send) {
                    scheduleInfo += `<span class='badge bg-warning ms-1'><i class="bi bi-broadcast"></i> 定时群发</span>`;
                }
            }
            historyItem.innerHTML = `
                <div class="history-item-header">
                    <h6>${item.title}</h6>
                    ${statusBadge}
                    ${scheduleInfo}
                </div>
                <p>生成时间: ${item.generated_at} | 长度: ${item.content_length}字 | 配图: ${item.image_count}张</p>
                <p>作者: ${item.author}</p>
                ${item.digest ? `<p class="text-muted">摘要: ${item.digest.substring(0, 100)}...</p>` : ''}
                ${actions}
            `;
            // 新增定时发布按钮
            const scheduleBtn = document.createElement('button');
            scheduleBtn.className = 'btn btn-sm btn-outline-secondary me-2';
            // 按钮禁用逻辑
            if (item.status !== 'published') {
                if (item.publish_time) {
                    scheduleBtn.disabled = true;
                    scheduleBtn.innerHTML = '<i class="bi bi-clock"></i> 已定时';
                } else {
                    scheduleBtn.innerHTML = '<i class="bi bi-clock"></i> 定时发布';
                    scheduleBtn.onclick = () => HistoryManager.openScheduleDialog(item);
                }
                historyItem.querySelector('.history-actions').appendChild(scheduleBtn);
            }
            historyList.appendChild(historyItem);
        });
    }
    
    static displayPublishHistory(history) {
        const publishHistoryList = document.getElementById('publish-history');
        if (!publishHistoryList) return;
        
        if (history.length === 0) {
            publishHistoryList.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-list-check"></i>
                    <h6>暂无发布历史</h6>
                    <p>发布的文章将在这里显示</p>
                </div>
            `;
            return;
        }
        
        publishHistoryList.innerHTML = '';
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            historyItem.innerHTML = `
                <div class="history-item-header">
                    <h6>${item.title}</h6>
                    <span class="badge bg-success">已发布</span>
                </div>
                <p>发布时间: ${item.published_at} | 长度: ${item.content_length}字 | 配图: ${item.image_count}张</p>
                <p>作者: ${item.author}</p>
                <p class="text-muted">发布ID: ${item.publish_id || 'N/A'}</p>
            `;
            
            publishHistoryList.appendChild(historyItem);
        });
    }
    
    static getStatusBadge(status) {
        const badges = {
            'generated': '<span class="badge bg-primary">已生成</span>',
            'saved': '<span class="badge bg-warning">已保存</span>',
            'published': '<span class="badge bg-success">已发布</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">未知</span>';
    }
    
    static getHistoryActions(item) {
        let actions = '';
        
        // 查看按钮
        actions += `<button class="btn btn-sm btn-outline-primary me-2" onclick="HistoryManager.viewArticle('${item.title}', ${JSON.stringify(item).replace(/"/g, '&quot;')})">
            <i class="bi bi-eye"></i> 查看
        </button>`;
        
        // 根据状态显示不同按钮
        if (item.status === 'generated') {
            actions += `<button class="btn btn-sm btn-outline-success me-2" onclick="HistoryManager.loadToPreview('${item.title}', ${JSON.stringify(item).replace(/"/g, '&quot;')})">
                <i class="bi bi-arrow-up-circle"></i> 加载到预览
            </button>`;
        }
        
        if (item.status === 'saved' && item.media_id) {
            actions += `<button class="btn btn-sm btn-outline-warning me-2" onclick="HistoryManager.publishDraft('${item.media_id}')">
                <i class="bi bi-send"></i> 发布
            </button>`;
        }
        
        // 新增：显示群发状态
        if (item.mass_sent) {
            actions += `<span class="badge bg-info ms-2"><i class="bi bi-broadcast"></i> 已群发</span>`;
        }
        
        return `<div class="history-actions mt-2">${actions}</div>`;
    }
    
    static async viewArticle(title, item) {
        try {
            if (!item.cache_files || item.cache_files.length === 0) {
                Utils.showToast('文章内容文件不存在', 'warning');
                return;
            }
            
            const response = await ApiClient.post('/api/article-content', {
                cache_files: item.cache_files
            });
            
            if (response.success) {
                // 显示文章内容
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="article-content">
                                    ${response.data.content}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                const modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
                
                // 清理模态框
                modal.addEventListener('hidden.bs.modal', () => {
                    document.body.removeChild(modal);
                });
            } else {
                Utils.showToast('获取文章内容失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('查看文章失败: ' + error.message, 'error');
        }
    }
    
    static async loadToPreview(title, item) {
        try {
            if (!item.cache_files || item.cache_files.length === 0) {
                Utils.showToast('文章内容文件不存在', 'warning');
                return;
            }
            
            const response = await ApiClient.post('/api/article-content', {
                cache_files: item.cache_files
            });
            
            if (response.success) {
                // 加载到预览区域
                const article = {
                    title: item.title,
                    content: response.data.content,
                    digest: item.digest,
                    generated_at: item.generated_at,
                    content_length: item.content_length,
                    image_count: item.image_count,
                    author: item.author
                };
                
                ArticlePreview.showPreview(article);
                Utils.showToast('文章已加载到预览区域', 'success');
            } else {
                Utils.showToast('加载文章失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('加载文章失败: ' + error.message, 'error');
        }
    }
    
    static async publishDraft(mediaId) {
        try {
            Utils.showToast('正在发布草稿...', 'info');
            
            const response = await ApiClient.post('/api/publish-draft', {
                media_id: mediaId
            });
            
            if (response.success) {
                Utils.showToast('草稿发布成功', 'success');
                // 刷新历史记录
                this.loadGenerationHistory();
                this.loadPublishHistory();
            } else {
                Utils.showToast('发布失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('发布失败: ' + error.message, 'error');
        }
    }

    // 新增：定时发布弹窗逻辑
    static openScheduleDialog(item) {
        // 创建弹窗
        let modal = document.createElement('div');
        modal.className = 'modal fade';
        // 弹窗默认值：如已有定时，显示原定时时间
        const defaultTime = item.publish_time ? item.publish_time.replace(' ', 'T') : HistoryManager.getDefaultScheduleTime();
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">定时发布 - ${item.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <label for="schedule-publish-time" class="form-label">请选择定时发布时间</label>
                        <input type="datetime-local" class="form-control" id="schedule-publish-time" value="${defaultTime}" min="${HistoryManager.getDefaultScheduleTime()}" />
                        <div class="form-check mt-3">
                            <input class="form-check-input" type="checkbox" id="schedule-mass-send">
                            <label class="form-check-label" for="schedule-mass-send">
                                <i class="bi bi-broadcast"></i> 同时群发给所有粉丝
                                <i class="bi bi-exclamation-triangle text-warning ms-1" 
                                   data-bs-toggle="tooltip" 
                                   data-bs-placement="top" 
                                   title="需要微信认证开通群发接口才可以使用此功能"></i>
                            </label>
                        </div>
                        ${item.publish_time ? `<div class='alert alert-info mt-2'>当前已定时：${item.publish_time}，可重新设置</div>` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" id="confirm-schedule-publish">确定定时</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        // 绑定确定按钮事件
        modal.querySelector('#confirm-schedule-publish').onclick = async () => {
            const dt = modal.querySelector('#schedule-publish-time').value;
            const enableMassSend = modal.querySelector('#schedule-mass-send').checked;
            if (!dt) {
                Utils.showToast('请选择定时发布时间', 'warning');
                return;
            }
            
            // 关闭弹窗
            modalInstance.hide();
            
            // 显示处理中的提示（显示5秒）
            Utils.showToast('正在设置定时任务，请稍候...', 'info', 5000);
            
            // 组装article数据
            let article = {
                title: item.title,
                author: item.author,
                digest: item.digest,
                content: '',
                content_source_url: item.content_source_url || '',
                thumb_media_id: '',
                show_cover_pic: 0,
                need_open_comment: 0,
                only_fans_can_comment: 0
            };
            
            try {
                // 获取内容
                const res = await ApiClient.post('/api/article-content', { cache_files: item.cache_files });
                if (res.success) {
                    article.content = res.data.content;
                } else {
                    Utils.showToast('获取文章内容失败: ' + res.message, 'error', 5000);
                    return;
                }
                
                // 先保存草稿，拿到media_id
                let media_id = '';
                const saveRes = await ApiClient.post('/api/save-draft', { article });
                if (saveRes.success && saveRes.data && saveRes.data.media_id) {
                    media_id = saveRes.data.media_id;
                } else {
                    Utils.showToast('保存草稿失败: ' + (saveRes.message || '未知错误'), 'error', 5000);
                    return;
                }
                
                // 调用定时发布接口
                const resp = await ApiClient.post('/api/schedule-publish', {
                    media_id: media_id,
                    publish_time: dt.replace('T', ' '),
                    draft_id: item.id,
                    enable_mass_send: enableMassSend
                });
                
                if (resp.success) {
                    const massText = enableMassSend ? '并群发' : '';
                    Utils.showToast(`已设置定时发布${massText}任务`, 'success', 4000);
                    HistoryManager.loadGenerationHistory();
                } else {
                    Utils.showToast('定时任务添加失败: ' + (resp.msg || '未知错误'), 'error', 5000);
                }
            } catch (e) {
                Utils.showToast('设置定时任务异常: ' + e.message, 'error', 5000);
            }
        };
        // 关闭时移除modal
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    static getDefaultScheduleTime() {
        // 默认定时为当前时间+10分钟
        const now = new Date(Date.now() + 10 * 60 * 1000);
        return now.toISOString().slice(0, 16);
    }
}

// 文章预览类
class ArticlePreview {
    static showPreview(article) {
        const previewElement = document.getElementById('article-preview');
        if (!previewElement) return;
        
        let previewHTML = `<h1>${article.title}</h1>`;
        
        if (article.image_url) {
            previewHTML += `<img src="${article.image_url}" alt="文章配图" style="max-width: 100%; margin-bottom: 1rem;">`;
        }
        
        if (article.digest) {
            previewHTML += `<div class="alert alert-info"><strong>摘要：</strong>${article.digest}</div>`;
        }
        
        previewHTML += article.content;
        
        previewElement.innerHTML = previewHTML;
        
        // 启用保存草稿按钮，发布按钮保持禁用状态直到草稿保存成功
        const publishBtn = document.getElementById('publish-article');
        const draftBtn = document.getElementById('save-draft');
        if (publishBtn) publishBtn.disabled = true;  // 发布按钮初始禁用
        if (draftBtn) draftBtn.disabled = false;     // 保存草稿按钮启用
        
        // 存储文章数据
        window.currentArticle = article;
    }
    
    static hidePreview() {
        const previewElement = document.getElementById('article-preview');
        if (previewElement) {
            previewElement.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-file-earmark"></i>
                    <h6>暂无预览内容</h6>
                    <p>生成文章后将在这里显示预览</p>
                </div>
            `;
        }
        
        const publishBtn = document.getElementById('publish-article');
        const draftBtn = document.getElementById('save-draft');
        if (publishBtn) publishBtn.disabled = true;
        if (draftBtn) draftBtn.disabled = true;
        
        window.currentArticle = null;
        window.currentDraftMediaId = null;  // 清除草稿media_id
    }
    
    static async saveDraft() {
        if (!window.currentArticle) {
            Utils.showToast('没有可保存的文章', 'warning');
            return;
        }
        
        try {
            this.showPublishProgress('正在保存草稿...');
            Utils.addLog(`开始保存草稿: ${window.currentArticle.title}`);
            
            // 检查当前文章内容是否包含代理图片URL
            if (window.currentArticle.content.includes('/api/proxy-image')) {
                Utils.addLog('保存草稿：使用包含代理图片URL的内容');
            } else {
                Utils.addLog('保存草稿：使用原始内容');
            }
            
            const response = await ApiClient.post('/api/save-draft', {
                article: window.currentArticle
            });
            
            if (response.success) {
                this.showPublishResult(response.data, 'success');
                Utils.showToast('草稿保存成功', 'success');
                Utils.addLog('草稿保存成功');
                
                // 存储草稿media_id，用于后续发布
                window.currentDraftMediaId = response.data.media_id;
                
                // 启用发布按钮
                const publishBtn = document.getElementById('publish-article');
                if (publishBtn) publishBtn.disabled = false;
                
                // 刷新历史记录
                HistoryManager.loadGenerationHistory();
            } else {
                this.showPublishResult(response, 'error');
                Utils.showToast('保存失败: ' + response.message, 'error');
            }
        } catch (error) {
            this.showPublishResult({ message: error.message }, 'error');
            Utils.showToast('保存草稿失败: ' + error.message, 'error');
        }
    }
    

    
    static async publishDraft() {
        if (!window.currentDraftMediaId) {
            Utils.showToast('没有可发布的草稿，请先保存草稿', 'warning');
            return;
        }
        
        try {
            this.showPublishProgress('正在发布草稿...');
            Utils.addLog(`开始发布草稿，media_id: ${window.currentDraftMediaId}`);
            
            const response = await ApiClient.post('/api/publish-draft', {
                media_id: window.currentDraftMediaId
            });
            
            if (response.success) {
                this.showPublishResult(response.data, 'success');
                Utils.showToast('草稿发布成功', 'success');
                Utils.addLog('草稿发布成功');
                
                // 检查是否勾选了群发
                const enableMassSend = document.getElementById('enable-mass-send')?.checked;
                if (enableMassSend && response.data.publish_id) {
                    Utils.showToast('正在群发给所有粉丝...', 'info');
                    Utils.addLog('开始群发给所有粉丝');
                    
                    // 调用群发接口
                    try {
                        const massResponse = await ApiClient.post('/api/mass-send', {
                            publish_id: response.data.publish_id
                        });
                        
                        if (massResponse.success) {
                            Utils.showToast('群发任务已提交，请等待群发完成', 'success');
                            Utils.addLog('群发任务提交成功');
                        } else {
                            Utils.showToast('群发失败: ' + (massResponse.message || '未知错误'), 'error');
                            Utils.addLog('群发失败: ' + massResponse.message);
                        }
                    } catch (massError) {
                        Utils.showToast('群发异常: ' + massError.message, 'error');
                        Utils.addLog('群发异常: ' + massError.message);
                    }
                }
                
                // 更新已发布统计
                const publishedElement = document.getElementById('published-articles');
                if (publishedElement) {
                    const current = parseInt(publishedElement.textContent) || 0;
                    publishedElement.textContent = current + 1;
                }
                
                // 清除草稿media_id
                window.currentDraftMediaId = null;
                
                // 刷新历史记录
                HistoryManager.loadGenerationHistory();
                HistoryManager.loadPublishHistory();
            } else {
                this.showPublishResult(response, 'error');
                Utils.showToast('发布失败: ' + response.message, 'error');
            }
        } catch (error) {
            this.showPublishResult({ message: error.message }, 'error');
            Utils.showToast('发布草稿失败: ' + error.message, 'error');
        }
    }
    
    static showPublishProgress(message) {
        const statusElement = document.getElementById('publish-status');
        const messageElement = document.getElementById('publish-message');
        
        if (statusElement) statusElement.style.display = 'block';
        if (messageElement) messageElement.textContent = message;
    }
    
    static showPublishResult(data, type) {
        const statusElement = document.getElementById('publish-status');
        if (statusElement) {
            const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
            const icon = type === 'success' ? 'bi-check-circle' : 'bi-x-circle';
            
            statusElement.innerHTML = `
                <h6><i class="bi bi-info-circle"></i> 发布结果</h6>
                <div class="alert ${alertClass}" role="alert">
                    <i class="${icon}"></i>
                    ${type === 'success' ? '发布成功' : '发布失败: ' + data.message}
                </div>
            `;
            
            setTimeout(() => {
                statusElement.style.display = 'none';
            }, 5000);
        }
    }
    
    static async refreshPreview() {
        try {
            Utils.addLog('开始刷新预览，从cache文件夹加载最新文件');
            
            const response = await ApiClient.get('/api/get-latest-cache-file');
            
            if (response.success && response.data) {
                const fileInfo = response.data;
                
                // 显示文件信息
                Utils.showToast(`已加载文件: ${fileInfo.filename} (${Utils.formatFileSize(fileInfo.size)})`, 'success');
                Utils.addLog(`成功加载文件: ${fileInfo.filename}, 大小: ${Utils.formatFileSize(fileInfo.size)}, 修改时间: ${fileInfo.modified_time}`);
                
                // 更新预览内容
                const previewElement = document.getElementById('article-preview');
                if (previewElement) {
                    // 处理微信图片防盗链问题
                    let processedContent = fileInfo.content;
                    
                    // 如果后端没有处理图片URL，前端进行处理
                    if (processedContent.includes('http://mmbiz.qpic.cn/')) {
                        processedContent = processedContent.replace(
                            /http:\/\/mmbiz\.qpic\.cn\/[^"']+/g,
                            function(match) {
                                return `/api/proxy-image?url=${encodeURIComponent(match)}`;
                            }
                        );
                        Utils.addLog('已处理微信图片URL，使用代理访问');
                    }
                    
                    previewElement.innerHTML = processedContent;
                    
                    // 更新当前文章对象的内容（包含处理后的图片URL）
                    if (window.currentArticle) {
                        window.currentArticle.content = processedContent;
                        Utils.addLog('已更新当前文章内容，包含处理后的图片URL');
                    }
                    
                    // 启用发布按钮
                    const publishBtn = document.getElementById('publish-article');
                    const saveDraftBtn = document.getElementById('save-draft');
                    if (publishBtn) publishBtn.disabled = false;
                    if (saveDraftBtn) saveDraftBtn.disabled = false;
                    
                    Utils.addLog('预览内容已更新');
                }
            } else {
                Utils.showToast(response.message || '没有找到可加载的文件', 'warning');
                Utils.addLog(`刷新预览失败: ${response.message}`, 'warning');
            }
        } catch (error) {
            Utils.showToast('刷新预览失败: ' + error.message, 'error');
            Utils.addLog(`刷新预览异常: ${error.message}`, 'error');
        }
    }
}

// 主应用类
class App {
    static _modelsAutoLoaded = false; // 标记是否已自动加载模型列表
    
    static init() {
        try {
            Utils.addLog('初始化微信公众号AI发布系统');
            this.bindEvents();
            this.loadInitialConfig();
            this.startTimeUpdate();
            this.startHistoryAutoRefresh(); // 新增：自动刷新历史记录
            this.initTooltips(); // 初始化tooltip功能
            Utils.addLog('系统初始化完成');
        } catch (error) {
            Utils.addLog('JavaScript错误: ' + error.message, 'error');
            console.error('Global error:', error);
        }
    }
    
    static bindEvents() {
        // 配置相关事件
        const saveConfigBtn = document.getElementById('save-config');
        if (saveConfigBtn) {
            saveConfigBtn.addEventListener('click', () => ConfigManager.saveConfig());
        }
        
        const testWeChatBtn = document.getElementById('test-wechat');
        if (testWeChatBtn) {
            testWeChatBtn.addEventListener('click', () => ConfigManager.testWeChatConnection());
        }
        
        const testGeminiBtn = document.getElementById('test-gemini');
        if (testGeminiBtn) {
            testGeminiBtn.addEventListener('click', () => ConfigManager.testGeminiConnection());
        }
        
        const loadGeminiModelsBtn = document.getElementById('load-gemini-models');
        if (loadGeminiModelsBtn) {
            loadGeminiModelsBtn.addEventListener('click', () => ConfigManager.loadGeminiModels());
        }
        
        const testDeepSeekBtn = document.getElementById('test-deepseek');
        if (testDeepSeekBtn) {
            testDeepSeekBtn.addEventListener('click', () => ConfigManager.testDeepSeekConnection());
        }
        
        const loadDeepSeekModelsBtn = document.getElementById('load-deepseek-models');
        if (loadDeepSeekModelsBtn) {
            loadDeepSeekModelsBtn.addEventListener('click', () => ConfigManager.loadDeepSeekModels());
        }
        
        const testDashScopeBtn = document.getElementById('test-dashscope');
        if (testDashScopeBtn) {
            testDashScopeBtn.addEventListener('click', () => ConfigManager.testDashScopeConnection());
        }
        
        const loadDashScopeModelsBtn = document.getElementById('load-dashscope-models');
        if (loadDashScopeModelsBtn) {
            loadDashScopeModelsBtn.addEventListener('click', () => {
                console.log('阿里云百炼刷新模型按钮被点击');
                Utils.addLog('阿里云百炼刷新模型按钮被点击');
                ConfigManager.loadDashScopeModels();
            });
        } else {
            console.error('阿里云百炼刷新模型按钮未找到');
            Utils.addLog('阿里云百炼刷新模型按钮未找到', 'error');
        }
        
        // 文章生成事件
        const generateBtn = document.getElementById('generate-article');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => ArticleGenerator.generateArticle());
        }
        
        // AI模型选择事件
        const aiModelSelect = document.getElementById('ai-model-select');
        if (aiModelSelect) {
            aiModelSelect.addEventListener('change', () => {
                const selectedModel = aiModelSelect.value;
                Utils.addLog(`切换到AI模型: ${selectedModel}`);
                console.log('AI模型切换:', selectedModel);
            });
        }
        
        
        // 发布相关事件
        const publishBtn = document.getElementById('publish-article');
        if (publishBtn) {
            publishBtn.addEventListener('click', () => ArticlePreview.publishDraft());
        }
        
        const saveDraftBtn = document.getElementById('save-draft');
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener('click', () => ArticlePreview.saveDraft());
        }
        
        // 刷新预览按钮事件
        const refreshPreviewBtn = document.getElementById('refresh-preview-btn');
        if (refreshPreviewBtn) {
            refreshPreviewBtn.addEventListener('click', () => ArticlePreview.refreshPreview());
        }

        // Coze JSON一键复制按钮事件（改为链接点击自动复制并跳转）
        const cozeSpaceLink = document.getElementById('coze-space-link');
        if (cozeSpaceLink) {
            cozeSpaceLink.addEventListener('click', function(e) {
                e.preventDefault();
                const json = this.getAttribute('data-json');
                if (json) {
                    // 现代浏览器优先
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(json).then(() => {
                            Utils.showToast('已复制工作流JSON到剪贴板', 'success');
                            window.open('https://www.coze.cn/space', '_blank');
                        }, () => {
                            Utils.showToast('复制失败，请手动复制', 'error');
                            window.open('https://www.coze.cn/space', '_blank');
                        });
                    } else {
                        // 兼容老浏览器
                        const temp = document.createElement('textarea');
                        temp.value = json;
                        document.body.appendChild(temp);
                        temp.select();
                        temp.setSelectionRange(0, 99999);
                        try {
                            document.execCommand('copy');
                            Utils.showToast('已复制工作流JSON到剪贴板', 'success');
                        } catch (err) {
                            Utils.showToast('复制失败，请手动复制', 'error');
                        }
                        document.body.removeChild(temp);
                        window.open('https://www.coze.cn/space', '_blank');
                    }
                }
            });
        }
        
    }
    
    static async loadInitialConfig() {
        await ConfigManager.loadConfig();
        
        // 只在项目启动时自动加载一次模型列表
        if (!this._modelsAutoLoaded) {
            Utils.addLog('项目启动，自动加载模型列表...');
            await ConfigManager.loadGeminiModels();
            await ConfigManager.loadDeepSeekModels();
            await ConfigManager.loadDashScopeModels();
            this._modelsAutoLoaded = true;
            Utils.addLog('模型列表自动加载完成，后续请手动点击刷新按钮获取最新模型');
        } else {
            Utils.addLog('模型列表已加载过，如需更新请手动点击刷新按钮');
        }
        
        // 加载历史记录
        Utils.addLog('加载历史记录...');
        await HistoryManager.loadGenerationHistory();
        await HistoryManager.loadPublishHistory();
        Utils.addLog('历史记录加载完成');
    }
    
    static startTimeUpdate() {
        Utils.updateCurrentTime();
        setInterval(() => {
            Utils.updateCurrentTime();
        }, 1000);
    }

    static startHistoryAutoRefresh() {
        setInterval(() => {
            HistoryManager.loadGenerationHistory();
            HistoryManager.loadPublishHistory();
        }, 30000); // 每30秒刷新一次
    }
    
    static initTooltips() {
        // 初始化所有tooltip
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // 监听动态添加的元素，为新的tooltip元素初始化
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // 元素节点
                        const tooltips = node.querySelectorAll ? node.querySelectorAll('[data-bs-toggle="tooltip"]') : [];
                        tooltips.forEach((tooltip) => {
                            new bootstrap.Tooltip(tooltip);
                        });
                        
                        // 如果节点本身是tooltip
                        if (node.hasAttribute && node.hasAttribute('data-bs-toggle') && node.getAttribute('data-bs-toggle') === 'tooltip') {
                            new bootstrap.Tooltip(node);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

// 新增：样式库模板选择功能
async function loadStyleTemplates() {
    try {
        const res = await fetch('/api/style-templates');
        const data = await res.json();
        if (data.success && Array.isArray(data.templates)) {
            const select = document.createElement('select');
            select.className = 'form-select';
            select.id = 'style-template-select';
            select.style.marginTop = '4px';
            // 选项：无模板、自定义、其它模板
            select.innerHTML = '<option value="">无模板（使用默认结构）</option>' +
                data.templates.map(t => `<option value="${t.id}">${t.name}</option>`).join('') +
                '<option value="custom">自定义</option>';
            // 插入到样式库模板选择区
            const selectWrapper = document.getElementById('style-template-select-wrapper');
            if (selectWrapper) selectWrapper.appendChild(select);
            // 控制自定义输入区显示/隐藏
            const customSection = document.getElementById('custom-template-section');
            const formatTextarea = document.getElementById('format-template');
            function updateCustomSection() {
                if (select.value === 'custom') {
                    customSection.style.display = '';
                    formatTextarea.value = '';
                    formatTextarea.readOnly = false;
                    formatTextarea.placeholder = '可粘贴公众号文章的<section>...</section>等完整HTML结构';
                } else if (select.value) {
                    customSection.style.display = 'none';
                    const tpl = data.templates.find(t => t.id === select.value);
                    formatTextarea.value = tpl ? tpl.content : '';
                    formatTextarea.readOnly = true;
                } else {
                    customSection.style.display = 'none';
                    formatTextarea.value = '';
                    formatTextarea.readOnly = true;
                }
            }
            select.addEventListener('change', updateCustomSection);
            // 初始化
            updateCustomSection();
        }
    } catch (e) {
        console.warn('样式库模板加载失败', e);
    }
}
document.addEventListener('DOMContentLoaded', loadStyleTemplates);

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

// 修改App.init，直接在函数体内合并下拉菜单和高级参数联动逻辑
App.init = function() {
    try {
        Utils.addLog('初始化微信公众号AI发布系统');
        this.bindEvents();
        this.loadInitialConfig();
        this.startTimeUpdate();
        this.startHistoryAutoRefresh(); // 新增：自动刷新历史记录
        this.initTooltips(); // 初始化tooltip功能
        Utils.addLog('系统初始化完成');
    } catch (error) {
        Utils.addLog('JavaScript错误: ' + error.message, 'error');
        console.error('Global error:', error);
    }
    // 生图模型选择与阿里云百炼自定义下拉菜单联动
    const imageModelSelect = document.getElementById('image-model-select');
    const dashscopeDropdown = document.getElementById('dashscope-image-model-dropdown');
    const dashscopeExtraFields = document.getElementById('dashscope-extra-fields');
    const customImagePrompt = document.getElementById('custom-image-prompt');
    if (imageModelSelect && dashscopeDropdown && dashscopeExtraFields && customImagePrompt) {
        function updateDashscopeFields() {
            if (imageModelSelect.value === 'dashscope') {
                dashscopeDropdown.style.display = '';
                dashscopeExtraFields.style.display = '';
                customImagePrompt.style.display = 'none';
            } else {
                dashscopeDropdown.style.display = 'none';
                dashscopeExtraFields.style.display = 'none';
                customImagePrompt.style.display = '';
            }
        }
        imageModelSelect.addEventListener('change', updateDashscopeFields);
        updateDashscopeFields();
    }
}