
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,	QAbstractItemView, QHeaderView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from .NaturalSortProxyModel import NaturalSortProxyModel
from .utils import HEADERS
from .database import IS_READ_ONLY

class ResultsView(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QVBoxLayout()
		self.setLayout(layout)
		
		# Control buttons
		control_layout = QHBoxLayout()
		self.back_btn = QPushButton("Nova Busca")
		self.back_btn_new_entry = QPushButton("Novo Registro")
		self.export_btn = QPushButton("Exportar para CSV")
		self.edit_btn = QPushButton("Editar Seleção")
		self.delete_btn = QPushButton("Deletar")
		
		self.edit_btn.setEnabled(False)  # Disabled until selection
		self.back_btn_new_entry.setEnabled(not IS_READ_ONLY)

		control_layout.addWidget(self.back_btn)
		control_layout.addWidget(self.back_btn_new_entry)
		control_layout.addWidget(self.export_btn)
		control_layout.addWidget(self.edit_btn)
		control_layout.addStretch(1)
		control_layout.addWidget(self.delete_btn)
		control_layout.addStretch()
		
		# Results table
		self.table = QTableView()
		self.model = QStandardItemModel()
		self.proxy = NaturalSortProxyModel(self)
		self.proxy.setSourceModel(self.model)
		self.proxy.setSortCaseSensitivity(Qt.CaseInsensitive)
		self.table.setModel(self.proxy)
		
		# Configure table behavior
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setSelectionMode(QAbstractItemView.SingleSelection)
		self.table.setSortingEnabled(True)
		self.proxy.sort(0, Qt.AscendingOrder)
		
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
			HEADERS.CX, HEADERS.ITEM, HEADERS.DESCRICAO, HEADERS.DATA_INICIO, HEADERS.DATA_FIM,
			HEADERS.LOCAL_GUARDA, HEADERS.ARQ, HEADERS.EST, HEADERS.PRAT, HEADERS.RET, HEADERS.DEST, HEADERS.DIG, HEADERS.MIC,
			HEADERS.CONF, HEADERS.EMPRESA, HEADERS.MICROFILME, HEADERS.OBSERVACAO, HEADERS.DESCARTE
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
		self.resize_to_contents()

	def get_selected_row(self):
		selected = self.table.selectionModel().selectedRows()
		if not selected:
			return None

		proxy_index = selected[0]
		source_index = self.proxy.mapToSource(proxy_index)
		row = source_index.row()

		return row
