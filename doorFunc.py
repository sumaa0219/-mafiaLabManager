import requests
import jsonDB


def open():
    data = jsonDB.read_db("lotDevice.json")
    data = data["device"]
    data["doorlock"]["status"] = True
    ip = data["doorlock"]["ip"]
    jsonDB.update_db("lotDevice.json", "device", data)
    print("http://"+str(ip)+"/open")
    requests.get("http://"+ip+"/open")


def close():
    data = jsonDB.read_db("lotDevice.json")
    data = data["device"]
    data["doorlock"]["status"] = False
    ip = data["doorlock"]["ip"]
    jsonDB.update_db("lotDevice.json", "device", data)
    requests.get("http://"+str(ip)+"/close")
