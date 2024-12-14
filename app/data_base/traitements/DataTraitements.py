import bz2
import re

class DataTraitements:

    @staticmethod
    def compression(text):
        return bz2.compress(text.encode("UTF-8"))

    @staticmethod
    def decompression(text_compressed):
        return bz2.decompress(text_compressed).decode("UTF-8")

    @staticmethod
    def clean_job_posting(text):
        if not isinstance(text, str):
            text = str(text) if text is not None else ''

            
        return re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9 ,.;:?!\"'«»(){}\[\]\-_/\n\t\r\\*@&#$%^~`+=<>|€£¥¢°]", ' ', text)

    @staticmethod
    def nanToNull(data):
        for i in data:
            if data[i] == None or data[i] != data[i]:
                data[i] = "NULL"
            else:
                data[i] = DataTraitements.clean_job_posting(data[i])
        return data
    
    @staticmethod
    def extraire_remuneration_multidevise(texte):
        try:
            texte = texte.lower()
            for text in texte.split("\n"):
                if text=='':
                    continue
                if "rémunération" in text or "salaire" in text:
                    
                    if "€" in text:
                        currency = "EUR"
                    elif "$" in text:
                        currency = "USD"
                    elif "£" in text:
                        currency = "GBP"
                    else: 
                        currency = ""

                    if currency!="":

                        unite = "mois"
                        if "jour" in text or "day" in text:
                            unite = "jour"
                        elif "heure " in text or "hour" in text:
                            unite = "heure"
                        elif "an " in text or "year" in text:
                            unite = "an"
                            
                        text = text.replace(",",".")
                        text = re.sub(r'[^0-9.€$£]', '', text)

                        liste = re.split(r'[\€\$\£]', text)
                        min_salary = liste[0]
                        max_salary = min_salary
                        if len(liste)>2:
                            max_salary = liste[1]

                        try:
                            float(min_salary)
                        except:
                            min_salary="0"

                        try:
                            float(max_salary)
                        except:
                            max_salary="0"

                        return min_salary, max_salary, unite, currency
                    
        except:
            return 0,0,"NULL", "NULL"

        return 0,0,"NULL", "NULL"
        