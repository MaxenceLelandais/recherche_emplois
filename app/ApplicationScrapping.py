from files.pipe.Client import Client
from scrapping.Scrapping import Scrapping
import os

class Runner:

    def __init__(self):

        self.path_run = os.path.dirname(os.path.abspath(__file__))

        self.scrapping = Scrapping()

    
    def start(self):

        self.client = Client(self.scrapping)
        self.client.connect_to_server()
        self.scrapping.setClient(self.client)

if "__main__" == __name__:

    run = Runner()
    run.start()
    
    
