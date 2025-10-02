
from PyQt5.QtWidgets import QSpinBox, QAbstractSpinBox
from PyQt5.QtGui import QValidator

class NullableSpinBox(QSpinBox):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._is_null = True
		self.lineEdit().setText("")
		self.setMinimum(0)
		self.setMaximum(999)

		self.lineEdit().textChanged.connect(self._handle_text_changed)

	def value(self):
		return None if self._is_null else super().value()

	def textFromValue(self, value):
		return "" if self._is_null else str(value)

	def valueFromText(self, text):
		text = text.strip()
		if text == "":
			self._is_null = True
			return self.minimum()  # dummy
		self._is_null = False
		return int(text)

	def validate(self, text, pos):
		if text.strip() == "":
			return (QValidator.Intermediate, text, pos)
		return super().validate(text, pos)

	def focusOutEvent(self, event):
		if self.lineEdit().text().strip() == "":
			self._is_null = True
			self.lineEdit().setText("")
		else:
			self._is_null = False
		super().focusOutEvent(event)

	def setValue(self, value):
		if value is None:
			self._is_null = True
			self.lineEdit().setText("")
			super().valueChanged.emit(-1)
		else:
			self._is_null = False
			super().setValue(value)

	def wheelEvent(self, event):
		delta = event.angleDelta().y()
		# If currently empty, scroll-up → go to 0
		if self._is_null:
			if delta > 0:
				self._is_null = False
				super().setValue(self.minimum())
				super().valueChanged.emit(0)
			# else: keep null
			event.accept()
			return

		# If at 0 and scroll-down → back to null
		if not self._is_null and super().value() == self.minimum() and delta < 0:
			self._is_null = True
			self.setValue(None)
			self.lineEdit().setText("")
			event.accept()
			return

		# Otherwise, default behavior
		super().wheelEvent(event)

	def stepBy(self, steps):
		# print(f"is_null: {self._is_null} | value: {super().value()} | minimum: {self.minimum()} | steps: {steps}")
		
		if self._is_null:
			if steps > 0:
				self._is_null = False
				super().setValue(self.minimum())
				super().valueChanged.emit(0)
			return

		if not self._is_null and super().value() == self.minimum() and steps < 0:
			self._is_null = True
			self.setValue(None)
			self.lineEdit().setText("")
			return

		super().stepBy(steps)

	def stepEnabled(self):
		if self._is_null:
			# Only allow step up (to minimum value)
			return QAbstractSpinBox.StepUpEnabled
		else:
			# Allow both directions at minimum value
			# (to enable stepping down to null)
			if super().value() == self.minimum():
				return QAbstractSpinBox.StepUpEnabled | QAbstractSpinBox.StepDownEnabled
			# Default behavior for other values
			return super().stepEnabled()

	def _handle_text_changed(self, text):
		"""Update null state when text changes"""
		if text.strip() == "":
			self._is_null = True
			self.setValue(None)
		elif int(text.strip()) == 0:
			self._is_null = False
			self.setValue(0)
