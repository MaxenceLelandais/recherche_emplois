import math
import os
import tarfile
import shutil
import time

from data_base.traitements.DataTraitements import DataTraitements

class SwitchRequest:

    def __init__(self):
        self.dictionnaireDonnees = {}

    def initialisation(self,cursor):

        self.__requete_init__(cursor, "SELECT id_site as id, site_name as name FROM site", "site")
        self.__requete_init__(cursor, "SELECT id_interval as id, interval_name as name FROM interval_salary", "interval")
        self.__requete_init__(cursor, "SELECT id_currency as id, currency_name as name FROM currency", "currency")
        self.__requete_init__(cursor, "SELECT id_salary_source as id, salary_source_name as name FROM salary_source", "salary_source")
        self.__requete_init__(cursor, "SELECT id_listing_type as id, listing_type_name as name FROM listing_type", "listing_type")
        self.__requete_init__(cursor, "SELECT id_company_industry as id, company_industry_name as name FROM company_industry", "company_industry")
    
    def rechercheData(self, connexion, cursor, data):

        self.__requete_recherche__(connexion, cursor, data, "site", "INSERT INTO site (site_name)")
        self.__requete_recherche__(connexion, cursor, data, "interval", "INSERT INTO interval_salary (interval_name)")
        self.__requete_recherche__(connexion, cursor, data, "currency", "INSERT INTO currency (currency_name)")
        self.__requete_recherche__(connexion, cursor, data, "salary_source", "INSERT INTO salary_source (salary_source_name)")
        self.__requete_recherche__(connexion, cursor, data, "listing_type", "INSERT INTO listing_type (listing_type_name)")
        self.__requete_recherche__(connexion, cursor, data, "company_industry", "INSERT INTO company_industry (company_industry_name)")
        
    def __requete_init__(self, cursor, requete, nom):

        cursor.execute(requete)
        result = cursor.fetchall()
        if result:
            dico = {}
            for data in result:
                dico[data[1]] = data[0]
            self.dictionnaireDonnees[nom] = dico
    
    def __requete_recherche__(self, connexion, cursor, data, nom, requete):
        dico = self.dictionnaireDonnees[nom]
        info = data[nom]
        if info in dico:
            data["id_"+str(nom)] = dico[info]
        else:
            cursor.execute(requete +" VALUES ('%s')"%(info))
            connexion.commit()
            self.dictionnaireDonnees[nom][info] = cursor.lastrowid


    
    ########################################################
    def getGetLocalisationsWithNullCoords(self,cursor):
        # Appel de la procédure stockée
        cursor.callproc('GetLocalisationsWithNullCoords',())

        # Parcourir tous les jeux de résultats
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        return results
    ########################################################
    
    ########################################################
    def updateLocalisationCoords(self,connexion, cursor, data):
        for loc in data:
            try:
                cursor.callproc('UpdateLocalisationCoords', (
                    loc["id"],
                    loc["longitude"],
                    loc["latitude"]
                ))

                # Vérifier que la procédure a bien été exécutée
                if cursor.rowcount > 0:
                    connexion.commit()
                    print(f"Les coordonnées de la localisation avec ID {loc['id']} ont été mises à jour.")
                else:
                    print(f"Aucune modification effectuée pour la localisation avec ID {loc['id']}.")

                # Vérification supplémentaire : Lire les données mises à jour
                cursor.execute("SELECT * FROM localisation WHERE id_localisation = %s", (loc["id"],))
                updated_loc = cursor.fetchone()
                if updated_loc:
                    print(f"Données mises à jour : {updated_loc}")
                else:
                    print(f"La localisation avec ID {loc['id']} n'existe pas.")
            
            except Exception as e:
                print(f"Une erreur s'est produite : {e}")
                connexion.rollback()  # Annuler toute transaction en cas d'erreur
    ########################################################

    def ensure_utf8(self,text):
        # Vérifier si le texte est déjà une chaîne, sinon renvoyer vide
        if not isinstance(text, str):
            return ""
        # Convertir en UTF-8
        return text.encode("latin1", errors="ignore").decode("latin1")

    ########################################################
    def addJob(self,connexion, cursor, data):

        job_url = ""
        if("job_url_hyper" in data):
            job_url = data["job_url_hyper"]
        if("job_url" in data):
            job_url = data["job_url"]

        job_has_description = len(data["description"])>0
        company_has_description = len(data["company_description"])>0

        if data["min_amount"]=="NULL":
            data["min_amount"] = 0

        if data["max_amount"]=="NULL":
            data["max_amount"] = 0


        if job_has_description and data["min_amount"] == 0 and data["max_amount"] == 0:
            try:
                data["min_amount"],data["max_amount"],data["interval"],data["currency"] = DataTraitements.extraire_remuneration_multidevise(data["description"])
            except:
                None
        try:
            data["min_amount"] = float(data["min_amount"])
            data["max_amount"] = float(data["max_amount"])

            if data["min_amount"]>data["max_amount"]:
                data["max_amount"] = data["min_amount"]

            if 0<data["min_amount"]<100:
                data["interval"] = "heure"
            elif 100<data["min_amount"]<10000:
                data["interval"] = "mois"
            elif data["min_amount"]>10000:
                data["interval"] = "an"

            if data["min_amount"]>10000000:
                info = str(data["min_amount"])
                try:
                    data["min_amount"] = float(info[:4])
                    data["max_amount"] = float(info[4:])
                    data["interval"] = "mois"
                except:
                    None
        except:
            data["min_amount"] = 0
            data["max_amount"] = 0

        try:
            data["min_amount"] = float(data["min_amount"])
            data["max_amount"] = float(data["max_amount"])
        except:
            data["min_amount"] = 0
            data["max_amount"] = 0

        data["min_amount"] = str(data["min_amount"])
        data["max_amount"] = str(data["max_amount"])

        data["is_remote"] = str(data["is_remote"]).lower()

        if data["is_remote"]!="true":
            data["is_remote"] = 0
        else:
            data["is_remote"] = 1

        # Déclaration de variables de sortie
        v_id_job = 0
        v_id_company = 0

        if data["company_addresses"]!="NULL":

            data["company_addresses"] = data["company"]+", "+data["company_addresses"]

        self.rechercheData(connexion, cursor, data)

        i = (
            data["id"],
            data["id_site"],
            self.ensure_utf8(job_url),
            self.ensure_utf8(data["job_url_direct"]),
            self.ensure_utf8(data["title"]),
            self.ensure_utf8(data["company"]),
            self.ensure_utf8(data["company"]+", "+data["location"]),
            data["job_type"],  # Assurez-vous que c'est bien "job_type", sinon changez-le en "job_title"
            data["date_posted"],
            data["id_salary_source"],
            data["id_interval"],
            data["min_amount"],
            data["max_amount"],
            data["id_currency"],
            data["is_remote"],
            data["job_level"],
            self.ensure_utf8(data["job_function"]),
            data["id_company_industry"],
            data["id_listing_type"],
            self.ensure_utf8(data["emails"]),
            job_has_description,
            self.ensure_utf8(data["company_url"]),
            self.ensure_utf8(data["company_url_direct"]),
            self.ensure_utf8(data["company_addresses"]),
            self.ensure_utf8(data["company_num_employees"]),
            self.ensure_utf8(data["company_revenue"]),
            company_has_description,
            self.ensure_utf8(data["logo_photo_url"]),
            self.ensure_utf8(data["banner_photo_url"]),
            self.ensure_utf8(data["ceo_name"]),
            self.ensure_utf8(data["ceo_photo_url"]),
            v_id_job,    
            v_id_company #
        )


        # Appel de la procédure stockée
        cursor.callproc('add_job', i)

        # Commit the changes to make sure data is saved
        connexion.commit()

        # Requête pour récupérer les valeurs de sortie
        cursor.execute("SELECT @v_id_job AS job_id, @v_id_company AS company_id")
        result = cursor.fetchone()

        # Vérification et affectation des résultats
        if result:
            job_id, company_id = result
            print(f"Job ID: {job_id}, Company ID: {company_id}")
        else:
            print("No job or company ID returned.")
        if job_id==None or company_id==None:
            return

        directory_name_job = str(math.floor((job_id-1)/1000)*1000+1)+"-"+str(math.floor((job_id-1)/1000+1)*1000)
        directory_name_company = str(math.floor((company_id-1)/1000)*1000+1)+"-"+str(math.floor((company_id-1)/1000+1)*1000)
        
        path_job = "files\\doc\\descriptions\\job\\"+directory_name_job+"\\"
        path_company = "files\\doc\\descriptions\\company\\"+directory_name_company+"\\"

        job_id_archive = job_id-1000
        company_id_archive = company_id-1000
        directory_name_job_archive = str(math.floor((job_id_archive-1)/1000)*1000+1)+"-"+str(math.floor((job_id_archive-1)/1000+1)*1000)
        directory_name_company_archive = str(math.floor((company_id_archive-1)/1000)*1000+1)+"-"+str(math.floor((company_id_archive-1)/1000+1)*1000)

        path_job_archive = "files\\doc\\descriptions\\job\\"+directory_name_job_archive+"\\"
        path_company_archive = "files\\doc\\descriptions\\company\\"+directory_name_company_archive+"\\"
        name_archive = "archive.tar.bz2"

        if not os.path.exists(path_job):
            os.makedirs(path_job)

        if not os.path.exists(path_company):
            os.makedirs(path_company)

        liste_dossier_job = os.listdir(path_job)
        if name_archive not in liste_dossier_job:
            file_job = open(path_job+str(job_id)+".txt","ab")
            file_job.write(data["description"].encode('UTF-8'))
            file_job.close()

        liste_dossier_company = os.listdir(path_company)
        if name_archive not in liste_dossier_company:

            file_company = open(path_company+str(company_id)+".txt","ab")
            file_company.write(data["company_description"].encode('UTF-8'))
            file_company.close()

        if os.path.exists(path_job_archive):
            liste_dossier_job_archive = os.listdir(path_job_archive)
            if name_archive not in liste_dossier_job_archive:
                with tarfile.open(path_job_archive+"\\archive.tar.bz2", 'w:bz2') as tar:
                    for file_name in liste_dossier_job_archive:
                        file_path = os.path.join(path_job_archive, file_name)
                        tar.add(file_path, arcname=file_name)
                for file_name in liste_dossier_job_archive:
                    if os.path.exists(path_job_archive+"//"+file_name):
                        os.remove(path_job_archive+"//"+file_name)

        if os.path.exists(path_company_archive):
            liste_dossier_company_archive = os.listdir(path_company_archive)
            if name_archive not in liste_dossier_company_archive:
                with tarfile.open(path_company_archive+"\\archive.tar.bz2", 'w:bz2') as tar:
                    for file_name in liste_dossier_company_archive:
                        file_path = os.path.join(path_company_archive, file_name)
                        tar.add(file_path, arcname=file_name)

                for file_name in liste_dossier_company_archive:
                    
                    if os.path.exists(path_company_archive+"//"+file_name):
                        os.remove(path_company_archive+"//"+file_name)
        
    ########################################################

    def getDescription(self, directory, id):

        path_partition = "files\\doc\\descriptions\\"+directory+"\\"+str(math.floor((id-1)/1000)*1000+1)+"-"+str(math.floor((id-1)/1000+1)*1000)+"\\"
        archive_name = 'archive.tar.bz2'

        if os.path.exists(path_partition):
            list_files = os.listdir(path_partition)
            
            if id+".txt" in list_files:
                file = open(id+".txt","rb")
                description = file.read()
                file.close()
                return description
            
            elif archive_name in list_files:

                file_to_extract = id+".txt"
                destination_folder = "files\\doc\\descriptions\\tmp\\"

                if os.path.exists(destination_folder):
                    shutil.rmtree(destination_folder) 

                os.makedirs(destination_folder)

                with tarfile.open(path_partition+archive_name, 'r:bz2') as tar:
                    try:
                        # Extraire un fichier spécifique
                        tar.extract(file_to_extract, path=destination_folder)
                        print(f"Le fichier '{file_to_extract}' a été extrait avec succès dans '{destination_folder}'")
                        file = open(destination_folder+file_to_extract,"rb")
                        description = file.read()
                        file.close()
                        os.remove(destination_folder+file_to_extract)
                        return description
                    
                    except KeyError:
                        print(f"Le fichier '{file_to_extract}' n'existe pas dans l'archive.")
        return None
    def addLocalisationVille(self, connexion, cursor, data):

        description = data["label"]+" ,"+data["region_name"]+" ("+data["department_number"]+"), France"
        
        try:
            data["longitude"] = str(round(float(data["longitude"]), 8))
            data["latitude"] = str(round(float(data["latitude"]), 8))
        
            i = [
                    data["insee_code"],
                    data["city_code"],
                    data["zip_code"],
                    data["label"],
                    description,
                    data["longitude"],
                    data["latitude"],
                    data["department_name"],
                    data["department_number"],
                    data["region_name"],
                    data["region_geojson_name"]
                ]

            cursor.callproc('addLocalisationVille', i)
            # Commit the changes to make sure data is saved
            connexion.commit()
            print("Ok, ", description)
        except :
            None
    
