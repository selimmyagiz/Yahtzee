import socket, threading, json

class YahtzeeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients, self.player_names = [], []
        self.turn, self.scores = 0, [{}, {}]

    def broadcast(self, data):
        for c in self.clients:
            try: c.send(json.dumps(data).encode('utf-8'))
            except: pass

    def handle_client(self, client, p_idx):
        while True:
            try:
                data = client.recv(2048).decode('utf-8')
                if not data: break
                msg = json.loads(data)
                
                # Sadece sırası gelen oyuncunun hamlesini işle
                if msg['action'] == 'end_turn' and self.turn == p_idx:
                    # Puanı kaydet
                    self.scores[p_idx][msg['category']] = msg['points']
                    
                    # Hamleyi kimin yaptığını istemciye bildir (Sütun ayarı için)
                    msg['author_id'] = p_idx 
                    
                    # Oyun bitiş kontrolü (Yahtzee'de her oyuncu 13 hamle yapar)
                    if len(self.scores[0]) == 13 and len(self.scores[1]) == 13:
                        msg['action'] = 'game_over'
                        msg['final_scores'] = self.scores
                        # Oyun bittiği için next_player göndermiyoruz, 
                        # böylece istemci tarafında KeyError oluşmuyor.
                    else:
                        # Oyun devam ediyorsa sırayı değiştir ve bildir
                        self.turn = 1 - self.turn
                        msg['next_player'] = self.turn
                
                # Güncellenmiş mesajı her iki oyuncuya da gönder
                self.broadcast(msg)
            except: 
                break

    def start(self):
        print("Yahtzee Sunucusu AWS/Global için Hazır...")
        while len(self.clients) < 2:
            conn, addr = self.server.accept()
            msg = json.loads(conn.recv(1024).decode('utf-8'))
            self.player_names.append(msg.get('username', 'P'))
            self.clients.append(conn)
            conn.send(json.dumps({"action": "assign_id", "id": len(self.clients)-1}).encode('utf-8'))
        
        # Oyunu başlatırken isimleri gönder
        self.broadcast({
            "action": "start_game", 
            "turn": 0, 
            "player1": self.player_names[0], 
            "player2": self.player_names[1]
        })
        threading.Thread(target=self.handle_client, args=(self.clients[0], 0)).start()
        threading.Thread(target=self.handle_client, args=(self.clients[1], 1)).start()

if __name__ == "__main__":
    YahtzeeServer().start()