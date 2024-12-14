import json
from threading import Thread
import time
import webview

class Map:

    def __init__(self, name, api, absolute_path_html, queueTkApi):
        self.name = name
        self.api = api
        self.queueTkApi = queueTkApi
        self.absolute_path_html = absolute_path_html
        
        Thread(target=self.loopGetMsgQueueTk, daemon=True).start()

    def start(self):
        
        self.webview_window = webview.create_window(self.name, self.absolute_path_html, js_api=self.api)
        webview.start()

    def mettre_a_jour_carte(self, absolute_path_html):
        if hasattr(self, 'webview_window'):
            self.webview_window.load_url(absolute_path_html)
    
    
    def update_map(self, updated_locations):
        self.webview_window.evaluate_js(f"updateLocations({json.dumps(updated_locations)})")

    def loopGetMsgQueueTk(self):

        while True:
            if not self.queueTkApi.empty():
                json_message = self.queueTkApi.get() 
                message = json.loads(json_message)
                
                if message.get("type") == "locations":
                    self.update_map(message.get("data"))
            else:
                time.sleep(1) 
