from files.pipe.Fifo import Fifo
import os

from map.Localisation import Localisation

class Runner:

    def __init__(self):

        self.path_run = os.path.dirname(os.path.abspath(__file__))

        self.localisation = Localisation()
        self.input_file = self.path_run+"\\files\\doc\\db_to_prog\\"+self.localisation.file_name
        self.output_file = self.path_run+"\\files\\doc\\prog_to_db\\"+self.localisation.file_name

    
    def start(self):

        self.fifo = Fifo(self.localisation, self.input_file, self.output_file)
        self.localisation.setFifo(self.fifo)

if "__main__" == __name__:

    run = Runner()
    run.start()
    
    
