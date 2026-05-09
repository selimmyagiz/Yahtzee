import socket, threading, json
from PyQt6.QtCore import QObject, pyqtSignal

class NetworkClient(QObject):
    message_received = pyqtSignal(dict)
    def __init__(self, ip, port):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = ip, port
    def connect(self):
        try:
            self.client.connect((self.ip, self.port))
            threading.Thread(target=self.receive, daemon=True).start()
            return True
        except: return False
    def send(self, data): self.client.send(json.dumps(data).encode('utf-8'))
    def receive(self):
        while True:
            try:
                data = self.client.recv(2048).decode('utf-8')
                if data: self.message_received.emit(json.loads(data))
            except: break