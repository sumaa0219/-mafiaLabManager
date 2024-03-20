from flask import Flask, render_template, request, redirect, Blueprint, jsonify
import jsonDB
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
memberJson = "memberStatus.json"
CORS(app)  # CORSを適用


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()  # リクエストボディからJSONデータを取得
    jsonDB.update_db(memberJson, "member", data)  # データをJSONファイルに書き込む
    return 'OK', 200


app.run(host="0.0.0.0",port=8000, debug=False)
