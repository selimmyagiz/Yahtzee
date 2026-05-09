import sys
import random
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont  
from ui_main import LoginDialog, YahtzeeWindow
from network_client import NetworkClient
from game_logic import calculate_points

class GameController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login = LoginDialog()
        self.my_id = -1
        self.roll_count = 0
        self.current_dice = [0]*5
        self.held = [False]*5

    def start(self):
        if self.login.exec() == QDialog.DialogCode.Accepted:
            data = self.login.get_data()
            self.ui = YahtzeeWindow()
            self.net = NetworkClient(data['ip'], 5555)
            self.net.message_received.connect(self.on_msg)
            
            if self.net.connect():
                self.net.send({"action": "join", "username": data['name']})
                self.ui.roll_btn.clicked.connect(self.do_roll)
                self.ui.score_table.cellClicked.connect(self.select_score)
                for i in range(5):
                    self.ui.dice_btns[i].clicked.connect(lambda _, x=i: self.toggle_hold(x))
                self.ui.show()
                sys.exit(self.app.exec())

    def do_roll(self):
        if self.roll_count < 3:
            vals = [random.randint(1,6) if not self.held[i] else self.current_dice[i] for i in range(5)]
            self.net.send({"action": "dice_rolled", "values": vals, "roll_count": self.roll_count + 1})

    def toggle_hold(self, i):
        if self.current_dice[i] != 0:
            self.held[i] = not self.held[i]
            self.ui.update_dice_visual(i, self.current_dice[i], self.held[i])
            
            # Seçilen zarlar değiştiği için puan tablosunu anlık güncelle
            self.show_previews()

    def select_score(self, row, col):
        # Sadece kendi sütunumuz (Sütun 1) üzerinden işlem yapabiliriz
        if col == 1 and self.roll_count > 0:
            item = self.ui.score_table.item(row, col)
            # Eğer hücre doluysa ve önizleme değilse (gerçek puansa) tıklama
            if item and item.text() != "" and not getattr(item, 'is_preview', False):
                return
            
            cat = self.ui.score_table.item(row, 0).text()
            if cat in ["Sum", "Bonus", "TOTAL SCORE"]: return
            
            # Puanı seçili olan zarlara göre değil, eldeki tüm zarlara göre kaydet
            p = calculate_points(self.current_dice, cat)
            self.net.send({"action": "end_turn", "category": cat, "row": row, "points": p})

    def show_previews(self):
        """Sadece seçili (kilitli) zarlara göre puan önizlemelerini günceller."""
        # Sadece kilitli (kırmızı çerçeveli) zarları listeye al
        selected_dice = [self.current_dice[i] for i in range(5) if self.held[i]]
        
        # Eğer hiç zar seçilmemişse veya zarlar henüz atılmamışsa önizlemeleri temizle
        if not selected_dice or self.roll_count == 0:
            self.clear_previews()
            return

        for row in range(15):
            cat = self.ui.score_table.item(row, 0).text()
            if cat in ["Sum", "Bonus", "TOTAL SCORE"]: continue
            
            item = self.ui.score_table.item(row, 1)
            # Eğer hücre boşsa veya önizlemeyse güncelle
            if not item or item.text() == "" or getattr(item, 'is_preview', False):
                p = calculate_points(selected_dice, cat)
                p_item = QTableWidgetItem(str(p))
                p_item.setForeground(QColor("#999")) # Gri önizleme rengi
                p_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                p_item.is_preview = True
                self.ui.score_table.setItem(row, 1, p_item)

    def clear_previews(self):
        """Tablodaki gri önizleme puanlarını temizler."""
        for row in range(15):
            item = self.ui.score_table.item(row, 1)
            if item and getattr(item, 'is_preview', False):
                self.ui.score_table.setItem(row, 1, QTableWidgetItem(""))
    def finalize_scores(self):
        """Oyun bittiğinde Sum, Bonus ve Total Score hesaplamalarını yapar."""
        for col in [1, 2]:  # Her iki oyuncu için de hesapla
            # 1. Üst Bölüm Toplamı (Ones - Sixes arası)
            upper_sum = 0
            for row in range(6):  # İlk 6 satır
                item = self.ui.score_table.item(row, col)
                if item and item.text() != "":
                    upper_sum += int(item.text())
            
            # Sum hücresini güncelle (Satır 6)
            self.ui.score_table.setItem(6, col, QTableWidgetItem(str(upper_sum)))
            
            # 2. Bonus Kontrolü (Satır 7)
            bonus = 35 if upper_sum >= 63 else 0
            self.ui.score_table.setItem(7, col, QTableWidgetItem(str(bonus)))
            
            # 3. Alt Bölüm Toplamı (Three of a kind - YAHTZEE arası)
            lower_sum = 0
            for row in range(8, 15):  # 8. satırdan 14. satıra kadar
                item = self.ui.score_table.item(row, col)
                if item and item.text() != "":
                    lower_sum += int(item.text())
            
            # 4. Genel Toplam (Satır 15)
            total = upper_sum + bonus + lower_sum
            total_item = QTableWidgetItem(str(total))
            total_item.setForeground(QColor("red")) # Toplam puan da kırmızı
            total_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.score_table.setItem(15, col, total_item)

        # Kazananı Belirle
        p1_total = int(self.ui.score_table.item(15, 1).text())
        p2_total = int(self.ui.score_table.item(15, 2).text())
        
        p1_name = self.ui.score_table.horizontalHeaderItem(1).text()
        p2_name = self.ui.score_table.horizontalHeaderItem(2).text()
        
        if p1_total > p2_total:
            winner_text = f"KAZANAN: {p1_name} ({p1_total} Puan)"
        elif p2_total > p1_total:
            winner_text = f"KAZANAN: {p2_name} ({p2_total} Puan)"
        else:
            winner_text = "BERABERE!"
            
        self.ui.status_box.setText(winner_text)
        self.ui.status_box.setStyleSheet("background-color: #FFD700; color: black; border: 3px solid black; font-weight: bold; font-size: 24px;")
    def on_msg(self, data):
        act = data['action']
        if act == "assign_id": 
            self.my_id = data['id']
        
        elif act == "start_game":
            # Sütun ayarlaması: Sol taraf daima aktif oyuncu (sen)
            my_name = data['player1'] if self.my_id == 0 else data['player2']
            opp_name = data['player2'] if self.my_id == 0 else data['player1']
            self.ui.score_table.setHorizontalHeaderLabels(["", my_name, opp_name])
            self.ui.player_name_label.setText(my_name)
            self.update_turn(data['turn'])

        elif act == "dice_rolled":
            self.current_dice, self.roll_count = data['values'], data['roll_count']
            for i in range(5): 
                self.ui.update_dice_visual(i, self.current_dice[i], self.held[i])
            # Zar atıldığında seçili duruma göre önizlemeleri göster
            self.show_previews()

        elif act == "end_turn":
            # Hamleyi yapanın kimliğine göre sütun belirle (0->P1, 1->P2)
            author_id = data.get('author_id')
            display_col = 1 if author_id == self.my_id else 2
            
            p_item = QTableWidgetItem(str(data['points']))
            # --- RENK DEĞİŞİKLİĞİ BURADA ---
            p_item.setForeground(QColor("red")) # Kesinleşen puanlar kırmızı olsun
            p_item.setFont(QFont("Arial", 10, QFont.Weight.Bold)) # Biraz daha belirgin yapalım
            # -------------------------------
            
            p_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            p_item.is_preview = False
            self.ui.score_table.setItem(data['row'], display_col, p_item)
            self.reset_round()
            
            # KRİTİK DÜZELTME: Sadece veri varsa turn güncellemesi yap
            if 'next_player' in data:
                self.update_turn(data['next_player'])

        elif act == "game_over":
            self.ui.status_box.setText("OYUN BİTTİ!")
            self.finalize_scores()
            self.ui.roll_btn.setEnabled(False)

            
    def update_turn(self, t):
        is_my = (t == self.my_id)
        self.ui.roll_btn.setEnabled(is_my)
        self.ui.status_box.setText("Senin Sıran!" if is_my else "Rakip Bekleniyor...")

    def reset_round(self):
        self.clear_previews()
        self.roll_count, self.held, self.current_dice = 0, [False]*5, [0]*5
        for i in range(5): 
            self.ui.update_dice_visual(i, 0, False)

if __name__ == "__main__":
    controller = GameController()
    controller.start()