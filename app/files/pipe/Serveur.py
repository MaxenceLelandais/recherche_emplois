import socket
import threading
import json
import struct, time

class Serveur:
    def __init__(self, program, host='127.0.0.1', port=12345):
        self.program = program
        self.host = host
        self.port = port
        self.serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_serveur(self):
        self.serveur_socket.bind((self.host, self.port))
        self.serveur_socket.listen()
        print(f"Serveur démarré et en écoute sur {self.host}:{self.port}")

        # Boucle pour accepter les connexions clients
        while True:
            client_socket, client_address = self.serveur_socket.accept()
            print(f"Nouvelle connexion de {client_address}")
            
            # Lancer un thread pour gérer le client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        """Gère la communication avec un seul client pour des messages de longueur variable"""
        while True:
            try:
                raw_msglen = self._recv_all(client_socket, 4)
                
                msglen = struct.unpack('>I', raw_msglen)[0]
                message = self._recv_all(client_socket, msglen).decode("UTF-8")
                
                data = json.loads(message)
                result = self.process_message(data)
                self.send_message(client_socket, result)
            except Exception as e:
                msg = f"Erreur de communication avec le client : {e}"
                print(msg)
                if "Une connexion existante a dû être fermée par l’hôte distant" in msg:
                    break
                time.sleep(1)
                

        client_socket.close()
        print("Client déconnecté.")

    def process_message(self, message):
        """Traitement du message en utilisant la méthode program.receive()"""
        if self.program:
            result = self.program.receive(message)
            if result["state"] == "GOOD":
                return result["data"]
        return {"state": "FAILED", "data": "Erreur de traitement"}

    def _recv_all(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send_message(self, sock, message):
        message = json.dumps(message).encode("UTF-8")
        msg_length = struct.pack('>I', len(message))
        sock.sendall(msg_length + message)

    def stop_serveur(self):
        self.serveur_socket.close()
        print("Serveur arrêté.")
