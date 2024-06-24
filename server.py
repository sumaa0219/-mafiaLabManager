from flask import Flask, render_template, request, redirect, Blueprint, jsonify, render_template_string, flash, url_for
import jsonDB
from flask_cors import CORS
import os
import cups

app = Flask(__name__, static_folder='.', static_url_path='')
memberJson = "memberStatus.json"
iotJson = "lotDevice.json"
CORS(app)  # CORSを適用

UPLOAD_FOLDER = "printFile"
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mainPrinter = "LP_S7160"


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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def print_pdf(printer_name, pdf_path, duplex=True):
    conn = cups.Connection()
    printers = conn.getPrinters()
    if printer_name not in printers:
        raise ValueError(f"プリンター '{printer_name}' が見つかりません")

    options = {
        'media': 'A4',
        'fit-to-page': 'true'
    }
    if duplex:
        options['sides'] = 'two-sided-long-edge'

    job_id = conn.printFile(printer_name, pdf_path, "Flask Print Job", options)
    return job_id


@app.route('/printer', methods=['GET'])
def printer_form():
    return render_template_string('''
    <!doctype html>
    <title>Upload PDF for Printing</title>
    <h1>Upload PDF File for Printing</h1>
    <form action="{{ url_for('print_file') }}" method=post enctype=multipart/form-data>
      <input type=file name=file>
      <label for="duplex">両面印刷:</label>
      <select name="duplex">
        <option value="false">しない</option>
        <option value="true">する</option>
      </select>
      <input type=submit value=Upload>
    </form>
    ''')


@app.route('/print', methods=['POST'])
def print_file():
    if 'file' not in request.files:
        return redirect(url_for('printer_form'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('printer_form'))

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        duplex = request.form.get('duplex', 'true').lower() == 'true'
        printer_name = mainPrinter

        try:
            # print_pdf(printer_name, file_path, duplex)
            pass
        except Exception as e:
            return f'Printing failed: {e}', 500

        return 'File successfully printed', 200


app.run(host="0.0.0.0", port=8000, debug=False)
