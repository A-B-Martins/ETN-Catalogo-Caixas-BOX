
import sys
import csv
from random import randint

from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QStackedWidget, QFileDialog, QDateTimeEdit
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QStandardItem

from views.HomeView import HomeView
from views.SearchView import SearchView
from views.ResultsView import ResultsView
from views.EditView import EditView
from views.NewEntryView import NewEntryView
from views.NullableSpinBox import NullableSpinBox

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Database Manager")
		self.setGeometry(100, 100, 1100, 680)
		
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
		self.results_view.table.selectionModel().selectionChanged.connect(
			lambda: self.results_view.edit_btn.setEnabled(
				self.results_view.table.selectionModel().hasSelection()
			)
		)
		self.edit_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.edit_view.save_btn.clicked.connect(self.save_changes)

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
				new_data[key] = str(widget.value()) if widget.value() is not None else ''
			else:
				new_data[key] = widget.text()

		row = [
			QStandardItem(new_data.get('CX', '')),
			QStandardItem(new_data.get('ITEM', '')),
			QStandardItem(new_data.get('DESCRIÇÃO', '')),
			QStandardItem(new_data.get('DATA INÍCIO', '')),
			QStandardItem(new_data.get('DATA FIM', '')),
			QStandardItem(new_data.get('ARQ.', '')),
			QStandardItem(new_data.get('EST.', '')),
			QStandardItem(new_data.get('PRAT.', '')),
			QStandardItem(new_data.get('RET.', '')),
			QStandardItem(new_data.get('DEST.', '')),
			QStandardItem(new_data.get('DIG.', '')),
			QStandardItem(new_data.get('MIC.', '')),
			QStandardItem(new_data.get('CONF.', '')),
			QStandardItem(new_data.get('EMPRESA', '')),
			QStandardItem(new_data.get('MICROFILME', '')),
			QStandardItem(new_data.get('OBSERVAÇÃO', '')),
			QStandardItem(new_data.get('Descarte', ''))
		]
		
		self.search_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.new_entry_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		
		self.results_view.model.appendRow(row)
		self.stacked_widget.setCurrentIndex(2)  # Switch to results view

	def prepare_edit_view(self):
		selected = self.results_view.table.selectionModel().selectedRows()
		if not selected:
			return

		row = selected[0].row()
		self.current_edit_data = {
			self.results_view.model.horizontalHeaderItem(col).text(): self.results_view.model.item(row, col).text()
			for col in range(self.results_view.model.columnCount())
		}

		# Load data into edit view
		date_fields = ['DATA INÍCIO', 'DATA FIM', 'CONF.']
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

	def save_changes(self):
		selected = self.results_view.table.selectionModel().selectedRows()
		if not selected:
			return

		row = selected[0].row()
		
		for col in range(self.results_view.model.columnCount()):
			header = self.results_view.model.horizontalHeaderItem(col).text()
			widget = self.edit_view.fields.get(header)
			
			if isinstance(widget, QDateTimeEdit):
				checkbox = self.edit_view.fields[f'{header} Enabled']
				value = widget.dateTime().toString("dd-MM-yyyy") if checkbox.isChecked() else ""
			elif isinstance(widget, QCheckBox):
				value = "✓" if widget.isChecked() else ""
			elif isinstance(widget, NullableSpinBox):
				value = str(widget.value()) if widget.value() is not None else ''
			else:
				value = widget.text()
			
			self.results_view.model.setItem(row, col, QStandardItem(value))
			self.back_to_results()

	def back_to_results(self):
		# Refresh results (simulate re-running query)
		# self.populate_results()
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
				writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				
				# Write headers
				headers = [
					self.results_view.model.horizontalHeaderItem(i).text()
					for i in range(self.results_view.model.columnCount())
				]
				writer.writerow(headers)
				
				# Write data
				for row in range(self.results_view.model.rowCount()):
					row_data = [
						self.results_view.model.item(row, col).text()
						for col in range(self.results_view.model.columnCount())
					]
					writer.writerow(row_data)
					
		except Exception as e:
			print(f"Error exporting CSV: {str(e)}")

	def show_results(self):
		# Store current search parameters
		self.current_search_params = self.get_search_params()
		self.populate_results()
		
		self.search_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.new_entry_view.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		
		# Switch to results view
		self.stacked_widget.setCurrentIndex(2)

	def show_search(self):
		self.stacked_widget.setCurrentIndex(0)

	def get_search_params(self):
		"""Collect parameters from search fields"""
		filters = self.search_view.filters

		line_tpls      = [(key, filters[key].text()     ) for key in ['CX', 'ITEM', 'DESCRIÇÃO', 'RET.', 'EMPRESA', 'MICROFILME', 'OBSERVAÇÃO']]
		spin_box_tpls  = [(key, filters[key].value()    ) for key in ['ARQ.', 'EST.', 'PRAT.', 'DEST.']]
		checkbox_tpls  = [(key, filters[key].isChecked()) for key in ['DIG.', 'MIC.', 'Descarte']]

		date_checkbox = {}
		date_checkbox['DATA INÍCIO Start'] = date_checkbox['DATA INÍCIO End'] = filters['DATA INÍCIO Enabled'].isChecked()
		date_checkbox['DATA FIM Start']    = date_checkbox['DATA FIM End']    = filters['DATA FIM Enabled'].isChecked()
		date_checkbox['CONF. Start']       = date_checkbox['CONF. End']       = filters['CONF. Enabled'].isChecked()
		
		date_time_tpls = [
			(key, filters[key].dateTime().toString(Qt.ISODate) if date_checkbox[key] else None)
			for key in ['DATA INÍCIO Start', 'DATA INÍCIO End', 'DATA FIM Start', 'DATA FIM End', 'CONF. Start', 'CONF. End']
		]

		return {
			key: value
			for key, value in [*line_tpls, *spin_box_tpls, *checkbox_tpls, *date_time_tpls]
		}

	def populate_results(self):
		# Clear existing data
		self.results_view.clear()
		
		# Add dummy data
		from datetime import datetime
		for i in range(20):
			row = [
				QStandardItem(f"CX{i}"),
				QStandardItem(f"ITEM{i}"),
				QStandardItem(f"Description {i}"),
				QStandardItem(datetime.now().strftime("%d-%m-%Y")),
				QStandardItem(datetime.now().strftime("%d-%m-%Y")),
				QStandardItem(str(randint(0, 10))),
				QStandardItem(str(randint(1, 99))),
				QStandardItem(str(randint(1, 99))),
				QStandardItem("RET"),
				QStandardItem(str(randint(0, 40))),
				QStandardItem("✓" if randint(0, 1)%2 else ""),
				QStandardItem("✓" if randint(0, 1)%2 else ""),
				QStandardItem(datetime.now().strftime("%d-%m-%Y")),
				QStandardItem("Company"),
				QStandardItem("Microfilm"),
				QStandardItem("Observation"),
				QStandardItem("✓" if randint(0, 1)%2 else "")
			]
			self.results_view.model.appendRow(row)

		self.results_view.resize_to_contents()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
