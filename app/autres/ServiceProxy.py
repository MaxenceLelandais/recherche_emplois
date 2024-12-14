import requests
import time
import random
import socket
from requests.exceptions import SSLError, ProxyError, Timeout
import ssl
import re

class ProxyManager:
    def __init__(self):
        self.proxy_list = []
        self.valid_proxies = []
        self.api_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&anonymity=Elite,Anonymous&timeout=1019"
        self.test_url = "https://httpbin.org/ip"  # Test de base
        self.ssl_test_url = "https://www.google.com"  # Test SSL

    def fetch_proxies(self):
        """Récupère la liste des proxies depuis l'API."""
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                self.proxy_list = response.text.strip().replace("\r","").replace("http://","").replace("https://","").replace("socks4://","").replace("socks5://","").split('\n')
                print(f"{len(self.proxy_list)} proxys récupérés.")
            else:
                print(f"Échec de la récupération des proxys (statut HTTP: {response.status_code}).")
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération des proxys : {e}")
    
    def check_ssl(self, proxy):
        """Vérifie si le proxy supporte le SSL correctement."""
        proxies = {"https": f"https://{proxy}"}
        try:
            response = requests.get(self.ssl_test_url, proxies=proxies, timeout=5)
            if response.status_code == 200:
                print(f"SSL vérifié pour {proxy}")
                return True
        except (SSLError, ProxyError, Timeout) as e:
            print(f"Erreur SSL pour {proxy} : {e}")
        return False

    def test_proxy(self, proxy):
        """Teste la validité d'un proxy en utilisant un simple test de connexion et vérifie l'anonymat."""
        # Configuration des proxies pour HTTP(S), SOCKS4, et SOCKS5
        proxies = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",
            "socks4": f"socks4://{proxy}",
            "socks5": f"socks5://{proxy}"
        }
        try:
            start_time = time.time()
            response = requests.get(self.test_url, proxies=proxies, timeout=5)
            elapsed_time = time.time() - start_time
            if response.status_code == 200:
                ip_returned = response.json().get('origin')
                # Vérifie que le proxy est anonyme (l'IP ne doit pas être celle du client)
                if ip_returned != requests.get(self.test_url).json().get('origin'):
                    print(f"Proxy {proxy} valide et anonyme (réponse en {elapsed_time:.2f} sec).")
                    return True
        except (ProxyError, Timeout, SSLError, socket.error) as e:
            print(f"Échec du proxy {proxy} : {e}")
        return False

    def blacklist_check(self, proxy):
        """Vérifie si l'IP du proxy est sur une liste noire via AbuseIPDB."""
        abuse_api_key = "YOUR_ABUSEIPDB_API_KEY"  # Remplace par ta clé API d'AbuseIPDB
        ip = proxy.split(':')[0]  # Extraire l'IP du proxy
        url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}"
        headers = {
            'Accept': 'application/json',
            'Key': abuse_api_key
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['data']['abuseConfidenceScore'] > 50:  # Marque comme risqué si le score est élevé
                    print(f"Le proxy {proxy} est sur une liste noire (score de risque: {data['data']['abuseConfidenceScore']}).")
                    return False
        except Exception as e:
            print(f"Erreur lors de la vérification blacklist pour {proxy}: {e}")
        return True

    def add_proxy(self, proxy):
        """Teste un proxy et l'ajoute si toutes les vérifications sont valides."""
        if self.test_proxy(proxy) and self.check_ssl(proxy) and self.blacklist_check(proxy):
            self.valid_proxies.append(proxy)

    def rotate_proxies(self):
        """Effectue une rotation automatique des proxys."""
        while True:
            self.valid_proxies.clear()  # Réinitialiser les proxys valides
            self.fetch_proxies()
            for proxy in self.proxy_list:
                self.add_proxy(proxy)
            print(f"{len(self.valid_proxies)} proxys valides après vérification.")
            time.sleep(3600)  # Rotation toutes les heures

    def get_random_proxy(self):
        """Retourne un proxy valide au hasard."""
        if not self.valid_proxies:
            print("Aucun proxy valide disponible.")
            return None
        return random.choice(self.valid_proxies)

# Exemple d'utilisation
if __name__ == "__main__":
    proxy_manager = ProxyManager()
    
    # Démarrer la rotation de proxy (bloque le programme)
    proxy_manager.rotate_proxies()
