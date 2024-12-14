import mysql.connector
from mysql.connector import errorcode
import time

from data_base.SwitchRequest import SwitchRequest

class DataBase :

    def __init__(self):

        self.switchRequest = SwitchRequest()

        print("Data base process initialisation ...")

        self.config = {
          'user': 'root',
          'password': '',
          'host': '127.0.0.1',
          'database': 'recherche_entreprise',
          'raise_on_warnings': True
        }

        self.db = None

        if self.connexion():
            
            with self.db.cursor() as cursor:
                self.switchRequest.initialisation(cursor)                

    def connexion(self):
        

        print("Start data base connexion...")
        lastError = ""
        while (self.db==None or not self.db.is_connected()) :

            try:
                self.db = mysql.connector.connect(**self.config)
            except mysql.connector.Error as err:

                msg = err.msg
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    msg = "Something is wrong with your user name or password."
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    msg = "Database does not exist."
                
                if(lastError!=msg):
                    print(msg)
                    lastError = msg
                time.sleep(1)

        print("Data base connexion is ready.")
        return self.db.is_connected()

    def request(self, request_json):

        requete_name = request_json["name"]
        result = []
        print("Request : %s." % requete_name)
        with self.db.cursor() as cursor:
            try:
                result = self.switch(cursor, requete_name, request_json["data"])
                if result==[]:
                    result = cursor.fetchall()
                self.db.commit()
            except mysql.connector.Error as err:
                print(err)
                self.connexion()
                self.request(request_json)
                        
        return result
    
    def receive(self,obj):
        resultats = self.request(obj)
        result = {
            "state":"GOOD",
            "data":resultats
        }
        return result
    
    def switch(self, cursor, name, data):

        if name == "add job":
            for info in data:
                try:
                    self.switchRequest.addJob(self.db, cursor, info)
                except mysql.connector.Error as err:
                    print(err)
                    self.connexion()
                        
                except Exception as e:
                
                    print(e)
                    self.connexion()
        elif name == "add localisation ville":
            for info in data:
                info = info[0]
                try:
                    self.switchRequest.addLocalisationVille(self.db,cursor, info)
                except mysql.connector.Error as err:
                    print(err)
                    self.connexion()
                        
                except Exception as e:
                
                    print(e)
                    
                    self.connexion()
        elif name == "UpdateLocalisationCoords":
            self.switchRequest.updateLocalisationCoords(self.db, cursor,data[0])
            return "OK"
        elif name == "GetLocalisationsWithNullCoords":
            return self.switchRequest.getGetLocalisationsWithNullCoords(cursor)

    def close(self):

        self.db.close()
        print("Data base is close.")

    def disconnectAllUser(self):

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )

        cursor = conn.cursor()

        # Exécuter la commande SHOW PROCESSLIST pour lister toutes les connexions
        cursor.execute("SHOW PROCESSLIST;")

        # Parcourir tous les résultats
        processes = cursor.fetchall()

        # Terminer chaque processus non root
        for process in processes:
            process_id = process[0]
            user = process[1]
            
            # Ne pas tuer la connexion root
            if user != 'root':
                print(f"Déconnexion de l'utilisateur avec le process ID: {process_id}")
                try:
                    cursor.execute(f"KILL {process_id};")
                except mysql.connector.Error as err:
                    # Vérifier si l'erreur est liée à un thread inconnu (processus déjà terminé)
                    if err.errno == 1094:
                        print(f"Le processus avec l'ID {process_id} n'existe plus (déjà terminé).")
                    else:
                        print(f"Erreur lors de la déconnexion du process ID {process_id}: {err}")

        # Fermer le curseur et la connexion
        cursor.close()
        conn.close()
