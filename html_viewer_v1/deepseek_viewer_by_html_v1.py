"""
1st version of DeepSeek Chat Viewer in HTML format
This script generates an HTML file to view chat records from a JSON file.
It includes a sidebar for conversation selection and a main area for displaying messages.
The messages are displayed with user and AI messages styled differently, and reasoning content is also shown if available.
"""
import json
from pathlib import Path
from datetime import datetime

def generate_chat_viewer(json_data, output_file="chat_viewer.html"):
    """
    生成聊天记录查看器的HTML文件
    
    参数:
        json_data: 包含聊天记录的JSON数据
        output_file: 输出HTML文件名
    """
    # HTML模板
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>聊天记录查看器</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                height: 100vh;
                background-color: #f5f5f5;
            }
            .sidebar {
                width: 300px;
                background-color: #2c3e50;
                color: white;
                overflow-y: auto;
                padding: 20px 0;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            }
            .sidebar-header {
                padding: 0 20px 20px;
                border-bottom: 1px solid #34495e;
            }
            .sidebar-header h2 {
                margin: 0;
                font-size: 1.5em;
            }
            .conversation-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .conversation-item {
                padding: 15px 20px;
                border-bottom: 1px solid #34495e;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .conversation-item:hover {
                background-color: #34495e;
            }
            .conversation-item.active {
                background-color: #3498db;
            }
            .conversation-title {
                font-weight: bold;
                margin-bottom: 5px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .conversation-date {
                font-size: 0.8em;
                color: #bdc3c7;
            }
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .chat-header {
                padding: 20px;
                background-color: #3498db;
                color: white;
                font-size: 1.2em;
                font-weight: bold;
            }
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background-color: #ecf0f1;
            }
            .message {
                margin-bottom: 15px;
                max-width: 80%;
            }
            .user-message {
                margin-left: auto;
                background-color: #3498db;
                color: white;
                border-radius: 18px 18px 0 18px;
                padding: 12px 16px;
            }
            .ai-message {
                margin-right: auto;
                background-color: white;
                border-radius: 18px 18px 18px 0;
                padding: 12px 16px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .message-sender {
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 0.9em;
            }
            .user-sender {
                text-align: right;
                color: #3498db;
            }
            .ai-sender {
                text-align: left;
                color: #2c3e50;
            }
            .message-content {
                line-height: 1.5;
                white-space: pre-wrap;
            }
            .empty-state {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                color: #7f8c8d;
                font-size: 1.2em;
            }
            .reasoning-content {
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 10px;
                margin-top: 10px;
                font-size: 0.9em;
                color: #555;
                border-radius: 0 0 0 4px;
            }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>对话列表</h2>
            </div>
            <ul class="conversation-list" id="conversationList"></ul>
        </div>
        <div class="chat-container">
            <div class="chat-header" id="chatHeader">
                请从左侧选择对话
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">选择对话以查看内容</div>
            </div>
        </div>

        <script>
            const conversations = ${conversations_json};
            
            // 渲染对话列表
            const conversationList = document.getElementById('conversationList');
            const chatHeader = document.getElementById('chatHeader');
            const chatMessages = document.getElementById('chatMessages');
            
            conversations.forEach((conversation, index) => {
                const li = document.createElement('li');
                li.className = 'conversation-item';
                li.dataset.index = index;
                
                const titleDiv = document.createElement('div');
                titleDiv.className = 'conversation-title';
                titleDiv.textContent = conversation.title || '无标题对话';
                
                const dateDiv = document.createElement('div');
                dateDiv.className = 'conversation-date';
                
                try {
                    const date = new Date(conversation.inserted_at || conversation.updated_at);
                    dateDiv.textContent = date.toLocaleString('zh-CN');
                } catch (e) {
                    dateDiv.textContent = '未知日期';
                }
                
                li.appendChild(titleDiv);
                li.appendChild(dateDiv);
                
                li.addEventListener('click', () => {
                    // 移除所有active类
                    document.querySelectorAll('.conversation-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    
                    // 添加active类到当前项
                    li.classList.add('active');
                    
                    // 加载对话内容
                    loadConversation(conversation);
                });
                
                conversationList.appendChild(li);
            });
            
            // 加载对话内容
            function loadConversation(conversation) {
                chatHeader.textContent = conversation.title || '无标题对话';
                chatMessages.innerHTML = '';
                
                if (!conversation.mapping) {
                    chatMessages.innerHTML = '<div class="empty-state">此对话没有内容</div>';
                    return;
                }
                
                // 找到根节点
                const rootNode = conversation.mapping.root;
                if (!rootNode || !rootNode.children) {
                    chatMessages.innerHTML = '<div class="empty-state">此对话没有内容</div>';
                    return;
                }
                
                // 按顺序遍历对话
                let currentNodeId = rootNode.children[0];
                while (currentNodeId) {
                    const node = conversation.mapping[currentNodeId];
                    if (!node || !node.message) {
                        if (node && node.children && node.children.length > 0) {
                            currentNodeId = node.children[0];
                        } else {
                            break;
                        }
                        continue;
                    }
                    
                    const message = node.message;
                    const isUser = currentNodeId% 2 === 1;  // 假设奇数ID为用户消息，偶数ID为AI消息
                    
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
                    
                    const senderDiv = document.createElement('div');
                    senderDiv.className = `message-sender ${isUser ? 'user-sender' : 'ai-sender'}`;
                    senderDiv.textContent = isUser ? '用户' : 'AI助手';
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    contentDiv.textContent = message.content || '[无内容]';
                    
                    messageDiv.appendChild(senderDiv);
                    messageDiv.appendChild(contentDiv);
                    
                    // 如果有推理内容，也显示出来
                    if (message.reasoning_content) {
                        const reasoningDiv = document.createElement('div');
                        reasoningDiv.className = 'reasoning-content';
                        reasoningDiv.textContent = message.reasoning_content;
                        messageDiv.appendChild(reasoningDiv);
                    }
                    
                    chatMessages.appendChild(messageDiv);
                    
                    // 移动到下一个节点
                    if (node.children && node.children.length > 0) {
                        currentNodeId = node.children[0];
                    } else {
                        break;
                    }
                }
                
                // 如果没有消息，显示空状态
                if (chatMessages.children.length === 0) {
                    chatMessages.innerHTML = '<div class="empty-state">此对话没有有效内容</div>';
                } else {
                    // 滚动到底部
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            }
            
            // 默认选中第一个对话
            if (conversations.length > 0) {
                document.querySelector('.conversation-item').click();
            }
        </script>
    </body>
    </html>
    """

    # 准备数据
    conversations = []
    for conv in json_data:
        # 提取对话基本信息
        conversation = {
            "id": conv.get("id", ""),
            "title": conv.get("title", "无标题对话"),
            "inserted_at": conv.get("inserted_at", ""),
            "updated_at": conv.get("updated_at", ""),
            "mapping": conv.get("mapping", {})
        }
        conversations.append(conversation)

    # 将对话数据转换为JSON字符串，用于JavaScript
    conversations_json = json.dumps(conversations, ensure_ascii=False, indent=2)

    # 替换模板中的占位符
    html_content = html_template.replace("${conversations_json}", conversations_json)

    # 写入HTML文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已生成聊天查看器: {Path(output_file).resolve()}")

# 示例使用
if __name__ == "__main__":
    # 示例数据（实际使用时应从JSON文件加载）
    sample_data = None
    with open("./conversations.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    generate_chat_viewer(sample_data)