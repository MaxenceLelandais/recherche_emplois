import socket
import json
import struct
import time

class Client:
    def __init__(self, program, host='127.0.0.1', port=12345):
        self.program = program
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect_to_server(self):
        while True:
            try:
                self.client_socket.connect((self.host, self.port))
                print("Connecté au serveur!")
                break
            except Exception as e:
                msg = f"Erreur de connexion au serveur : {e}"
                print(msg)
                if "Une demande de connexion a été effectuée sur un socket déjà connecté" in msg:
                    break
                time.sleep(1)

    def send_message(self, message):
        """Envoie un message JSON avec en-tête de longueur et reçoit une réponse"""
        try:
            message = json.dumps(message).encode("UTF-8")
            msg_length = struct.pack('>I', len(message))
            self.client_socket.sendall(msg_length + message)

            raw_msglen = self._recv_all(4)
                
            msglen = struct.unpack('>I', raw_msglen)[0]
            message = self._recv_all(msglen).decode("UTF-8")
                
            response_data = json.loads(message)
            return response_data
        except Exception as e:
            msg = f"Erreur de communication avec le client : {e}"
            print(msg)
            if "Une connexion existante a dû être fermée par l’hôte distant" in msg:
                self.connect_to_server()
            time.sleep(1)

    def _recv_all(self, n):
        data = b''
        while len(data) < n:
            packet = self.client_socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def disconnect(self):
        self.client_socket.close()
        print("Déconnecté du serveur.")
