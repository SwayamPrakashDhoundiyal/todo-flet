import json
import sys as system
import os
import pathlib

class DataClass:
    def __init__(self):
        self.file_path = 'asstits/data.json'
    
    def resource_path(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller onefile """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = system._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def make_dir(self):
        import ctypes.wintypes
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        dir = buf.value + '\\assets'
        if not os.path.exists(dir):
            os.mkdir(dir)
            self.file_path = os.path.join(dir,'data.json')
            return True
        else:
            self.file_path = os.path.join(dir,'data.json')
            return False

    def add_task(self,dicts):
        if os.path.exists(self.file_path):
            jsonFile = open(self.file_path,"r")
            jsonData = json.load(jsonFile)
            jsonFile.close()
            for value in dicts:
                jsonData[value] = dicts[value]
            jsonString = json.dumps(jsonData)
            jsonFile = open(self.file_path,"w")
            jsonFile.write(jsonString)
            jsonFile.close()

    def remove_task(self,list_names):
        jsonFile = open(self.file_path,"r")
        dicts = json.load(jsonFile)
        for name in list_names:
            del dicts[name]
        jsonString = json.dumps(dicts)
        jsonFile.close()
        jsonFile = open(self.file_path,"w")
        jsonFile.write(jsonString)
        jsonFile.close()

    def load_task(self):
        if os.path.exists(self.file_path):
            jsonFile = open(self.file_path,"r")
            dicts = json.load(jsonFile)
            return dicts
        else:
            if self.make_dir():
                jsonFile = open(self.file_path,"w")
                dicts = {"example task":{"completed":False,"timer":0}}
                jsonData = json.dumps(dicts)
                jsonFile.write(jsonData)
                jsonFile.close()
                
            return self.load_task() 

    def set_timer_task(self,hr,min,sec):
        seconds = hr*3600 + min * 60 + sec
        return seconds