import json
import threading
import time
import os

pause = False
file_path = 'data.json'
def add_task(dicts):
    if os.path.exists(file_path):
        jsonFile = open("data.json","r")
        jsonData = json.load(jsonFile)
        jsonFile.close()
        for value in dicts:
            jsonData[value] = dicts[value]
        jsonString = json.dumps(jsonData)
        jsonFile = open("data.json","w")
        jsonFile.write(jsonString)
        jsonFile.close()

def remove_task(list_names):
    jsonFile = open("data.json","r")
    dicts = json.load(jsonFile)
    for name in list_names:
        del dicts[name]
    jsonString = json.dumps(dicts)
    jsonFile.close()
    jsonFile = open("data.json","w")
    jsonFile.write(jsonString)
    jsonFile.close()

def load_task():
    if os.path.exists(file_path):
        jsonFile = open("data.json","r")
        dicts = json.load(jsonFile)
        return dicts
    else:
        jsonFile = open("data.json","w")
        dicts = {"example task":{"completed":False,"timer":0}}
        jsonData = json.dumps(dicts)
        jsonFile.write(jsonData)
        jsonFile.close()

def set_timer_task(hr,min,sec):
    seconds = hr*3600 + min * 60 + sec
    return seconds