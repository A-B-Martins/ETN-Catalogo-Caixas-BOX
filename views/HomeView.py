
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

from .database import IS_READ_ONLY

class HomeView(QWidget):
	def __init__(self):
		super().__init__()
		layout = QVBoxLayout()
		self.setLayout(layout)
		
		layout.addStretch()
		
		btn_layout = QVBoxLayout()
		self.search_btn = QPushButton("Buscar")
		self.create_btn = QPushButton("Novo Registro")
		
		# Style buttons
		self.search_btn.setFixedSize(200, 60)
		self.create_btn.setFixedSize(200, 60)
		
		btn_layout.addWidget(self.search_btn)
		btn_layout.addWidget(self.create_btn)
		btn_layout.setSpacing(20)
		btn_layout.setAlignment(Qt.AlignCenter)
		
		layout.addLayout(btn_layout)
		layout.addStretch()

		self.create_btn.setEnabled(not IS_READ_ONLY)
