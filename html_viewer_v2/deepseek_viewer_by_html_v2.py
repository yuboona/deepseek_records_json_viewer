"""DeepSeek Viewer by HTML V2
This script provides a web interface to view DeepSeek chat conversations.
It loads conversation data from a JSON file, processes it, and renders it using Flask and Jinja2 templates.
NOTE:template.html should be created in the templates directory with appropriate HTML structure, because Flask will defautly look for it there.
   You can change  the default template directory by setting the `template_folder` parameter in the Flask app initialization. Flask(__name__, template_folder='your_template_directory')
"""
import json
from flask import Flask, render_template
from markdown import markdown
from pathlib import Path

app = Flask(__name__)

def load_chat_data(file_path):
    """加载JSON聊天数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_chat_data(chat_data):
    """处理聊天数据，提取对话信息"""
    processed = []
    for conversation in chat_data:
        # 提取对话基本信息
        conv_info = {
            'id': conversation['id'],
            'title': conversation['title'],
            'inserted_at': conversation['inserted_at'],
            'messages': []
        }
        
        # 提取对话消息
        current_node = conversation['mapping']['root']
        while current_node['children']:
            child_id = current_node['children'][0]
            child_node = conversation['mapping'][child_id]
            
            if child_node['message']:
                message = child_node['message']
                message['id'] = int(child_id)  # 将ID转为整数用于判断说话人
                message['is_user'] = message['id'] % 2 == 1  # 奇数ID是用户
                message['content_html'] = markdown(message['content']) if message['content'] else ""
                conv_info['messages'].append(message)
            
            current_node = child_node
        
        processed.append(conv_info)
    
    return processed

@app.route('/')
def index():
    # 假设聊天数据文件在当前目录下的"chat_data.json"
    file_path = Path(__file__).parent / '../conversations.json'
    chat_data = load_chat_data(file_path)
    processed_data = process_chat_data(chat_data)
    return render_template('template.html', conversations=processed_data)

if __name__ == '__main__':
    app.run(debug=True)