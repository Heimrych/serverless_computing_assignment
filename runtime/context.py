import os
from datetime import datetime as dt

class Context(object):
    def __init__(self, host='localhost', port=6379, input_key=None, output_key=None):
        self.host = host
        self.port = port
        self.input_key = input_key
        self.output_key = output_key
        timestamp = os.path.getmtime("/opt/custom_module.py")
        self.function_getmtime = dt.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.last_execution = None
        self.env = {}

    def set_last_execution(self):
        self.last_execution = datetime.datetime.now()
