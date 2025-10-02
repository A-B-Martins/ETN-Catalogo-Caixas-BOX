
from enum import StrEnum
from functools import reduce

from PyQt5.QtWidgets import QLineEdit, QCheckBox, QDateTimeEdit
from .NullableSpinBox import NullableSpinBox

from peewee import *

class HEADERS(StrEnum):
	CX = "CAIXA"
	ITEM = "ITEM"
	DESCRICAO = "DESCRIÇÃO"
	RET = "RETENÇÃO"
	DEST = 'DESTINAÇÃO'
	
	DATA_INICIO = 'DATA INÍCIO'
	DATA_INICIO_ENABLED = DATA_INICIO + ' Enabled'
	DATA_INICIO_START = DATA_INICIO + ' Start'
	DATA_INICIO_END = DATA_INICIO + ' End'
	
	DATA_FIM = 'DATA FIM'
	DATA_FIM_ENABLED = DATA_FIM + ' Enabled'
	DATA_FIM_START = DATA_FIM + ' Start'
	DATA_FIM_END = DATA_FIM + ' End'
	
	CONF = 'CONFERÊNCIA'
	CONF_ENABLED = CONF + ' Enabled'
	CONF_START = CONF + ' Start'
	CONF_END = CONF + ' End'

	LOCAL_GUARDA = "LOCAL DE GUARDA"
	ARQ = 'ARQUIVO DESLIZANTE'
	EST = 'ESTANTE'
	PRAT = 'PRATELEIRA'

	DIG = 'DIGITALIZADO'
	DIG_SIM = DIG + ' Sim'
	DIG_NAO = DIG + ' Não'

	MIC = 'MICROFILMADO'
	MIC_SIM = MIC + ' Sim'
	MIC_NAO = MIC + ' Não'
	
	DESCARTE = 'DESCARTE'
	DESCARTE_SIM = DESCARTE + ' Sim'
	DESCARTE_NAO = DESCARTE + ' Não'

	MICROFILME = "MICROFILME"
	EMPRESA = "EMPRESA"
	
	OBSERVACAO = "OBSERVAÇÃO"

def setup_fields_dict(search:bool=False):
	# QLineEdit()
	line = [HEADERS.CX, HEADERS.ITEM, HEADERS.DESCRICAO, HEADERS.RET, HEADERS.EMPRESA, HEADERS.MICROFILME, HEADERS.OBSERVACAO, HEADERS.LOCAL_GUARDA]
	# QCheckBox()
	checkbox = [HEADERS.DATA_INICIO_ENABLED, HEADERS.DATA_FIM_ENABLED, HEADERS.CONF_ENABLED, HEADERS.DIG, HEADERS.MIC, HEADERS.DESCARTE] if not search else [HEADERS.DATA_INICIO_ENABLED, HEADERS.DATA_FIM_ENABLED, HEADERS.CONF_ENABLED, HEADERS.DIG_SIM, HEADERS.DIG_NAO, HEADERS.MIC_SIM, HEADERS.MIC_NAO, HEADERS.DESCARTE_SIM, HEADERS.DESCARTE_NAO]
	# QDateTimeEdit
	date_time = [HEADERS.DATA_INICIO, HEADERS.DATA_FIM, HEADERS.CONF] if not search else [HEADERS.DATA_INICIO_START, HEADERS.DATA_FIM_START, HEADERS.DATA_INICIO_END, HEADERS.DATA_FIM_END, HEADERS.CONF_START, HEADERS.CONF_END]
	# NullableSpinBox()
	spin_box = [HEADERS.ARQ, HEADERS.EST, HEADERS.PRAT, HEADERS.DEST]

	fields = {}
	for tpl in [(line, QLineEdit), (checkbox, QCheckBox), (date_time, QDateTimeEdit), (spin_box, NullableSpinBox)]:
		lst, fnct = tpl
		for item in lst:
			fields[item] = fnct()

	return fields

def setup_field_groups_dict(search:bool=False):
	return {
		'Dados Primários': [HEADERS.CX, HEADERS.ITEM, HEADERS.DESCRICAO, HEADERS.RET, HEADERS.DEST],
		'Datas': [
			(HEADERS.DATA_INICIO_ENABLED, HEADERS.DATA_INICIO) if not search else (HEADERS.DATA_INICIO_ENABLED, HEADERS.DATA_INICIO_START, HEADERS.DATA_INICIO_END),
			(HEADERS.DATA_FIM_ENABLED, HEADERS.DATA_FIM) if not search else (HEADERS.DATA_FIM_ENABLED, HEADERS.DATA_FIM_START, HEADERS.DATA_FIM_END),
			(HEADERS.CONF_ENABLED, HEADERS.CONF) if not search else (HEADERS.CONF_ENABLED, HEADERS.CONF_START, HEADERS.CONF_END)
		],
		'Local de Guarda': [HEADERS.LOCAL_GUARDA, HEADERS.ARQ, HEADERS.EST, HEADERS.PRAT],
		'Controle': [HEADERS.DIG, HEADERS.MIC, HEADERS.DESCARTE, HEADERS.MICROFILME, HEADERS.EMPRESA] if not search else [
			{'dual_checkbox': True, 'field_name': HEADERS.DIG, 'sim_key': HEADERS.DIG_SIM, 'nao_key': HEADERS.DIG_NAO},
			{'dual_checkbox': True, 'field_name': HEADERS.MIC, 'sim_key': HEADERS.MIC_SIM, 'nao_key': HEADERS.MIC_NAO},
			{'dual_checkbox': True, 'field_name': HEADERS.DESCARTE, 'sim_key': HEADERS.DESCARTE_SIM, 'nao_key': HEADERS.DESCARTE_NAO},
			HEADERS.MICROFILME,
			HEADERS.EMPRESA
		],
		'Dados Adicionais': [HEADERS.OBSERVACAO]
	}

