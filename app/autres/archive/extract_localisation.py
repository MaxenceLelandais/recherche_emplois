import pandas as pd
import random
class Main:
    
    def __init__(self,km):
        # Charger le fichier CSV
        file_path = 'cities.json'
        self.df = pd.read_json(file_path)
        self.km = km


        
    def start(self):
        nn = 1

        km_to_degret = self.km*0.009
        
        data = {}
        nbr = float(len(self.df.values))
        n = 0.0
        print("nbr init commune",len(self.df.values))
        for info in self.df.values:

            if n%1000==1:
                print((n/nbr)*100.0,"%")

            try:

                if int(info[0]["department_number"])<120:
            
                    nom = info[0]["label"]+" ("+info[0]["department_number"]+")"
                    longitude=float(info[0]["longitude"])
                    latitude=float(info[0]["latitude"])

                    key_data = str(int(longitude//km_to_degret))+"-"+str(int(latitude//km_to_degret))

                    if key_data in data:
                        data[key_data].append(nom)
                    else:
                        data[key_data] = [nom]
                
            except:
                None
            n+=1
        print("nbr commune découpe de %s km carré : %s"%(str(self.km), len(data)))
        liste_total = []
        for i in data.values():
            if len(i)>nn*3:
                for p in range(nn):
                    liste_total.append(i[random.randint(0,len(i)-1)])
            else:
                liste_total.append(i[0])
        print("total", len(liste_total))

        file = open("communes_.txt","a")
        file.write("en_cours:0\n")
        for i in liste_total:
            file.write(i+":0\n")
        file.close()
m = Main(50)
m.start()

