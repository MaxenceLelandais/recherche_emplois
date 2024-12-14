from multiprocessing import Process, Queue
import os

from map.app.FenetreGestion import FenetreGestion
from map.app.Map import Map
from map.app.API import API

class ApplicationMap:

    def __init__(self):

        self.absolute_path_html = os.path.abspath("autres/heatmap_france_factorise.html")
        self.queueApiTk = Queue()
        self.queueTkApi = Queue()
        
        self.api = API(self.queueApiTk)
        self.map = Map("Carte de recherche emplois", self.api, self.absolute_path_html,self.queueTkApi)

    def start(self):

        fenetre_gestion_process = Process(target=FenetreGestion, args=(self.queueApiTk,self.queueTkApi,))
        fenetre_gestion_process.start()
        self.map.start()


if "__main__" == __name__:

    show = ApplicationMap()
    show.start()
    