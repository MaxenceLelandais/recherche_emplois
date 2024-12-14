import json
import webview
import os, time
from threading import Thread

from map.app.API import API

carte = "autres/heatmap_france_factorise.html"



# Fonction pour lancer pywebview et afficher la carte
def lancer_webview():
    # Créer une première version de la carte
    carte_absolue_path = os.path.abspath(carte)  # par défaut, tout est affiché
    
    api = API()  # Créer l'objet API pour exposer à JS
    webview.create_window('Carte Heatmap - France', carte_absolue_path, js_api=api)


    # Lancer l'interface webview avec le callback pour injecter le JS une fois prête
    webview.start( debug=True)
#ajouter_location(locations)
# Ajouter un bouton pour lancer la WebView
lancer_webview()
