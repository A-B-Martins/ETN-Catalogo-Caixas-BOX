
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QFormLayout, QSizePolicy
from PyQt5.QtCore import QDateTime

from .utils import setup_fields_dict, setup_field_groups_dict

class SearchView(QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		# Add top stretch to push content down
		self.layout.addStretch()
		
		# Create filter widgets for all columns
		self.filters = setup_fields_dict(True)

		# configure NullableSpinBox widgets
		for key in ['ARQ.', 'EST.', 'PRAT.', 'DEST.']:
			self.filters[key].setMaximum(999)

		# Initialize date widgets
		for key in ['DATA INÍCIO Start', 'DATA INÍCIO End', 'DATA FIM Start', 'DATA FIM End', 'CONF. Start', 'CONF. End']:
			self.filters[key].setCalendarPopup(True)
			self.filters[key].setDisplayFormat("dd-MM-yyyy")
			self.filters[key].setDateTime(QDateTime.currentDateTime())
			self.filters[key].setEnabled(False)  # Disabled by default

		# Link checkboxes to date widgets
		self.filters['DATA INÍCIO Enabled'].toggled.connect( lambda state: self.filters['DATA INÍCIO Start'].setEnabled(state) )
		self.filters['DATA INÍCIO Enabled'].toggled.connect( lambda state: self.filters['DATA INÍCIO End'  ].setEnabled(state) )
		self.filters['DATA FIM Enabled'   ].toggled.connect( lambda state: self.filters['DATA FIM Start'   ].setEnabled(state) )
		self.filters['DATA FIM Enabled'   ].toggled.connect( lambda state: self.filters['DATA FIM End'     ].setEnabled(state) )
		self.filters['CONF. Enabled'      ].toggled.connect( lambda state: self.filters['CONF. Start'      ].setEnabled(state) )
		self.filters['CONF. Enabled'      ].toggled.connect( lambda state: self.filters['CONF. End'        ].setEnabled(state) )

		# Group filters into sections
		groups = setup_field_groups_dict(True)

		# Create group boxes with width constraints
		for group_name, fields in groups.items():
			group = QGroupBox(group_name)
			flayout = QFormLayout()
			
			# Configure layout spacing
			flayout.setHorizontalSpacing(10)
			flayout.setVerticalSpacing(8)
			
			# Add fields to layout
			for field in fields:
				if isinstance(field, tuple):
					checkbox_key, *widget_keys = field
					hbox = QHBoxLayout()
					hbox.addWidget(self.filters[checkbox_key])
					for widget_key in widget_keys:
						hbox.addWidget(self.filters[widget_key])
					flayout.addRow(checkbox_key.replace(' Enabled', ''), hbox)
				else:
					flayout.addRow(field, self.filters[field])
			
			group.setLayout(flayout)
			group.setMaximumWidth(500)
			group.setMinimumWidth(450)
			
			# Prevent groups from expanding horizontally
			group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

			# Wrap group in centering layout
			group_container = QHBoxLayout()
			group_container.addStretch()
			group_container.addWidget(group)
			group_container.addStretch()

			self.layout.addLayout(group_container)

		# Add centered search button
		self.back_btn = QPushButton("Back")
		self.search_btn = QPushButton("Search")
		btn_layout = QHBoxLayout()
		btn_layout.addStretch()
		btn_layout.addWidget(self.back_btn)
		btn_layout.addWidget(self.search_btn)
		btn_layout.addStretch()
		self.layout.addLayout(btn_layout)

		# Add bottom stretch to push content up
		self.layout.addStretch()
