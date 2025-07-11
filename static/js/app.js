/**
 * 微信公众号AI发布系统 - 前端JavaScript
 */

// 工具类
class Utils {
    static showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            Utils.createToastContainer();
        }
        
        const toast = Utils.createToast(message, type);
        document.getElementById('toast-container').appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
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
            const response = await ApiClient.post('/api/config', configData);
            
            if (response.success) {
                Utils.showToast('配置保存成功', 'success');
                Utils.addLog('配置保存成功');
            } else {
                Utils.showToast('保存失败: ' + response.message, 'error');
            }
        } catch (error) {
            Utils.showToast('保存配置失败: ' + error.message, 'error');
        }
    }
    
    static getConfigFormData() {
        return {
            wechat_appid: document.getElementById('wechat-appid')?.value || '',
            wechat_appsecret: document.getElementById('wechat-appsecret')?.value || '',
            gemini_api_key: document.getElementById('gemini-api-key')?.value || '',
            gemini_model: document.getElementById('gemini-model')?.value || 'gemini-2.5-flash',
            author: document.getElementById('author-name')?.value || 'AI笔记',
            content_source_url: document.getElementById('content-source-url')?.value || ''
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
        if (document.getElementById('author-name')) {
            document.getElementById('author-name').value = config.author || 'AI笔记';
        }
        if (document.getElementById('content-source-url')) {
            document.getElementById('content-source-url').value = config.content_source_url || '';
        }
    }
    
    static async testWeChatConnection() {
        try {
            const response = await ApiClient.post('/api/test-wechat', {});
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
            }
        } catch (error) {
            Utils.showToast('测试连接失败: ' + error.message, 'error');
        }
    }
    
    static async testGeminiConnection() {
        try {
            const response = await ApiClient.post('/api/test-gemini', {});
            const statusElement = document.getElementById('gemini-status');
            
            if (response.success) {
                Utils.showToast('Gemini连接测试成功', 'success');
                if (statusElement) {
                    statusElement.textContent = '连接正常';
                    statusElement.className = 'badge bg-success';
                }
            } else {
                Utils.showToast('Gemini连接测试失败: ' + response.message, 'error');
                if (statusElement) {
                    statusElement.textContent = '连接失败';
                    statusElement.className = 'badge bg-danger';
                }
            }
        } catch (error) {
            Utils.showToast('测试连接失败: ' + error.message, 'error');
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
        
        try {
            this.showGenerationProgress();
            Utils.addLog(`开始生成文章: ${title}`);
            
            const response = await ApiClient.post('/api/generate-article', { title });
            
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
            this.updateProgress(0, '开始生成...');
            
            // 模拟进度更新
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 90) {
                    clearInterval(interval);
                    this.updateProgress(90, '即将完成...');
                } else {
                    this.updateProgress(progress, '正在生成内容...');
                }
            }, 500);
        }
    }
    
    static hideGenerationProgress() {
        const progressElement = document.getElementById('generation-progress');
        if (progressElement) {
            this.updateProgress(100, '生成完成');
            setTimeout(() => {
                progressElement.style.display = 'none';
            }, 1000);
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
        // 更新历史记录
        const historyList = document.getElementById('history-list');
        if (historyList) {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <h6>${data.title}</h6>
                <p>生成时间: ${data.generated_at} | 长度: ${data.content_length}字</p>
            `;
            
            // 移除空状态
            const emptyState = historyList.querySelector('.empty-state');
            if (emptyState) {
                emptyState.remove();
            }
            
            historyList.insertBefore(historyItem, historyList.firstChild);
        }
        
        // 更新统计
        const totalElement = document.getElementById('total-articles');
        if (totalElement) {
            const current = parseInt(totalElement.textContent) || 0;
            totalElement.textContent = current + 1;
        }
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
        
        // 启用发布按钮
        const publishBtn = document.getElementById('publish-article');
        const draftBtn = document.getElementById('save-draft');
        if (publishBtn) publishBtn.disabled = false;
        if (draftBtn) draftBtn.disabled = false;
        
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
    }
    
    static async publishArticle() {
        if (!window.currentArticle) {
            Utils.showToast('没有可发布的文章', 'warning');
            return;
        }
        
        try {
            this.showPublishProgress('正在发布到微信公众号...');
            Utils.addLog(`开始发布文章: ${window.currentArticle.title}`);
            
            const response = await ApiClient.post('/api/publish-article', {
                article: window.currentArticle
            });
            
            if (response.success) {
                this.showPublishResult(response.data, 'success');
                Utils.showToast('文章发布成功', 'success');
                Utils.addLog('文章发布成功');
                
                // 更新已发布统计
                const publishedElement = document.getElementById('published-articles');
                if (publishedElement) {
                    const current = parseInt(publishedElement.textContent) || 0;
                    publishedElement.textContent = current + 1;
                }
            } else {
                this.showPublishResult(response, 'error');
                Utils.showToast('发布失败: ' + response.message, 'error');
            }
        } catch (error) {
            this.showPublishResult({ message: error.message }, 'error');
            Utils.showToast('发布文章失败: ' + error.message, 'error');
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
}

// 主应用类
class App {
    static init() {
        try {
            Utils.addLog('初始化微信公众号AI发布系统');
            this.bindEvents();
            this.loadInitialConfig();
            this.startTimeUpdate();
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
        
        // 文章生成事件
        const generateBtn = document.getElementById('generate-article');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => ArticleGenerator.generateArticle());
        }
        
        // 发布相关事件
        const publishBtn = document.getElementById('publish-article');
        if (publishBtn) {
            publishBtn.addEventListener('click', () => ArticlePreview.publishArticle());
        }
        
        // 表单回车事件
        const titleInput = document.getElementById('article-title');
        if (titleInput) {
            titleInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    ArticleGenerator.generateArticle();
                }
            });
        }
    }
    
    static async loadInitialConfig() {
        await ConfigManager.loadConfig();
    }
    
    static startTimeUpdate() {
        Utils.updateCurrentTime();
        setInterval(() => {
            Utils.updateCurrentTime();
        }, 1000);
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}