
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,	QAbstractItemView, QHeaderView
from PyQt5.QtGui import QStandardItemModel

class ResultsView(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QVBoxLayout()
		self.setLayout(layout)
		
		# Control buttons
		control_layout = QHBoxLayout()
		self.back_btn = QPushButton("Search")
		self.back_btn_new_entry = QPushButton("New Entry")
		self.export_btn = QPushButton("Export to CSV")
		self.edit_btn = QPushButton("Edit Selected")
		self.edit_btn.setEnabled(False)  # Disabled until selection
		
		control_layout.addWidget(self.back_btn)
		control_layout.addWidget(self.back_btn_new_entry)
		control_layout.addWidget(self.export_btn)
		control_layout.addWidget(self.edit_btn)
		control_layout.addStretch()
		
		# Results table
		self.table = QTableView()
		self.model = QStandardItemModel()
		self.table.setModel(self.model)
		
		# Configure table behavior
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setSelectionMode(QAbstractItemView.SingleSelection)
		self.table.setSortingEnabled(True)
		
		# Header setup
		self.table.verticalHeader().setVisible(False)
		header = self.table.horizontalHeader()
		header.setSectionResizeMode(QHeaderView.Interactive)  # Allows manual resize
		header.setStretchLastSection(False)  # Optional: don't stretch last column

		layout.addLayout(control_layout)
		layout.addWidget(self.table)

		self.set_headers()
		self.resize_to_contents()

	def set_headers(self):
		self.model.setHorizontalHeaderLabels([
			'CX', 'ITEM', 'DESCRIÇÃO', 'DATA INÍCIO', 'DATA FIM',
			'ARQ.', 'EST.', 'PRAT.', 'RET.', 'DEST.', 'DIG.', 'MIC.',
			'CONF.', 'EMPRESA', 'MICROFILME', 'OBSERVAÇÃO', 'Descarte'
		])

	def resize_to_contents(self, padding_px:int=5):
		# Resize to contents with padding
		header = self.table.horizontalHeader()
		for col in range(self.model.columnCount()):
			self.table.resizeColumnToContents(col)
			current_width = header.sectionSize(col)
			header.resizeSection(col, current_width + padding_px)

	def clear(self):
		self.model.clear()
		self.set_headers()
