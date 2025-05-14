
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QDateTimeEdit

from .NullableSpinBox import NullableSpinBox

def setup_fields_dict(search:bool=False):
	# QLineEdit()
	line = ['CX', 'ITEM', 'DESCRIÇÃO', 'RET.', 'EMPRESA', 'MICROFILME', 'OBSERVAÇÃO']
	# QCheckBox()
	checkbox = ['DATA INÍCIO Enabled', 'DATA FIM Enabled', 'CONF. Enabled', 'DIG.', 'MIC.', 'Descarte']
	# QDateTimeEdit
	date_time = ['DATA INÍCIO', 'DATA FIM', 'CONF.'] if not search else ['DATA INÍCIO Start', 'DATA FIM Start', 'DATA INÍCIO End', 'DATA FIM End', 'CONF. Start', 'CONF. End']
	# NullableSpinBox()
	spin_box = ['ARQ.', 'EST.', 'PRAT.', 'DEST.']

	fields = {}
	for tpl in [(line, QLineEdit), (checkbox, QCheckBox), (date_time, QDateTimeEdit), (spin_box, NullableSpinBox)]:
		lst, fnct = tpl
		for item in lst:
			fields[item] = fnct()

	return fields

def setup_field_groups_dict(search:bool=False):
	return {
		'Basic Information': ['CX', 'ITEM', 'DESCRIÇÃO'],
		'Dates': [
			('DATA INÍCIO Enabled', 'DATA INÍCIO') if not search else ('DATA INÍCIO Enabled', 'DATA INÍCIO Start', 'DATA INÍCIO End'),
			('DATA FIM Enabled', 'DATA FIM') if not search else ('DATA FIM Enabled', 'DATA FIM Start', 'DATA FIM End'),
			('CONF. Enabled', 'CONF.') if not search else ('CONF. Enabled', 'CONF. Start', 'CONF. End')
		],
		'Numerical Data': ['ARQ.', 'EST.', 'PRAT.', 'DEST.'],
		'Status Flags': ['DIG.', 'MIC.', 'Descarte'],
		'Additional Information': ['RET.', 'EMPRESA', 'MICROFILME', 'OBSERVAÇÃO']
	}
