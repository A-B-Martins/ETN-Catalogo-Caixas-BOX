
from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QFormLayout, QSizePolicy,
	QLineEdit, QCheckBox
)

from .NullableSpinBox import NullableSpinBox
from .utils import setup_fields_dict, setup_field_groups_dict, HEADERS
from .models import db_col_restrictions_extended, text_fields_max_len

class EditView(QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		self.layout.addStretch()

		# Create field widgets
		self.fields = setup_fields_dict()

		# Configure date widgets
		date_fields = [HEADERS.DATA_INICIO, HEADERS.DATA_FIM, HEADERS.CONF]
		for field in date_fields:
			self.fields[field].setCalendarPopup(True)
			self.fields[field].setDisplayFormat("dd-MM-yyyy")
			self.fields[field].setEnabled(False)
			
			# Connect checkboxes to date fields
			checkbox = self.fields[f'{field} Enabled']
			checkbox.toggled.connect(self.fields[field].setEnabled)

		# Configure spinboxes
		for field in [HEADERS.ARQ, HEADERS.EST, HEADERS.PRAT, HEADERS.DEST]:
			self.fields[field].setMaximum(999)

		# Create groups
		groups = setup_field_groups_dict()

		# Create and add group boxes to container
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
					# Handle checkbox + date field pairs
					checkbox_key, date_key = field
					hbox = QHBoxLayout()
					hbox.addWidget(self.fields[checkbox_key])
					hbox.addWidget(self.fields[date_key])
					flayout.addRow(checkbox_key.replace(' Enabled', ''), hbox)
				else:
					flayout.addRow(field, self.fields[field])
			
			group.setLayout(flayout)
			group.setMaximumWidth(500)
			group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
			
			# Add group to container with horizontal centering
			group_wrapper = QHBoxLayout()
			group_wrapper.addStretch()
			group_wrapper.addWidget(group)
			group_wrapper.addStretch()
			container_layout.addLayout(group_wrapper)

			group.setMaximumWidth(500)
			group.setMinimumWidth(450)

		self.layout.addWidget(container)

		# Add max character limit for text fields
		for field_name, widget in self.fields.items():
			if isinstance(widget, QLineEdit) and text_fields_max_len[field_name]:
				widget.setMaxLength(text_fields_max_len[field_name])
		
		# Add control buttons
		self.save_btn = QPushButton("Salvar Mudanças")
		self.back_btn = QPushButton("Retornar")
		
		btn_layout = QHBoxLayout()
		btn_layout.addStretch()
		btn_layout.addWidget(self.back_btn)
		btn_layout.addWidget(self.save_btn)
		btn_layout.addStretch()
		self.layout.addLayout(btn_layout)
		self.layout.addStretch()

		# Connect field signals
		self.connect_field_signals()
		self.validate_form()  # Initial validation

	def connect_field_signals(self):
		"""Connect change signals for all input fields to validation"""
		for field_name, widget in self.fields.items():
			if isinstance(widget, QLineEdit):
				widget.textChanged.connect(self.validate_form)
			elif isinstance(widget, NullableSpinBox):
				widget.valueChanged.connect(self.validate_form)
			elif isinstance(widget, QCheckBox):
				widget.stateChanged.connect(self.validate_form)

	def validate_form(self):
		"""Validate form and enable/disable save button"""
		is_valid = True

		for field_name, widget in self.fields.items():
			is_nullable, max_len = db_col_restrictions_extended[field_name]

			if (
				(not is_nullable) and 
				(
					(isinstance(widget, QCheckBox) and not widget.isChecked()) or
					(isinstance(widget, NullableSpinBox) and (widget.value() == "" or widget.value() is None)) or
					(isinstance(widget, QLineEdit) and not widget.text())
				)
			):
				is_valid = False
				break

		# print(f"is_valid: {is_valid}")

		self.save_btn.setEnabled(is_valid)