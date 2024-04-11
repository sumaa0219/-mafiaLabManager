import requests
import jsonDB


def open():
    print("doorFunc.open() called")
    data = jsonDB.read_db("lotDevice.json")
    data = data["device"]
    data["doorlock"]["status"] = True
    ip = data["doorlock"]["ip"]
    jsonDB.update_db("lotDevice.json", "device", data)
    print("http://"+ip+"/open")
    requests.get("http://"+ip+"/open")


def close():
    data = jsonDB.read_db("lotDevice.json")
    data = data["device"]
    data["doorlock"]["status"] = False
    ip = data["doorlock"]["ip"]
    jsonDB.update_db("lotDevice.json", "device", data)
    requests.get("http://"+ip+"/close")
