
import re
from datetime import datetime
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QModelIndex

class NaturalSortProxyModel(QSortFilterProxyModel):
	_date_re   = re.compile(r"(\d{2}-\d{2}-\d{4})")
	_number_re = re.compile(r"(\d+)")

	def _parse_date(self, s: str):
		# s is "dd-mm-yyyy"
		return datetime.strptime(s, "%d-%m-%Y").date()

	def _key(self, s: str):
		"""
		Build a list of key‐elements from s, where each element is:
		 - a date.date() for dd-mm-yyyy substrings,
		 - an integer for digit runs,
		 - or a lowercase text chunk.
		"""
		key = []
		# First split on date substrings
		parts = self._date_re.split(s)
		for part in parts:
			if self._date_re.fullmatch(part):
				# it's a date
				key.append(self._parse_date(part))
			else:
				# no date here: split that chunk further by numbers
				subparts = self._number_re.split(part)
				for sub in subparts:
					if self._number_re.fullmatch(sub):
						key.append(int(sub))
					else:
						if sub:
							key.append(sub.lower())
		return key

	def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
		l = left.data(Qt.DisplayRole)
		r = right.data(Qt.DisplayRole)

		try:
			result = self._key(l) < self._key(r)
		except TypeError:
			result = str(self._key(l)) < str(self._key(r))

		return result
