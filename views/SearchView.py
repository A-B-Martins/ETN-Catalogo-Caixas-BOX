
from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QFormLayout, QSizePolicy,
	QLabel, QLineEdit, QCheckBox
)

from PyQt5.QtCore import QDateTime

from .utils import setup_fields_dict, setup_field_groups_dict, HEADERS
from .NullableSpinBox import NullableSpinBox
from .models import text_fields_max_len

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
		for key in [HEADERS.ARQ, HEADERS.EST, HEADERS.PRAT, HEADERS.DEST]:
			self.filters[key].setMaximum(999)

		# Initialize date widgets
		for key in [HEADERS.DATA_INICIO_START, HEADERS.DATA_INICIO_END, HEADERS.DATA_FIM_START, HEADERS.DATA_FIM_END, HEADERS.CONF_START, HEADERS.CONF_END]:
			self.filters[key].setCalendarPopup(True)
			self.filters[key].setDisplayFormat("dd-MM-yyyy")
			self.filters[key].setDateTime(QDateTime.currentDateTime())
			self.filters[key].setEnabled(False)  # Disabled by default

		# Link checkboxes to date widgets
		self.filters[HEADERS.DATA_INICIO_ENABLED].toggled.connect( lambda state: self.filters[HEADERS.DATA_INICIO_START].setEnabled(state) )
		self.filters[HEADERS.DATA_INICIO_ENABLED].toggled.connect( lambda state: self.filters[HEADERS.DATA_INICIO_END  ].setEnabled(state) )
		self.filters[HEADERS.DATA_FIM_ENABLED   ].toggled.connect( lambda state: self.filters[HEADERS.DATA_FIM_START   ].setEnabled(state) )
		self.filters[HEADERS.DATA_FIM_ENABLED   ].toggled.connect( lambda state: self.filters[HEADERS.DATA_FIM_END     ].setEnabled(state) )
		self.filters[HEADERS.CONF_ENABLED       ].toggled.connect( lambda state: self.filters[HEADERS.CONF_START       ].setEnabled(state) )
		self.filters[HEADERS.CONF_ENABLED       ].toggled.connect( lambda state: self.filters[HEADERS.CONF_END         ].setEnabled(state) )

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
				elif isinstance(field, dict) and 'dual_checkbox' in field:
					# Handle dual checkbox fields (DIG., MIC., Descarte)
					field_name = field['field_name']
					sim_key = field['sim_key']
					nao_key = field['nao_key']
					
					hbox = QHBoxLayout()
					
					# Add "Sim" checkbox with label
					sim_label = QLabel("Sim")
					hbox.addWidget(sim_label)
					hbox.addWidget(self.filters[sim_key])
					
					# Add some spacing
					hbox.addSpacing(20)
					
					# Add "Não" checkbox with label
					nao_label = QLabel("Não")
					hbox.addWidget(nao_label)
					hbox.addWidget(self.filters[nao_key])
					
					# Add stretch to push checkboxes to the left
					hbox.addStretch()
					
					flayout.addRow(field_name, hbox)
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

		# Add max character limit for text fields
		for field_name, widget in self.filters.items():
			if isinstance(widget, QLineEdit) and text_fields_max_len[field_name]:
				widget.setMaxLength(text_fields_max_len[field_name])

		# Add centered search button
		self.back_btn = QPushButton("Retornar")
		self.search_btn = QPushButton("Buscar")
		btn_layout = QHBoxLayout()
		btn_layout.addStretch()
		btn_layout.addWidget(self.back_btn)
		btn_layout.addWidget(self.search_btn)
		btn_layout.addStretch()
		self.layout.addLayout(btn_layout)

		# Add bottom stretch to push content up
		self.layout.addStretch()

		# Connect field signals
		self.connect_field_signals()
		self.validate_form()  # Initial validation

	def connect_field_signals(self):
		"""Connect change signals for all input fields to validation"""
		for field_name, widget in self.filters.items():
			if isinstance(widget, QLineEdit):
				widget.textChanged.connect(self.validate_form)
			elif isinstance(widget, NullableSpinBox):
				widget.valueChanged.connect(self.validate_form)
			elif isinstance(widget, QCheckBox):
				widget.stateChanged.connect(self.validate_form)

	def validate_form(self):
		"""Validate form and enable/disable save button"""
		is_valid = False

		for field_name, widget in self.filters.items():
			if (
				(isinstance(widget, QCheckBox) and widget.isChecked()) or
				(isinstance(widget, NullableSpinBox) and not (widget.value() == "" or widget.value() is None)) or
				(isinstance(widget, QLineEdit) and widget.text())
			):
				is_valid = True
				break

		# print(f"is_valid: {is_valid}")

		self.search_btn.setEnabled(is_valid)