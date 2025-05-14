
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QFormLayout
from PyQt5.QtCore import QDateTime

from .utils import setup_fields_dict, setup_field_groups_dict

class NewEntryView(QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		self.layout.addStretch()

		# Create field widgets
		self.fields = setup_fields_dict()

		# Configure date widgets
		date_fields = ['DATA INÍCIO', 'DATA FIM', 'CONF.']
		for field in date_fields:
			self.fields[field].setCalendarPopup(True)
			self.fields[field].setDisplayFormat("dd-MM-yyyy")
			self.fields[field].setDateTime(QDateTime.currentDateTime())
			self.fields[field].setEnabled(False)
			self.fields[f'{field} Enabled'].toggled.connect(self.fields[field].setEnabled)

		# Configure spinboxes
		for field in ['ARQ.', 'EST.', 'PRAT.', 'DEST.']:
			self.fields[field].setMaximum(999)

		# Create groups
		groups = setup_field_groups_dict()

		# Add groups to layout
		container = QWidget()
		container_layout = QVBoxLayout()
		container.setLayout(container_layout)

		for group_name, fields in groups.items():
			group = QGroupBox(group_name)
			flayout = QFormLayout()
			flayout.setHorizontalSpacing(10)
			flayout.setVerticalSpacing(8)
			
			for field in fields:
				if isinstance(field, tuple):
					checkbox_key, date_key = field
					hbox = QHBoxLayout()
					hbox.addWidget(self.fields[checkbox_key])
					hbox.addWidget(self.fields[date_key])
					flayout.addRow(checkbox_key.replace(' Enabled', ''), hbox)
				else:
					flayout.addRow(field, self.fields[field])
			
			group.setLayout(flayout)
			group.setMaximumWidth(500)
			group.setMinimumWidth(450)

			group_wrapper = QHBoxLayout()
			group_wrapper.addStretch()
			group_wrapper.addWidget(group)
			group_wrapper.addStretch()
			
			container_layout.addLayout(group_wrapper)

		self.layout.addWidget(container)
		
		# Add control buttons
		self.back_btn = QPushButton("Back")
		self.save_btn = QPushButton("Save New Entry")
		
		btn_layout = QHBoxLayout()
		btn_layout.addStretch()
		btn_layout.addWidget(self.back_btn)
		btn_layout.addWidget(self.save_btn)
		btn_layout.addStretch()
		self.layout.addLayout(btn_layout)
		self.layout.addStretch()
