#!/usr/bin/env python3

import sys
import csv
from random import randint
from datetime import datetime, timezone, timedelta

from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QStackedWidget, QFileDialog, QDateTimeEdit
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMessageBox

from views.HomeView import HomeView
from views.SearchView import SearchView
from views.ResultsView import ResultsView
from views.EditView import EditView
from views.NewEntryView import NewEntryView
from views.NullableSpinBox import NullableSpinBox

from views.models import ArchiveBox, db_col_restrictions
from views.utils import build_query, update_record, HEADERS
from views.database import IS_READ_ONLY

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Catálogo Caixas BOX")
		self.setGeometry(100, 100, 1100, 680)
		
		self.results_pk = None

		# Create stacked widget
		self.stacked_widget = QStackedWidget()
		self.setCentralWidget(self.stacked_widget)
		
		# Create views
		self.home_view = HomeView()
		self.search_view = SearchView()
		self.results_view = ResultsView()
		self.edit_view = EditView()
		self.new_entry_view = NewEntryView()
		
		# Add to stack
		self.stacked_widget.addWidget(self.home_view)         # Index 0
		self.stacked_widget.addWidget(self.search_view)       # Index 1
		self.stacked_widget.addWidget(self.results_view)      # Index 2
		self.stacked_widget.addWidget(self.edit_view)         # Index 3
		self.stacked_widget.addWidget(self.new_entry_view)    # Index 4

		# Connect navigation signals
		self.home_view.search_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
		self.home_view.create_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
		self.search_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.new_entry_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.results_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
		self.results_view.back_btn_new_entry.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
		
		# Connect signals
		self.new_entry_view.save_btn.clicked.connect(self.save_new_entry)
		self.search_view.search_btn.clicked.connect(self.show_results)
		self.results_view.export_btn.clicked.connect(self.export_to_csv)
		self.results_view.edit_btn.clicked.connect(self.prepare_edit_view)
		self.results_view.delete_btn.clicked.connect(self.delete_entry)
		self.results_view.table.selectionModel().selectionChanged.connect(
			lambda: self.results_view.edit_btn.setEnabled(
				self.results_view.table.selectionModel().hasSelection() and not IS_READ_ONLY
			)
		)
		self.results_view.table.selectionModel().selectionChanged.connect(
			lambda: self.results_view.delete_btn.setEnabled(
				self.results_view.table.selectionModel().hasSelection() and not IS_READ_ONLY
			)
		)
		self.edit_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.edit_view.save_btn.clicked.connect(self.save_changes)

		# UI columns to db columns map
		self.text_fields_col_db_map = [
			(HEADERS.CX, 'cx'), (HEADERS.ITEM, "item"), (HEADERS.DESCRICAO, "descricao"), (HEADERS.LOCAL_GUARDA, "local_guarda"),
			(HEADERS.RET, "ret"), (HEADERS.EMPRESA, "empresa"), (HEADERS.MICROFILME, "microfilme"), (HEADERS.OBSERVACAO, "observacao")
		]

		self.date_fields_col_db_map = [
			(HEADERS.DATA_INICIO_START, 'data_inicio', 'gte'), (HEADERS.DATA_FIM_START, "data_fim", 'gte'), (HEADERS.CONF_START, "conf", 'gte'),
			(HEADERS.DATA_INICIO_END, 'data_inicio', 'lte'), (HEADERS.DATA_FIM_END, "data_fim", 'lte'), (HEADERS.CONF_END, "conf", 'lte')
		]

		self.integer_bool_fields_col_db_map = [
			# Integer fields
			(HEADERS.ARQ, "arq"), (HEADERS.EST, "est"), (HEADERS.PRAT, "prat"), (HEADERS.DEST, "dest"),
			# Boolean fields
			(HEADERS.DIG, "dig"), (HEADERS.MIC, "mic"), (HEADERS.DESCARTE, "descarte")
		]

		self.columns_db_map = {
			# Text fields
			HEADERS.CX: 'cx', HEADERS.ITEM: "item", HEADERS.DESCRICAO: "descricao", HEADERS.LOCAL_GUARDA: "local_guarda",
			HEADERS.RET: "ret", HEADERS.EMPRESA: "empresa", HEADERS.MICROFILME: "microfilme", HEADERS.OBSERVACAO: "observacao",
			# Date fields
			HEADERS.DATA_INICIO: 'data_inicio', HEADERS.DATA_FIM: "data_fim", HEADERS.CONF: "conf",
			# Integer fields
			HEADERS.ARQ: "arq", HEADERS.EST: "est", HEADERS.PRAT: "prat", HEADERS.DEST: "dest",
			# Boolean fields
			HEADERS.DIG: "dig", HEADERS.MIC: "mic", HEADERS.DESCARTE: "descarte"
		}

		self.db_col_restrictions = db_col_restrictions

	def save_new_entry(self):
		new_data = {}
		
		for key, widget in self.new_entry_view.fields.items():
			if 'Enabled' in key: continue
			
			if isinstance(widget, QDateTimeEdit):
				checkbox = self.new_entry_view.fields[f'{key} Enabled']
				new_data[key] = widget.dateTime().toString("dd-MM-yyyy") if checkbox.isChecked() else ""
			elif isinstance(widget, QCheckBox):
				new_data[key] = "✓" if widget.isChecked() else ""
			elif isinstance(widget, NullableSpinBox):
				new_data[key] = str(widget.value()) if widget.value() is not None else ""
			else:
				new_data[key] = widget.text()

		# print(new_data)
		row = [QStandardItem(new_data[key]) for key in [self.results_view.model.horizontalHeaderItem(i).text() for i in range(self.results_view.model.columnCount())]]
		# row = {key: self.db_col_restrictions[key] for key in self.columns_db_map.keys()}
		params = {}
		for key, db_key in self.columns_db_map.items():
			accept_null, max_len = self.db_col_restrictions[key]

			if accept_null and new_data[key] == "":
				if db_key in ["ret", "empresa", "microfilme", "observacao"]:
					params[db_key] = ""
				elif db_key in ["dig", "mic", "descarte"]:
					params[db_key] = False
				else:
					params[db_key] = None
			
			elif new_data[key]:
				# date
				if db_key in ["data_inicio", "data_fim", "conf"]:
					params[db_key] = datetime.strptime(new_data[key], "%d-%m-%Y").replace(tzinfo=timezone(timedelta(hours=-3)))
				# integer
				elif db_key in ["arq", "est", "prat", "dest"]:
					params[db_key] = int(new_data[key])
				# boolean
				elif db_key in ["dig", "mic", "descarte"]:
					params[db_key] = True if new_data[key] == '✓' else False
				# text
				else: #db_key in ['cx', "item", "descricao", "ret", "empresa", "microfilme", "observacao"]:
					params[db_key] = new_data[key].strip()
			
			else:
				params[db_key] = ""
				# TODO CANNOT SEND

			# print(f"accept_null: {accept_null} | new_data[key]: '{new_data[key]}' | param: '{params[self.columns_db_map[key]]}' | type: {type(params[self.columns_db_map[key]])}")

		# print(f"save entry params: { params }")
		
		self.search_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.new_entry_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		
		new_row = ArchiveBox.create(**params)
		self.results_pk.append(new_row.id)
		self.results_view.model.appendRow(row)
		self.stacked_widget.setCurrentIndex(2)  # Switch to results view

	def prepare_edit_view(self):
		row = self.results_view.get_selected_row()
		if row is None: return

		self.current_edit_data = {
			self.results_view.model.horizontalHeaderItem(col).text(): self.results_view.model.item(row, col).text()
			for col in range(self.results_view.model.columnCount())
		}

		# Load data into edit view
		date_fields = [HEADERS.DATA_INICIO, HEADERS.DATA_FIM, HEADERS.CONF]
		for field in date_fields:
			checkbox = self.edit_view.fields[f'{field} Enabled']
			date_widget = self.edit_view.fields[field]
			value = self.current_edit_data.get(field, "")
			
			# Check if date is valid
			if value.strip():
				qdatetime = QDateTime.fromString(value, "dd-MM-yyyy")
				if qdatetime.isValid():
					checkbox.setChecked(True)
					date_widget.setDateTime(qdatetime)
					continue
			
			# Invalid/empty date
			checkbox.setChecked(False)
			date_widget.setDateTime(QDateTime.currentDateTime())

		# Load other fields
		for field, widget in self.edit_view.fields.items():
			if field in date_fields or 'Enabled' in field:
				continue  # Already handled dates
				
			value = self.current_edit_data.get(field.replace(' Enabled', ''), "")
			if isinstance(widget, QCheckBox):
				widget.setChecked(value.lower() == "✓")
			elif isinstance(widget, NullableSpinBox):
				widget.setValue(int(value) if value.isdigit() else None)
			else:
				widget.setText(value)

		self.stacked_widget.setCurrentIndex(3)

	def delete_entry(self):
		row = self.results_view.get_selected_row()

		if row is None: return
		db_row = ArchiveBox.get(ArchiveBox.id == self.results_pk[row])

		# Create QMessageBox and customize button text
		msg_box = QMessageBox(self)
		msg_box.setWindowTitle('Confirmação')
		msg_box.setText('Deletar registro selecionado?')
		msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		msg_box.setDefaultButton(QMessageBox.No)
		
		# Customize button text
		msg_box.button(QMessageBox.Yes).setText('Sim')
		msg_box.button(QMessageBox.No).setText('Não')

		reply = msg_box.exec_()

		if reply == QMessageBox.Yes:
			print(f"deleted {db_row}")
			db_row.delete_instance()
			self.show_results()
		else:
			pass

	def save_changes(self):
		row = self.results_view.get_selected_row()
		print('C1')
		# print(f"row: {row} | pk: {self.results_pk[row]}")
		if row is None: return
		db_row = ArchiveBox.get(ArchiveBox.id == self.results_pk[row])
		print('C2')

		columns_to_update = {}

		for col in range(self.results_view.model.columnCount()):
			print(col)
			header = self.results_view.model.horizontalHeaderItem(col).text()
			widget = self.edit_view.fields.get(header)
			
			if isinstance(widget, QDateTimeEdit):
				checkbox = self.edit_view.fields[f'{header} Enabled']
				value = widget.dateTime().toString("dd-MM-yyyy") if checkbox.isChecked() else ""
				columns_to_update[self.columns_db_map[header]] = widget.dateTime().toPyDateTime().replace(tzinfo=timezone(timedelta(hours=-3))) if checkbox.isChecked() else None

			elif isinstance(widget, QCheckBox):
				value = "✓" if widget.isChecked() else ""
				columns_to_update[self.columns_db_map[header]] = widget.isChecked()

			elif isinstance(widget, NullableSpinBox):
				value = str(widget.value()) if widget.value() is not None else ''
				columns_to_update[self.columns_db_map[header]] = widget.value()

			else:
				value = widget.text()
				columns_to_update[self.columns_db_map[header]] = widget.text()
			
			# self.results_view.model.setItem(row, col, QStandardItem(value))
		
		update_record(db_row, columns_to_update)
		# re-query search with same parameters
		self.show_results()

	def back_to_results(self):
		self.stacked_widget.setCurrentIndex(2)

	def export_to_csv(self):
		options = QFileDialog.Options()
		filename, _ = QFileDialog.getSaveFileName(
			self, "Save CSV File", "", "CSV Files (*.csv)", options=options
		)
		
		if not filename:
			return
		
		try:
			with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
				writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
				
				# Write headers (from source model)
				headers = [
					self.results_view.model.horizontalHeaderItem(i).text()
					for i in range(self.results_view.model.columnCount())
				]
				writer.writerow(headers)
				
				# Get proxy model reference
				proxy = self.results_view.proxy
				
				# Write data using proxy model directly
				for row in range(proxy.rowCount()):
					row_data = []
					for col in range(proxy.columnCount()):
						text = proxy.index(row, col).data() or ""
						row_data.append("" if text == "None" else text)
					writer.writerow(row_data)
					
		except Exception as e:
			print(f"Error exporting CSV: {str(e)}")

	def show_results(self):
		# Store current search parameters
		self.current_search_params = self.get_search_params()
		# print(self.current_search_params)
		# Query rows based on search parameters
		self.query_search()
		# Set rows into view
		self.populate_results()
		
		self.search_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.new_entry_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.results_view.edit_btn.setEnabled(False)
		self.results_view.delete_btn.setEnabled(False)
		
		# Switch to results view
		self.stacked_widget.setCurrentIndex(2)

	def show_search(self):
		self.stacked_widget.setCurrentIndex(0)

	def get_search_params(self):
		"""Collect parameters from search fields"""
		filters = self.search_view.filters

		line_tpls      = [(key, filters[key].text()     ) for key in [HEADERS.CX, HEADERS.ITEM, HEADERS.DESCRICAO, HEADERS.RET, HEADERS.EMPRESA, HEADERS.MICROFILME, HEADERS.OBSERVACAO, HEADERS.LOCAL_GUARDA]]
		spin_box_tpls  = [(key, filters[key].value()    ) for key in [HEADERS.ARQ, HEADERS.EST, HEADERS.PRAT, HEADERS.DEST]]
		checkbox_tpls  = [(key, filters[key].isChecked()) for key in [HEADERS.DIG_SIM, HEADERS.DIG_NAO, HEADERS.MIC_SIM, HEADERS.MIC_NAO, HEADERS.DESCARTE_SIM, HEADERS.DESCARTE_NAO]]

		date_checkbox = {}
		date_checkbox[HEADERS.DATA_INICIO_START] = date_checkbox[HEADERS.DATA_INICIO_END] = filters[HEADERS.DATA_INICIO_ENABLED].isChecked()
		date_checkbox[HEADERS.DATA_FIM_START]    = date_checkbox[HEADERS.DATA_FIM_END]    = filters[HEADERS.DATA_FIM_ENABLED].isChecked()
		date_checkbox[HEADERS.CONF_START]        = date_checkbox[HEADERS.CONF_END]        = filters[HEADERS.CONF_ENABLED].isChecked()
		
		date_time_tpls = [
			(key, filters[key].dateTime().toString(Qt.ISODate) if date_checkbox[key] else None)
			for key in [HEADERS.DATA_INICIO_START, HEADERS.DATA_INICIO_END, HEADERS.DATA_FIM_START, HEADERS.DATA_FIM_END, HEADERS.CONF_START, HEADERS.CONF_END]
		]

		return {
			key: value
			for key, value in [*line_tpls, *spin_box_tpls, *checkbox_tpls, *date_time_tpls]
		}

	def query_search(self):
		filters = {}
		params = self.current_search_params
		print(params)

		# Text fields
		for col, col_db in self.text_fields_col_db_map:
			if params[col]: filters[f"{col_db}__ilike"] = f"{params[col]}"

		# Date fields
		for col, col_db, operator in self.date_fields_col_db_map:
			if params[col]: filters[f"{col_db}__{operator}"] = f"{params[col]}"

		# Integer and Boolean fields
		control_boxes = [HEADERS.DIG, HEADERS.MIC, HEADERS.DESCARTE]
		for col, col_db in self.integer_bool_fields_col_db_map:
				if col not in control_boxes:
					if params[col]:
						filters[f"{col_db}__eq"] = f"{params[col]}"
				else:
					if (params[f"{col} Sim"] and params[f"{col} Não"]) or ((not params[f"{col} Sim"]) and (not params[f"{col} Não"])):
						pass
					else:
						print(params[f"{col} Sim"])
						if params[f"{col} Sim"]:
							filters[f"{col_db}__eq"] = f"{params[f"{col} Sim"]}"
						else:
							filters[f"{col_db}__ne"] = f"{params[f"{col} Sim"]}"

		# print(f"filters: {filters}")
		self.query = list(build_query(ArchiveBox, filters))
		
		# print(f"query: {list(query)}")
		# for row in self.query:
		# 	print(f"id: {row.id} | cx: {row.cx}")

	def populate_results(self):
		# Clear existing data
		self.results_view.clear()
		self.results_pk = []

		# Add dummy data
		for i in self.query:
			column_values = [
				f"{i.cx}", f"{i.item}", f"{i.descricao}",
				
				i.data_inicio.strftime("%d-%m-%Y") if i.data_inicio else "",
				i.data_fim.strftime("%d-%m-%Y") if i.data_fim else "",
				
				str(i.local_guarda) if i.local_guarda else "",

				str(i.arq), str(i.est), str(i.prat), str(i.ret), str(i.dest) if i.dest != -1 else "",
				
				"✓" if i.dig else "", "✓" if i.mic else "",
				
				i.conf.strftime("%d-%m-%Y") if i.conf else "",
				
				str(i.empresa), str(i.microfilme), str(i.observacao),
				
				"✓" if i.descarte else ""
			]

			row = [QStandardItem(item) for item in column_values]
			
			self.results_view.model.appendRow(row)
			self.results_pk.append(i.id)

		# self.results_view.resize_to_contents()
		# print(self.results_pk)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
