
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtGui import QValidator

class NullableSpinBox(QSpinBox):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._is_null = True
		self.lineEdit().setText("")
		self.setMinimum(0)
		self.setMaximum(999)

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
			# else: keep null
			event.accept()
			return

		# If at 0 and scroll-down → back to null
		if not self._is_null and super().value() == self.minimum() and delta < 0:
			self._is_null = True
			self.lineEdit().setText("")
			event.accept()
			return

		# Otherwise, default behavior
		super().wheelEvent(event)
