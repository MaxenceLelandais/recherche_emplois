import datetime
from threading import Thread
from scrapping.jobspy import scrape_jobs
from data_base.traitements.DataTraitements import DataTraitements
import time, math,os


class Historique:

    def __init__(self, url):

        self.seen_urls = set()
        self.path_history = url

        # Charge les URLs vues depuis le fichier si il existe
        if os.path.exists(self.path_history):
            with open(self.path_history, "r") as file:
                urls = file.read().splitlines()  # Utilise splitlines() pour éviter les nouvelles lignes vides
                self.seen_urls.update(urls)
        else:
            with open(self.path_history, "a"):  # Crée le fichier s'il n'existe pas
                pass  # On n'a rien à faire ici, le fichier est simplement créé


    def ajoutId(self, key):
        if key in self.seen_urls:
            return True
        else:
            with open(self.path_history, "a") as file:
                file.write(key+"\n")

        self.seen_urls.add(key)
        return False


class Scrapping:

    def __init__(self):

        self.historiqueIndeed = Historique("scrapping/historique/url_indeed.txt")
        self.historiqueGlassdoor = Historique("scrapping/historique/url_glassdoor.txt")
        
        self.file_name = ["Indeed", "Glassdoor"]   
        self.commune_names = []
        self.list_job = [
            ["Développeur logiciel", "Software Developer", "Ingénieur logiciel", "Software Engineer", "Architecte logiciel", "Software Architect", 
             "Développeur web", "Web Developer", "Développeur mobile", "Mobile Developer", "Data Scientist", "transformation numérique", 
             "Analyste de données", "Data Analyst", "intelligence artificielle", "AI", "machine learning", "fullstack", "DevOps", "système informatique"],
            
            ["réseaux", "network", "Testeur", "quality software", "Python", "JavaScript", "Java", "Ruby", "Go (Golang)", "C++", "Django", "Flask", 
             "FastAPI", "Ladder Logic", "PLC programming languages", "Qiskit", "UX/UI", "informatique embarquée", "cybersécurité", "Cybersecurity"],
            
            ["Ingénieur en électronique", "Electronics Engineer", "Technicien en électronique", "Electronics Technician", "Concepteur de circuits intégrés", 
             "Systèmes embarqués", "Embedded Systems", "Automatisation", "automatique", "automatisme", "Ingénieur en télécommunications", "Telecommunications Engineer", 
             "Développeur FPGA", "FPGA Developer", "Ingénieur en robotique", "Robotics Engineer", "Chercheur en informatique", "Computer Scientist", 
             "Chercheur en électronique", "Electronics Researcher", "Ingénieur R&D"],
            
            ["R&D Engineer", "Scientifique", "chercheur", "virtualisation", "Analyste de systèmes", "Systems Analyst", "Bio-informaticien", "Bioinformatician", 
             "biotechnologie", "Bioinformatic", "Chercheur en physique computationnelle", "Computational Physics Researcher", "cloud", "IOT", "Express.js", 
             "NestJS", "ASP.NET", "Q#", "Rust", "Unity", "Unreal Engine"],
            
            ["frontend", "backend", "Testeur logiciel", "data base", "base de données", "big data", "DSI", "CISO", "computer vision", "neural network", 
             "automatisation", "supervision informatique", "Sécurité informatique", "C/C++", "C#", "NodeJS", "SQL", "PL/SQL", "Git", "MATLAB"],
            
            ["Fortran", "Simulink", "linux", "ubuntu", "serveur informatique", "machine virtuelle", "VM", "JIRA", "réalité virtuelle", "réalité augmentée", 
             "objets connectés", "contrôle distance", "cobol", "assembleur", "spring boot", "API", "TypeScript", "HTML", "CSS", "React"],
            
            ["Vue.js", "Angular", "Svelte", "Bootstrap", "Tailwind CSS", "RestAPI", "hibernate", "android", "ios", "applications mobiles", "applications portatives", 
             "recherche informatique", "quantique", "cryptographie", "informatics research", "quantum research", "data compression", "data transmission", 
             "compression de données", "transmission de données"]
        ]



        with open("scrapping\\communes\\communes_indeed.txt", "rb") as file:
            liste = file.read().decode("UTF-8").splitlines()
            premiere_ligne = liste[0].split(":")[1]
            
            self.actual_commune_post_indeed = int(premiere_ligne)

            self.liste_triee_indeed = []

            self.dico_commune_indeed = {}

            for ligne in liste[1:]:
                data = ligne.split(":")
                nom_commune = data[0]

                self.dico_commune_indeed[nom_commune] = int(data[1])

                self.liste_triee_indeed.append([nom_commune, int(data[1])])
                                                     
            #self.liste_triee_indeed = sorted(self.liste_triee_indeed, key=lambda x: x[1])[::-1]

        with open("scrapping\\communes\\communes_glassdoor.txt", "rb") as file:
            liste = file.read().decode("UTF-8").splitlines()
            premiere_ligne = liste[0].split(":")[1]
            
            self.actual_commune_post_glassdoor = int(premiere_ligne)

            self.liste_triee_glassdoor = []

            self.dico_commune_glassdoor = {}

            for ligne in liste[1:]:
                data = ligne.split(":")
                nom_commune = data[0]

                self.dico_commune_glassdoor[nom_commune] = int(data[1])

                self.liste_triee_glassdoor.append([nom_commune, int(data[1])])
                                                     
            #self.liste_triee_glassdoor = sorted(self.liste_triee_glassdoor, key=lambda x: x[1])[::-1]                
            

    def setClient(self, client):
        self.client = client
        self.start()

    def send(self, data):

        print("message de sortie de test ", data)
        self.client.write_to_file(data)

    def save_doc(self):

        with open("scrapping\\communes\\communes_indeed.txt", "wb") as file:

            premiere_ligne = "en_cours:"+str(self.actual_commune_post_indeed)+"\n"
            file.write(premiere_ligne.encode("utf-8"))

            for key in self.dico_commune_indeed.keys():
                
                ligne = key+":"+str(self.dico_commune_indeed[key])+"\n"
                file.write(ligne.encode("utf-8"))

        with open("scrapping\\communes\\communes_glassdoor.txt", "wb") as file:

            premiere_ligne = "en_cours:"+str(self.actual_commune_post_glassdoor)+"\n"
            file.write(premiere_ligne.encode("utf-8"))

            for key in self.dico_commune_glassdoor.keys():
                
                ligne = key+":"+str(self.dico_commune_glassdoor[key])+"\n"
                file.write(ligne.encode("utf-8"))

    def scrapping(self, site, jobs, term, commune, historique):
        for job in scrape_jobs(
                        historique_obj = historique,
                        site_name=site,
                        country_indeed="france",
                        search_term=term,
                        location=commune,
                        results_wanted=2000,
                        distance=100
                    ).to_dict('records'):
            jobs[job["id"]] = job


    def envoie(self,liste):

        if len(liste)>0:

            data = list(liste.values())

            for dico in data:
                for key in dico.keys():
                    obj = dico[key]
                    if obj is None or (isinstance(obj, float) and math.isnan(obj)):
                                    dico[key] = "NULL"
                dico["date_posted"] = dico["date_posted"].isoformat()

            request = {
                "name":"add job",
                "data":data
            }
            
            self.client.send_message(request)

    def a_indeed(self, term,liste_indeed, commune_indeed):

        for recherche in term:

            t_indeed = Thread(target=self.scrapping, args=("Indeed", liste_indeed, recherche, commune_indeed, self.historiqueIndeed))
            t_indeed.start()
            t_indeed.join()

    def a_glassdoor(self, term,liste_glassdoor, commune_glassdoor):
        

        for i in term:

            p=Thread(target=self.scrapping, args=("Glassdoor", liste_glassdoor, i, commune_glassdoor, self.historiqueGlassdoor))
                
            p.start()
            p.join()
        

    def start(self):

 
        while True:

            commune_indeed = self.liste_triee_indeed[self.actual_commune_post_indeed][0]
            commune_glassdoor = self.liste_triee_glassdoor[self.actual_commune_post_glassdoor][0]

            
            for term in self.list_job:

                if 1:
                    print("Indeed : ",commune_indeed,", Glassdoor : ",commune_glassdoor)
                    liste_indeed = {}
                    liste_glassdoor = {}

                    # liste_thread = []

                    
                    t_indeed = Thread(target=self.a_indeed, args=(term, liste_indeed, commune_indeed))
                    n = len(term)
                    p = int(n/3)
                    
                    t_glassdoor1 = Thread(target=self.a_glassdoor, args=(term[:p], liste_glassdoor, commune_glassdoor))
                    t_glassdoor2 = Thread(target=self.a_glassdoor, args=(term[p:p*2], liste_glassdoor, commune_glassdoor))
                    t_glassdoor3 = Thread(target=self.a_glassdoor, args=(term[p*2:], liste_glassdoor, commune_glassdoor))


                    t_indeed.start()
                    t_glassdoor1.start()
                    t_glassdoor2.start()
                    t_glassdoor3.start()
                    t_indeed.join()
                    t_glassdoor1.join()
                    t_glassdoor2.join()
                    t_glassdoor3.join()
                    
                    """
                    for recherche in term:
                        
                        

                        t_indeed = Thread(target=self.scrapping, args=("Indeed", liste_indeed, recherche, commune_indeed, self.historiqueIndeed))
                        t_glassdoor = Thread(target=self.scrapping, args=("Glassdoor", liste_glassdoor, recherche, commune_glassdoor, self.historiqueGlassdoor))

                        # liste_thread.append(t_indeed)
                        # liste_thread.append(t_glassdoor)
                        

                        t_indeed.start()
                        t_glassdoor.start()
                        t_indeed.join()
                        t_glassdoor.join()
                    """

                    # for t in liste_thread:
                        # t.join()
                        
                    print("nombre job envoyé indeed : ", len(liste_indeed))
                    
                    self.envoie(liste_indeed)

                    self.dico_commune_indeed[commune_indeed] += len(liste_indeed)
                    
                    
                    print("nombre job envoyé glassdoor : ", len(liste_glassdoor))
                    
                    self.envoie(liste_glassdoor)

                    self.dico_commune_glassdoor[commune_glassdoor] += len(liste_glassdoor)



                self.save_doc()                

            self.actual_commune_post_indeed = (self.actual_commune_post_indeed+1)%len(self.liste_triee_indeed)
            self.actual_commune_post_glassdoor = (self.actual_commune_post_glassdoor+1)%len(self.liste_triee_glassdoor)    


    def replace_nan_and_none_with_null(self,obj):
        if isinstance(obj, dict):
            return {k: self.replace_nan_and_none_with_null(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_nan_and_none_with_null(v) for v in obj]
        elif obj is None or (isinstance(obj, float) and math.isnan(obj)):
            return "NULL"
        else:
            return obj
