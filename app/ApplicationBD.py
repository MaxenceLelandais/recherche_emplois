from files.pipe.Serveur import Serveur
from data_base.DataBase import DataBase
import os

class Runner:

    def __init__(self):

        self.path_run = os.path.dirname(os.path.abspath(__file__))

        self.path_db_to_prog = self.path_run+"\\files\\doc\\db_to_prog\\"
        self.path_prog_to_db = self.path_run+"\\files\\doc\\prog_to_db\\"

        self.db = DataBase()
        
        self.serveur = Serveur(self.db)
    
    def start(self):

        self.serveur.start_serveur()

if "__main__" == __name__:

    run = Runner()
    run.start()
    
    