# postgres
def build_query(model, filters):
	"""
	Builds dynamic Peewee WHERE clause for PostgreSQL from dictionary
	
	Structure:
	{
		'field': value,                     # Equality
		'field__operator': value,            # Custom operator
		'_or': [                             # OR group
			{'field1': value1},
			{'field2__gt': value2}
		],
		'_not': {'field': value}             # NOT condition
	}
	"""
	conditions = []
	
	# Extended operator map with PostgreSQL-specific options
	operator_map = {
		# Standard operators
		'eq': lambda f, v: f == v,
		'gt': lambda f, v: f > v,
		'lt': lambda f, v: f < v,
		'gte': lambda f, v: f >= v,
		'lte': lambda f, v: f <= v,
		'ne': lambda f, v: f != v,
		'like': lambda f, v: f ** v,
		'ilike': lambda f, v: f.ilike(v),   # PostgreSQL case-insensitive LIKE
		'in': lambda f, v: f.in_(v),
		'contains': lambda f, v: f.contains(v),  # For arrays/hstore
		'contained_by': lambda f, v: f.contained_by(v),
		'overlap': lambda f, v: f.overlap(v),    # For arrays
		'regex': lambda f, v: f.regexp(v),    # Regular expression match
		'iregex': lambda f, v: f.iregexp(v),  # Case-insensitive regex
		'has_key': lambda f, v: f.has_key(v),  # For hstore/JSON
		'json_contains': lambda f, v: f.json_contains(v),
		'json_contained': lambda f, v: f.json_contained_by(v),
		# Add more PostgreSQL-specific operators as needed
	}

	for key, value in filters.items():
		# Skip None values
		if value is None:
			continue
			
		# Handle OR groups
		if key == '_or':
			or_conditions = [build_postgres_query(model, subfilters).where_clause
							 for subfilters in value]
			if or_conditions:
				conditions.append(reduce(operator.or_, or_conditions))
			continue
			
		# Handle NOT conditions
		if key == '_not':
			for subfield, subvalue in value.items():
				if '__' in subfield:
					field_name, operator = subfield.split('__', 1)
				else:
					field_name, operator = subfield, 'eq'
				field = getattr(model, field_name)
				condition = operator_map.get(operator, operator_map['eq'])(field, subvalue)
				conditions.append(~condition)
			continue
			
		# Handle field operators
		if '__' in key:
			field_name, operator = key.split('__', 1)
		else:
			field_name, operator = key, 'eq'
			
		try:
			field = getattr(model, field_name)
		except AttributeError:
			raise ValueError(f"Field '{field_name}' does not exist in model {model.__name__}")
		
		# Get operator function (default to equality)
		op_func = operator_map.get(operator, operator_map['eq'])
		conditions.append(op_func(field, value))
	print(conditions)
	return model.select().where(*conditions)

	# # PostgreSQL-Specific Features to Note:
	# # 1. Case-Insensitive Matching:
	# Use ilike instead of like for case-insensitive search
	# filters = {'name__ilike': 'john%'}

	# # 2. Array Operators (if using ArrayField):
	# filters = {
	# 	'tags__contains': ['python', 'postgres'],  # Array contains all elements
	# 	'ids__overlap': [1, 2, 3]                 # Array overlaps with
	# }

	# # 3. JSON/JSONB Operators:
	# filters = {
	# 	'metadata__has_key': 'email',          # JSON has key
	#    'settings__json_contains': {'dark_mode': True}
	# }

	# # 4. Regular Expressions:
	# filters = {
	# 	'name__regex': '^[A-Z]',     # POSIX regex
	# 	'email__iregex': '@gmail\.'   # Case-insensitive regex
	# }

	# # Example Usage with PostgreSQL:
	# # Define a model with PostgreSQL-specific fields
	# class User(Model):
	# 	name = CharField()
	# 	email = CharField()
	# 	age = IntegerField()
	# 	tags = ArrayField(CharField)  # PostgreSQL array
	# 	metadata = JSONField()        # PostgreSQL JSONB
	# 	created_at = DateTimeField()

	# 	class Meta:
	# 		database = db  # Your PostgreSQL database connection

	# # Complex query using PostgreSQL features
	# filters = {
	# 	'age__gte': 18,
	# 	'name__ilike': '%john%',
	# 	'tags__contains': ['verified'],
	# 	'metadata__has_key': 'phone',
	# 	'_or': [
	# 		{'email__iregex': '@gmail\.com$'},
	# 		{'email__iregex': '@yahoo\.com$'}
	# 	],
	# 	'_not': {'tags__contains': ['banned']}
	# }

	# query = build_postgres_query(User, filters)

	# # See generated SQL
	# print(query.sql())

	# # Execute query
	# for user in query:
	# 	print(user.name, user.email)

def update_record(record, update_data, skip_none=False):
	"""
	Dynamically update a Peewee record instance with dictionary data
	Skips unchanged values to optimize database updates
	
	:param record: Peewee model instance to update
	:param update_data: Dict of {field_name: new_value}
	:param skip_none: Whether to skip None values (default: True)
	:return: Updated record instance
	"""
	fields_to_update = []
	
	for field_name, new_value in update_data.items():
		# Get current value
		current_value = getattr(record, field_name)
		
		# Handle None values
		if skip_none and new_value is None:
			continue
			
		# Check for value changes
		if current_value != new_value:
			setattr(record, field_name, new_value)
			fields_to_update.append(field_name)
	
	if fields_to_update:
		# Save only changed fields
		record.save(only=fields_to_update)
	
	return record