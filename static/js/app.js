// 全局变量
let currentArticle = null;
let logEntries = [];

// 工具函数
class Utils {
    static showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);
        
        // 显示toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // 自动移除
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    static createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    static createToast(message, type) {
        const iconMap = {
            success: 'check-circle-fill',
            error: 'exclamation-triangle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill'
        };
        
        const colorMap = {
            success: 'text-success',
            error: 'text-danger',
            warning: 'text-warning',
            info: 'text-info'
        };
        
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-header">
                <i class="bi bi-${iconMap[type]} ${colorMap[type]} me-2"></i>
                <strong class="me-auto">系统通知</strong>
                <small>${new Date().toLocaleTimeString()}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        return toast;
    }
    
    static addLog(message, level = 'info') {
        const timestamp = new Date().toLocaleString();
        const logEntry = {
            timestamp,
            level,
            message
        };
        
        logEntries.unshift(logEntry);
        
        // 限制日志条数
        if (logEntries.length > 100) {
            logEntries = logEntries.slice(0, 100);
        }
        
        console.log(`[${timestamp}] ${level.toUpperCase()}: ${message}`);
        this.updateLogDisplay();
    }
    
    static updateLogDisplay() {
        const logContent = document.getElementById('log-content');
        if (!logContent) return;
        
        if (logEntries.length === 0) {
            logContent.innerHTML = '<div class="text-muted">暂无日志</div>';
            return;
        }
        
        const logHtml = logEntries.map(entry => `
            <div class="log-entry">
                <span class="log-time">[${entry.timestamp}]</span>
                <span class="log-level-${entry.level}">${entry.level.toUpperCase()}:</span>
                <span class="log-message">${entry.message}</span>
            </div>
        `).join('');
        
        logContent.innerHTML = logHtml;
    }
    
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    static updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleString();
        }
    }
}

// API请求类
class ApiClient {
    static async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
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
            body: JSON.stringify(data)
        });
    }
}

