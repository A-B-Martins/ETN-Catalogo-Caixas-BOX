import pandas as pd

columns = [
	'CX', 'ITEM', 'DESCRIÇÃO', 'DATA INÍCIO',
	'DATA FIM', 'ARQ.', 'EST.', 'PRAT.',
	'RET.', 'DEST.', 'DIG.', 'MIC.',
	'CONF.', 'EMPRESA', 'MICROFILME', 'OBSERVAÇÃO',
	'Descarte'
]

def check_length(excel_path):
	df = pd.read_excel(excel_path)
	longest_row = {col: 0 for col in columns}

	for _, row in df.iterrows():
		for col in columns:
			if (length:=len(str(row[col]))) > longest_row[col]: longest_row[col] = length

	return longest_row

if __name__ == '__main__':
	r = check_length('Cópia de Catálogo_Caixas BOX.xls')