from peewee import *
from datetime import datetime
from .database import db
from .utils import HEADERS

# Primary data
CX_MAX_LEN = 16
CX_NULL = False

ITEM_MAX_LEN = 128
ITEM_NULL = False

DESCRICAO_MAX_LEN = None
DESCRICAO_NULL = False

RET_MAX_LEN = 8
RET_NULL = False

DEST_NULL = False

# Dates
DATA_INICIO_NULL = True
DATA_FIM_NULL = True
CONF_NULL = True

# Custody location
LOCAL_GUARDA_MAX_LEN = 64
LOCAL_GUARDA_NULL = True

ARQ_NULL = True
EST_NULL = True
PRAT_NULL = True

# Control
DIG_NULL = True
MIC_NULL = True
DESCARTE_NULL = True

MICROFILME_MAX_LEN = 64
MICROFILME_NULL = True

EMPRESA_MAX_LEN = 32
EMPRESA_NULL = True

# Additional data
OBSERVACAO_MAX_LEN = None
OBSERVACAO_NULL = True

db_col_restrictions = {
	# Text fields
	HEADERS.CX: (CX_NULL, CX_MAX_LEN), HEADERS.ITEM: (ITEM_NULL, ITEM_MAX_LEN), HEADERS.DESCRICAO: (DESCRICAO_NULL, DESCRICAO_MAX_LEN), HEADERS.LOCAL_GUARDA: (LOCAL_GUARDA_NULL, LOCAL_GUARDA_MAX_LEN),
	HEADERS.RET: (RET_NULL, RET_MAX_LEN), HEADERS.EMPRESA: (EMPRESA_NULL, EMPRESA_MAX_LEN), HEADERS.MICROFILME: (MICROFILME_NULL, MICROFILME_MAX_LEN), HEADERS.OBSERVACAO: (OBSERVACAO_NULL, OBSERVACAO_MAX_LEN),
	# Date fields
	HEADERS.DATA_INICIO: (DATA_INICIO_NULL, None), HEADERS.DATA_FIM: (DATA_FIM_NULL, None), HEADERS.CONF: (CONF_NULL, None),
	# Integer fields
	HEADERS.ARQ: (ARQ_NULL, None), HEADERS.EST: (EST_NULL, None), HEADERS.PRAT: (PRAT_NULL, None), HEADERS.DEST: (DEST_NULL, None),
	# Boolean fields
	HEADERS.DIG: (DIG_NULL, None), HEADERS.MIC: (MIC_NULL, None), HEADERS.DESCARTE: (DESCARTE_NULL, None)
}

db_col_restrictions_extended = {
	**db_col_restrictions,
	HEADERS.DATA_INICIO_ENABLED: (DATA_INICIO_NULL, None), HEADERS.DATA_FIM_ENABLED: (DATA_FIM_NULL, None), HEADERS.CONF_ENABLED: (CONF_NULL, None),
}

text_fields_max_len = {
	HEADERS.CX: CX_MAX_LEN, HEADERS.ITEM: ITEM_MAX_LEN, HEADERS.DESCRICAO: DESCRICAO_MAX_LEN,
	HEADERS.RET: RET_MAX_LEN, HEADERS.EMPRESA: EMPRESA_MAX_LEN, HEADERS.MICROFILME: MICROFILME_MAX_LEN,
	HEADERS.OBSERVACAO: OBSERVACAO_MAX_LEN, HEADERS.LOCAL_GUARDA: LOCAL_GUARDA_MAX_LEN
}

def filter_params(params):
	return {key: value for key, value in params.items() if value}

class BaseModel(Model):
	class Meta:
		database = db

class ArchiveBox(BaseModel):
	cx = CharField(**filter_params({'max_length': CX_MAX_LEN, 'null': CX_NULL}))
	item = CharField(**filter_params({'max_length': ITEM_MAX_LEN, 'null': ITEM_NULL}))
	descricao = TextField(**filter_params({'max_length': DESCRICAO_MAX_LEN, 'null': DESCRICAO_NULL}))
	ret = CharField(**filter_params({'max_length': RET_MAX_LEN, 'null': RET_NULL}))
	dest = IntegerField(**filter_params({'null': DEST_NULL}))
	
	data_inicio = DateTimeField(**filter_params({'null': DATA_INICIO_NULL}))
	data_fim = DateTimeField(**filter_params({'null': DATA_FIM_NULL}))
	conf = DateTimeField(**filter_params({'null': CONF_NULL}))
	
	local_guarda = CharField(**filter_params({'max_length': LOCAL_GUARDA_MAX_LEN, 'null': LOCAL_GUARDA_NULL}))
	arq = IntegerField(**filter_params({'null': ARQ_NULL}))
	est = IntegerField(**filter_params({'null': EST_NULL}))
	prat = IntegerField(**filter_params({'null': PRAT_NULL}))
	
	dig = BooleanField(**filter_params({'null': DIG_NULL}))
	mic = BooleanField(**filter_params({'null': MIC_NULL}))
	descarte = BooleanField(**filter_params({'null': DESCARTE_NULL}))
	microfilme = CharField(**filter_params({'max_length': MICROFILME_MAX_LEN, 'null': MICROFILME_NULL}))
	empresa = CharField(**filter_params({'max_length': EMPRESA_MAX_LEN, 'null': EMPRESA_NULL}))

	observacao = TextField(**filter_params({'max_length': OBSERVACAO_MAX_LEN, 'null': OBSERVACAO_NULL}))

	class Meta:
		table_name = 'archive_boxes'


# class ArchiveBox(BaseModel):
# 	cx = CharField(max_length=16)
# 	item = CharField(max_length=128)
# 	descricao = TextField()
	
# 	data_inicio = DateTimeField(null=True)
# 	data_fim = DateTimeField(null=True)
# 	conf = DateTimeField(null=True)
	
# 	arq = IntegerField()
# 	est = IntegerField()
# 	prat = IntegerField(null=True)
# 	dest = IntegerField(null=True)
	
# 	dig = BooleanField()
# 	mic = BooleanField()
# 	descarte = BooleanField()

# 	ret = CharField(max_length=8)
# 	empresa = CharField(max_length=32)
# 	microfilme = CharField(max_length=64)
# 	observacao = TextField()

# 	class Meta:
# 		table_name = 'archive_boxes'