// 配置管理
class ConfigManager {
    static async loadConfig() {
        try {
            Utils.addLog('开始加载配置', 'info');
            const response = await ApiClient.get('/api/config');
            
            if (response.success) {
                const config = response.data;
                this.fillConfigForm(config);
                Utils.addLog('配置加载成功', 'success');
                Utils.showToast('配置加载成功', 'success');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            Utils.addLog(`配置加载失败: ${error.message}`, 'error');
            Utils.showToast(`配置加载失败: ${error.message}`, 'error');
        }
    }
    
    static async saveConfig() {
        try {
            const formData = this.getConfigFormData();
            
            // 验证必填字段
            const requiredFields = {
                'wechat_appid': '微信AppID',
                'wechat_appsecret': '微信AppSecret',
                'gemini_api_key': 'Gemini API密钥'
            };
            
            for (const [field, label] of Object.entries(requiredFields)) {
                if (!formData[field] || formData[field].trim() === '') {
                    throw new Error(`请填写${label}`);
                }
            }
            
            Utils.addLog('开始保存配置', 'info');
            const response = await ApiClient.post('/api/config', formData);
            
            if (response.success) {
                Utils.addLog('配置保存成功', 'success');
                Utils.showToast('配置保存成功', 'success');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            Utils.addLog(`配置保存失败: ${error.message}`, 'error');
            Utils.showToast(`配置保存失败: ${error.message}`, 'error');
        }
    }
    
    static getConfigFormData() {
        const form = document.getElementById('config-form');
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value.trim();
        }
        
        return data;
    }
    
    static fillConfigForm(config) {
        const form = document.getElementById('config-form');
        
        for (const [key, value] of Object.entries(config)) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value || '';
            }
        }
    }
    
    static async testWeChatConnection() {
        try {
            const btn = document.getElementById('test-wechat-btn');
            const originalText = btn.innerHTML;
            
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> 测试中...';
            
            Utils.addLog('开始测试微信API连接', 'info');
            const response = await ApiClient.post('/api/test-wechat', {});
            
            if (response.success) {
                Utils.addLog('微信API连接测试成功', 'success');
                Utils.showToast('微信API连接成功', 'success');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            Utils.addLog(`微信API连接测试失败: ${error.message}`, 'error');
            Utils.showToast(`微信API连接测试失败: ${error.message}`, 'error');
        } finally {
            const btn = document.getElementById('test-wechat-btn');
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle"></i> 测试微信连接';
        }
    }
    
    static async testGeminiConnection() {
        try {
            const btn = document.getElementById('test-gemini-btn');
            const originalText = btn.innerHTML;
            
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> 测试中...';
            
            Utils.addLog('开始测试Gemini AI连接', 'info');
            const response = await ApiClient.post('/api/test-gemini', {});
            
            if (response.success) {
                Utils.addLog('Gemini AI连接测试成功', 'success');
                Utils.showToast('Gemini AI连接成功', 'success');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            Utils.addLog(`Gemini AI连接测试失败: ${error.message}`, 'error');
            Utils.showToast(`Gemini AI连接测试失败: ${error.message}`, 'error');
        } finally {
            const btn = document.getElementById('test-gemini-btn');
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle"></i> 测试AI连接';
        }
    }
}

// 文章生成管理
class ArticleGenerator {
    static async generateArticle() {
        try {
            const titleInput = document.getElementById('article-title');
            const title = titleInput.value.trim();
            
            if (!title) {
                Utils.showToast('请输入文章标题', 'warning');
                titleInput.focus();
                return;
            }
            
            const btn = document.getElementById('generate-btn');
            const originalText = btn.innerHTML;
            
            // 显示进度
            this.showGenerationProgress();
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> 生成中...';
            
            Utils.addLog(`开始生成文章: ${title}`, 'info');
            
            // 更新进度
            this.updateProgress(20, '准备生成内容...');
            
            const response = await ApiClient.post('/api/generate-article', { title });
            
            if (response.success) {
                this.updateProgress(100, '生成完成');
                
                currentArticle = response.data;
                this.showGenerationResult(response.data);
                this.hideGenerationProgress();
                
                Utils.addLog('文章生成成功', 'success');
                Utils.showToast('文章生成成功', 'success');
                
                // 自动切换到预览
                setTimeout(() => {
                    ArticlePreview.showPreview(response.data);
                }, 1000);
                
            } else {
                throw new Error(response.message);
            }
            
        } catch (error) {
            this.hideGenerationProgress();
            Utils.addLog(`文章生成失败: ${error.message}`, 'error');
            Utils.showToast(`文章生成失败: ${error.message}`, 'error');
        } finally {
            const btn = document.getElementById('generate-btn');
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-magic"></i> 生成文章';
        }
    }
    
    static showGenerationProgress() {
        document.getElementById('generation-result').classList.add('d-none');
        document.getElementById('generation-progress').classList.remove('d-none');
        this.updateProgress(0, '准备开始生成...');
    }
    
    static hideGenerationProgress() {
        document.getElementById('generation-progress').classList.add('d-none');
    }
    
    static updateProgress(percent, text) {
        const progressBar = document.querySelector('#generation-progress .progress-bar');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }
        
        if (progressText) {
            progressText.textContent = text;
        }
    }
    
    static showGenerationResult(data) {
        const resultDiv = document.getElementById('generation-result');
        
        document.getElementById('result-title').textContent = data.title;
        document.getElementById('result-digest').textContent = data.digest || '无摘要';
        document.getElementById('result-time').textContent = data.generated_at;
        
        const imageStatus = document.getElementById('result-image-status');
        if (data.image_url) {
            imageStatus.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> 已生成</span>';
        } else {
            imageStatus.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-triangle"></i> 未生成</span>';
        }
        
        resultDiv.classList.remove('d-none');
    }
}

// 文章预览管理
class ArticlePreview {
    static showPreview(article) {
        if (!article) {
            this.hidePreview();
            return;
        }
        
        // 隐藏空状态
        document.getElementById('empty-preview').classList.add('d-none');
        
        // 显示预览
        const previewDiv = document.getElementById('article-preview');
        previewDiv.classList.remove('d-none');
        
        // 填充内容
        document.getElementById('preview-title').textContent = article.title;
        document.getElementById('preview-digest').textContent = article.digest || '';
        document.getElementById('preview-content').innerHTML = article.content || '';
        
        // 设置作者
        const authorSpan = document.getElementById('preview-author');
        const authorInput = document.getElementById('author');
        authorSpan.textContent = authorInput.value || 'AI笔记';
        
        // 处理配图
        const imageContainer = document.getElementById('preview-image-container');
        const previewImage = document.getElementById('preview-image');
        
        if (article.image_url) {
            previewImage.src = article.image_url;
            imageContainer.classList.remove('d-none');
        } else {
            imageContainer.classList.add('d-none');
        }
        
        Utils.addLog('文章预览已更新', 'info');
    }
    
    static hidePreview() {
        document.getElementById('article-preview').classList.add('d-none');
        document.getElementById('empty-preview').classList.remove('d-none');
    }
    
