import json
import time
from threading import Thread

class FenetreGestion:

    def __init__(self, queueApiTk,queueTkApi):
                
        self.queueApiTk = queueApiTk
        self.queueTkApi = queueTkApi
        Thread(target=self.loopGetMsgQueueTk).start()
    
        self.start()

    def maj_location(self, data):
        time.sleep(3)

        result = {
            "type" : "locations",
            "data" : data
        }
        self.queueTkApi.put(json.dumps(result))

    def start(self):

        # Initialisation des coordonnées
        locations = [
            {"coords": [46.36634, 6.46545], "popup": "Vivaservices, Thonon-les-Bains, ARA, FR", "tooltip": "Vivaservices, Thonon-les-Bains, ARA, FR"},
            {"coords": [45.52326, 4.87579], "popup": "Vivaservices, Siège social : 49/55 rue Victor Hugo 38200 VIENNE", "tooltip": "Vivaservices, Siège social : 49/55 rue Victor Hugo 38200 VIENNE"},
            # ... autres coordonnées
        ]

        self.maj_location(locations)

    def recuperationInfoSelectionnee(self, selection):
        print(selection)

    def loopGetMsgQueueTk(self):

        while True:
            if not self.queueApiTk.empty():
                json_message = self.queueApiTk.get() 
                message = json.loads(json_message)
                
                if message.get("type") == "selection":
                    self.recuperationInfoSelectionnee(message.get("data"))
            else:
                time.sleep(1) 