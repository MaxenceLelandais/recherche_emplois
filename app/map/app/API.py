import json

class API:

    def __init__(self, queueApiTk):

        self.queueApiTk = queueApiTk

    def on_marker_click(self, data):
        
        result = {
            "type" : "selection",
            "data" : data
        }
        self.queueApiTk.put(json.dumps(result)) 