    static async publishArticle() {
        if (!currentArticle) {
            Utils.showToast('没有可发布的文章', 'warning');
            return;
        }
        
        try {
            const btn = document.getElementById('publish-btn');
            const originalText = btn.innerHTML;
            
            // 显示发布进度
            this.showPublishProgress('正在发布到微信公众号...');
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> 发布中...';
            
            Utils.addLog('开始发布文章到微信公众号', 'info');
            
            const response = await ApiClient.post('/api/publish-article', { 
                article: currentArticle 
            });
            
            if (response.success) {
                this.showPublishResult(response.data, 'success');
                Utils.addLog('文章发布成功', 'success');
                Utils.showToast('文章发布成功', 'success');
            } else {
                throw new Error(response.message);
            }
            
        } catch (error) {
            this.showPublishResult({ error: error.message }, 'error');
            Utils.addLog(`文章发布失败: ${error.message}`, 'error');
            Utils.showToast(`文章发布失败: ${error.message}`, 'error');
        } finally {
            const btn = document.getElementById('publish-btn');
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-send-fill"></i> 发布到微信公众号';
        }
    }
    
    static showPublishProgress(message) {
        const statusDiv = document.getElementById('publish-status');
        const progressDiv = document.getElementById('publish-progress');
        const progressText = document.getElementById('publish-progress-text');
        
        statusDiv.classList.remove('d-none');
        progressDiv.classList.remove('d-none');
        progressText.textContent = message;
        
        document.getElementById('publish-result').innerHTML = '';
    }
    
    static showPublishResult(data, type) {
        const progressDiv = document.getElementById('publish-progress');
        const resultDiv = document.getElementById('publish-result');
        
        progressDiv.classList.add('d-none');
        
        if (type === 'success') {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="bi bi-check-circle"></i> 发布成功</h6>
                    <p class="mb-1">文章已成功发布到微信公众号</p>
                    ${data.publish_id ? `<small>发布ID: ${data.publish_id}</small>` : ''}
                    ${data.msg_data_id ? `<br><small>消息ID: ${data.msg_data_id}</small>` : ''}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="bi bi-exclamation-triangle"></i> 发布失败</h6>
                    <p class="mb-0">${data.error || '发布过程中发生未知错误'}</p>
                </div>
            `;
        }
    }
}

// 主应用类
class App {
    static init() {
        this.bindEvents();
        this.loadInitialConfig();
        this.startTimeUpdate();
        Utils.addLog('应用初始化完成', 'info');
    }
    
    static bindEvents() {
        // 配置表单事件
        document.getElementById('config-form').addEventListener('submit', (e) => {
            e.preventDefault();
            ConfigManager.saveConfig();
        });
        
        document.getElementById('load-config-btn').addEventListener('click', () => {
            ConfigManager.loadConfig();
        });
        
        document.getElementById('test-wechat-btn').addEventListener('click', () => {
            ConfigManager.testWeChatConnection();
        });
        
        document.getElementById('test-gemini-btn').addEventListener('click', () => {
            ConfigManager.testGeminiConnection();
        });
        
        // 文章生成事件
        document.getElementById('generate-form').addEventListener('submit', (e) => {
            e.preventDefault();
            ArticleGenerator.generateArticle();
        });
        
        document.getElementById('preview-article-btn').addEventListener('click', () => {
            if (currentArticle) {
                ArticlePreview.showPreview(currentArticle);
            }
        });
        
        // 发布事件
        document.getElementById('publish-btn').addEventListener('click', () => {
            ArticlePreview.publishArticle();
        });
        
        // 日志清空事件
        document.getElementById('clear-log-btn').addEventListener('click', () => {
            logEntries = [];
            Utils.updateLogDisplay();
            Utils.showToast('日志已清空', 'info');
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // Ctrl + Enter 快速生成文章
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                const titleInput = document.getElementById('article-title');
                if (titleInput.value.trim()) {
                    ArticleGenerator.generateArticle();
                }
            }
        });
    }
    
    static loadInitialConfig() {
        ConfigManager.loadConfig();
    }
    
    static startTimeUpdate() {
        Utils.updateCurrentTime();
        setInterval(() => {
            Utils.updateCurrentTime();
        }, 1000);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// 全局错误处理
window.addEventListener('error', (e) => {
    Utils.addLog(`JavaScript错误: ${e.message}`, 'error');
    console.error('Global error:', e);
});

window.addEventListener('unhandledrejection', (e) => {
    Utils.addLog(`未处理的Promise错误: ${e.reason}`, 'error');
    console.error('Unhandled promise rejection:', e);
});
