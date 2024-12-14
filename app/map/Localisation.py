import requests
import time
class Localisation:

    def __init__(self):
        self.file_name = "Localisation"

        # Exemple d'utilisation
        # MDP ApiLoc54!joB
        # https://platform.here.com/admin/apps/P3uSJp5wnUB5OzFTzxbv
        self.here = 1000
        self.api_key_here_api = [
            #'WRxsX5rhFX7k_IQzwVSBfMVjy93ZOEpHZkeODassuUA'
            'nxKppcO9USjHGRT0fWYTwhMHfiO9zKsiymVbbwhRuHg'
        ]
        
        self.open_cage = 2500
        self.api_key_open_cage = '0e2d7bb96736432aab57d3dc9af84a04'

        self.good = False
        self.nbr = -1

    def setFifo(self, fifo):
        self.fifo = fifo
        self.start()

    def send(self):
        request = {
            "state":"GOOD",
            "name":"GetLocalisationsWithNullCoords",
            "data":{}
        }
        print("Demande liste localisation sans GPS ")
        self.good = False
        self.fifo.write_to_file(request)

    def receive(self, data):
        print("Receive localisations ")

        if self.nbr<10 and self.nbr>0:
            quit()

        if data=="OK" and self.good:
            self.send()
            return {
                "state":"PASS",
            }

        else:
            self.good = True
            address = data
            liste_result = []

            for addr in address:

                identifiant = addr[0]
                description = addr[1].replace("\n"," ").replace("\r"," ")

                while len(self.api_key_here_api)>0:
                    key = self.api_key_here_api[0]
                    try:
                        coord, self.nbr = self.get_coordinates(description, key)
                        break
                    except:
                        del self.api_key_here_api[0]
                if coord==None:
                    break
                if len(coord)>0:
                    coord = coord[0]

                    print(f"Adresse: {addr}, Latitude: {coord[0]}, Longitude: {coord[1]}")

                    liste_result.append({
                            "id":identifiant,
                            "latitude":coord[0],
                            "longitude":coord[1]
                        })

            return {
                    "state":"GOOD",
                    "data":{
                        "name":"UpdateLocalisationCoords",
                        "data":liste_result
                    }
            }

    def start(self):
        self.send()
        while 1:            
            
            time.sleep(60)

    def get_coordinates(self, address, key):

        delay = 0.02
        base_url = ""
        params = {}
        type = ""
        nbr = 0

        if self.here<0:
            type = "here"
            params = {
                    'q': address,
                    'apikey': key
                }
            base_url = "https://geocode.search.hereapi.com/v1/geocode"

        elif self.open_cage>0:
            type = "open_cage"
            params = {
                    'q': address,
                    'key': self.api_key_open_cage,
                    'limit': 1,  # Limite à 1 résultat
                    'no_annotations': 1  # Désactive les annotations supplémentaires
                }
            base_url = "https://api.opencagedata.com/geocode/v1/json"

        if base_url=="":
            return None
        
        coordinates = []

        try:
            
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()

                if type=="open_cage":
                        
                    rate = data['rate']
                    print("request restantes aujourd'hui(open_cage) : %s/%s: "%(rate['remaining'],rate['limit']))
                    
                    if 'results' in data and len(data['results']) > 0:
                        location = data['results'][0]['geometry']
                        coordinates.append((location['lat'], location['lng']))

                    nbr = rate['remaining']

                if type=="here":
                    if 'items' in data and len(data['items']) > 0:
                        location = data['items'][0]['position']
                        coordinates.append((location['lat'], location['lng']))
                else:
                    coordinates.append((0, 0))
            else:
                coordinates.append((0, 0))
        except Exception as e:
            print(f"Erreur pour l'adresse {address}: {e}")
            coordinates.append((0, 0))
            
        # Ajoute un délai pour éviter de surcharger le service
        time.sleep(delay)
        
        return coordinates, nbr


