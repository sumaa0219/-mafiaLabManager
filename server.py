from flask import Flask, render_template, request, redirect, Blueprint, jsonify
import jsonDB
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='.', static_url_path='')
memberJson = "memberStatus.json"
iotJson = "lotDevice.json"
CORS(app)  # CORSを適用


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route("/check", methods=['GET'])
def check():
    return 'OK', 200


@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()  # リクエストボディからJSONデータを取得
    jsonDB.update_db(memberJson, "member", data)  # データをJSONファイルに書き込む
    return 'OK', 200


@app.route("/restartBOT", methods=['GET'])
def restartBOT():
    os.system("sudo systemctl restart discordbot.service")
    return 'OK', 200


@app.route("/resisterIP", methods=['POST'])
def resisterIP():
    data = request.get_json()
    jsonDB.update_db(iotJson, "device", data)
    return 'OK', 200


@app.route("/getIotData", methods=['GET'])
def getIotData():
    data = jsonDB.read_db(iotJson)
    return jsonify(data), 200


app.run(host="0.0.0.0", port=8000, debug=False)
