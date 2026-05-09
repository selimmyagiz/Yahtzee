from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yahtzee Giriş")
        layout = QFormLayout(self)
        self.name_in = QLineEdit()
        self.ip_in = QLineEdit("127.0.0.1")
        self.btn = QPushButton("Bağlan")
        layout.addRow("Adınız:", self.name_in)
        layout.addRow("Sunucu IP:", self.ip_in)
        layout.addRow(self.btn)
        self.btn.clicked.connect(self.accept)
    def get_data(self): return {"name": self.name_in.text(), "ip": self.ip_in.text()}

class YahtzeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1150, 800)
        self.setStyleSheet("QMainWindow { background-color: #228B22; }")
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left = QVBoxLayout()
        self.player_name_label = QLabel("Bekleniyor...")
        self.player_name_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        
        self.status_box = QLabel("Zar Atın...")
        self.status_box.setFixedSize(500, 120)
        self.status_box.setStyleSheet("background-color: #FFFF88; border: 2px solid black; color: black; font-size: 20px;")
        self.status_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.roll_btn = QPushButton("Roll Dice")
        self.roll_btn.setFixedSize(280, 70)
        self.roll_btn.setStyleSheet("font-size: 28px; background-color: white; color: black; border: 2px solid black;")

        self.dice_layout = QHBoxLayout()
        self.dice_btns = []
        for _ in range(5):
            b = QPushButton()
            b.setFixedSize(90, 90)
            b.setStyleSheet("background-color: white; border: 2px solid #555; border-radius: 12px;")
            self.dice_btns.append(b)
            self.dice_layout.addWidget(b)

        left.addWidget(self.player_name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        left.addWidget(self.status_box, alignment=Qt.AlignmentFlag.AlignCenter)
        left.addWidget(self.roll_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        left.addLayout(self.dice_layout)

        self.score_table = QTableWidget(16, 3)
        self.score_table.setFixedWidth(380)
        self.score_table.setHorizontalHeaderLabels(["", "P1", "P2"])
        self.score_table.verticalHeader().setVisible(False)
        self.score_table.setStyleSheet("""
            QTableWidget { background-color: white; color: black; gridline-color: #ccc; }
            QHeaderView::section { background-color: #f0f0f0; color: black; font-weight: bold; border: 1px solid #ccc; }
            QTableWidget::item { color: black; background-color: white; }
        """)
        self.setup_rows()

        layout.addLayout(left, stretch=2)
        layout.addWidget(self.score_table, stretch=1)

    def setup_rows(self):
        cats = ["Ones", "Twos", "Threes", "Fours", "Fives", "Sixes", "Sum", "Bonus", 
                "Three of a kind", "Four of a kind", "Full House", "Small straight", 
                "Large straight", "Chance", "YAHTZEE", "TOTAL SCORE"]
        for i, c in enumerate(cats):
            item = QTableWidgetItem(c)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setForeground(QColor("black"))
            self.score_table.setItem(i, 0, item)

    def update_dice_visual(self, index, value, held):
        btn = self.dice_btns[index]
        if value != 0:
            btn.setIcon(QIcon(f"dice_{value}.png"))
            btn.setIconSize(QSize(75, 75))
        else: btn.setIcon(QIcon())
        border = "5px solid red" if held else "2px solid #555"
        btn.setStyleSheet(f"background-color: white; border: {border}; border-radius: 12px;")