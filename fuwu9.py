from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)), static_url_path='')
CORS(app)

API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
API_KEY = os.getenv("VOLC_API_KEY","")
MODEL = os.getenv("VOLC_MODEL","")
#原值：ep-20261015104416-p9p92
@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 204

    data = request.get_json(force=True, silent=True) or {}
    user_msg = data.get('content') or data.get('prompt') or 'hi'

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是大一C语言和思政知识点辅导老师，只回答大一C语言、思政相关名词解释、知识点讲解。如果用户问无关内容，请回复：我仅支持大一C语言与思政知识点答疑。回答简洁易懂，适合大学生复习。"},
            {"role": "user", "content": user_msg}
        ],
        "stream": False
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        obj = r.json()
        answer = obj["choices"][0]["message"]["content"]
        return jsonify({"content": answer})
    except Exception as e:
        return jsonify({"content": f"请求失败：{str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=False)
