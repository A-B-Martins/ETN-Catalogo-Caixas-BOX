from views.database import db
from views.models import ArchiveBox
from views.database import *

import pandas as pd

from datetime import datetime, timezone, timedelta
import re

columns = [
	'CX', 'ITEM', 'DESCRIÇÃO', 'DATA INÍCIO',
	'DATA FIM', 'ARQ.', 'EST.', 'PRAT.',
	'RET.', 'DEST.', 'DIG.', 'MIC.',
	'CONF.', 'EMPRESA', 'MICROFILME', 'OBSERVAÇÃO',
	'Descarte'
]

def date(date:str, date_format:str='%Y-%m-%d'):
	return datetime.strptime(date, date_format).replace(tzinfo=timezone(timedelta(hours=-3)))

def parse_date_abb(date_str):
	month_translation = {
		# Portuguese abbreviations and full names
		'JANEIRO': 'Jan', 'FEVEREIRO': 'Feb', 'MARÇO': 'Mar', 'ABRIL': 'Apr',
		'MAIO': 'May', 'JUNHO': 'Jun', 'JULHO': 'Jul', 'AGOSTO': 'Aug',
		'SETEMBRO': 'Sep', 'OUTUBRO': 'Oct', 'NOVEMBRO': 'Nov', 'DEZEMBRO': 'Dec',

		'JAN': 'Jan', 'FEV': 'Feb', 'MAR': 'Mar', 'ABR': 'Apr',
		'MAI': 'May', 'JUN': 'Jun', 'JUL': 'Jul', 'AGO': 'Aug',
		'SET': 'Sep', 'OUT': 'Oct', 'NOV': 'Nov', 'DEZ': 'Dec',
		'AGT': 'Aug',
		
		# German variations
		'JÄNNER': 'Jan', 'JANEIRO': 'Jan', 'FEBRERO': 'Feb', 'MÄRZEN': 'Mar', 
		'APRIL': 'Apr', 'AUGUST': 'Aug', 'SEPTEMBER': 'Sep', 'OKTOVER': 'Oct',
		'OKTOBER': 'Oct', 'NOVEMBER': 'Nov', 'DEZEMBER': 'Dec',
		'MAI': 'May', 'JUNI': 'Jun', 'JULI': 'Jul', 
		
		# English full month names
		'JANUARY': 'Jan', 'FEBRUARY': 'Feb', 'MARCH': 'Mar', 'APRIL': 'Apr', 
		'MAY': 'May', 'JUNE': 'Jun', 'JULY': 'Jul', 'AUGUST': 'Aug', 
		'SEPTEMBER': 'Sep', 'OCTOBER': 'Oct', 'NOVEMBER': 'Nov', 'DECEMBER': 'Dec'
	}

	def normalize_date_str(date_str):
		# Normalize the input string
		# Remove any extra whitespace
		date_str = date_str.strip()
		
		# Try to find the month in the string
		for foreign, english in month_translation.items():
			if foreign.upper() in date_str.upper():
				# Replace the month with its standard abbreviation
				date_str = date_str.upper().replace(foreign.upper(), english)
				break
		
		# Handle different separator formats
		date_str = re.sub(r'([\s-]|[\s/])+', '/', date_str)
		
		return date_str

	def parse_year(year_str):
		# Convert two-digit years to four-digit years
		year = int(year_str)
		if 0 <= year <= 25:
			return 2000 + year
		elif 26 <= year <= 99:
			return 1900 + year
		return year

	try:
		# Normalize the date string
		normalized_date_str = normalize_date_str(date_str)
		# print(normalized_date_str)
		
		# Try different parsing formats
		parsing_formats = [
			"%b/%Y",   # Jan/2024
			"%b/%y",   # Jan/24
			"%b%Y",    # Jan2024
			"%b%y"     # Jan24
		]
		
		for fmt in parsing_formats:
			try:
				# Attempt to parse the date with the current format
				parsed_date = datetime.strptime(normalized_date_str, fmt).replace(tzinfo=timezone(timedelta(hours=-3)))
				return parsed_date
			except ValueError:
				continue
		
		# If no format works, raise an error
		raise ValueError(f"Unable to parse date: {date_str}")
	
	except ValueError as e:
		raise ValueError(f"Invalid date format: {date_str}") from e

def parse_date(date_str):
	final_date = None

	if date_str:
		date_str = date_str.replace(" ", "")
		try:
			regex_list = [
				# mm/YYYY; mmYYYY; dd/mmyy
				(r"(?<=^)[0-9]{1,2}[./-]+[0-9]{4}(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", date_str), (lambda clean_str: "%d%m%y" if int(clean_str[0:2]) > 12 or int(clean_str[2:]) < 1950 else "%m%Y")(re.sub(r"[./\-]", "", date_str))) , None),
				# dd/mm/YYYY; ddmmYYY
				(r"(?<=^)(([0-9]{1,2}[./-]+){2}|([0-9]{1,2}){2})[0-9]{4}(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", date_str), "%d%m%Y"), None),
				# dd/mmYYYY
				(r"(?<=^)[0-9]{2}[./-]+[0-9]{2}[0-9]{4}(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", date_str), "%d%m%Y"), None),
				# ddmm/YYYY
				(r"(?<=^)[0-9]{2}[0-9]{2}[./-]+[0-9]{4}(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", date_str), "%d%m%Y"), None),
				# YYYY/mm/dd
				(r"(?<=^)[0-9]{4}[./-]+[0-9]{1,2}[./-]+[0-9]{1,2}(?=$)", lambda date_str, format_str: date(re.sub(r"[./\-]", "", date_str), format_str), ["%Y%m%d", "%Y%d%m"]),
				# dd/mm/yy
				(r"(?<=^)([0-9]{1,2}[./-]+){2}[0-9]{2}(?=$)", lambda date_str: date((lambda clean_str, year: f"{clean_str[:4]}{'19' + year if int(year) > 25 else '20' + year}")(re.sub( r'[./\-]', '', date_str), date_str[-2:]), "%d%m%Y"), None),
				# ddmm/yy
				(r"(?<=^)[0-9]{2}[0-9]{2}[./-]+[0-9]{2}(?=$)", lambda date_str: date((lambda clean_str, year: f"{clean_str[:4]}{'19' + year if int(year) > 25 else '20' + year}")(re.sub( r'[./\-]', '', date_str), date_str[-2:]), "%d%m%Y"), None),
				# YYYY
				(r"(?<=^)[0-9]{4}(?=$)", lambda date_str: date(date_str, "%Y"), None),
				# até YYYY
				(r"(?i)(?<=^)até\s*[0-9]{4}(?=$)", lambda date_str: date(re.sub(r"(?i)até\s*", "", date_str), "%Y"), None),
				# mm/yy
				(r"(?<=^)[0-9]{2}[./-]+[0-9]{2}(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", date_str), "%m%y"), None),
				# NI (Não Informado)
				(r"(?<=^)\s*NI\s*(?=$)", lambda date_str: None, None),
				# mm/YYYY a mm/YYYY TODO: capture and save first date
				(r"(?<=^)([0-9]{2}[./-]+[0-9]{4})\s*[a]+\s*([0-9]{2}[./\-]+[0-9]{4})(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", re.sub(r".*[a]+\s*", "", date_str)), "%m%Y"), None),
				# YYYY YYYY TODO: capture and save first date
				(r"(?<=^)[0-9]{4}\s+[0-9]{4}(?=$)", lambda date_str: date(re.sub(r".*\s+", "", date_str), "%Y"), None),
				# dd/mm/YYYY dd/mm/YYYY; ddmmYYY ddmmYYY TODO: capture and save first date
				(r"(?<=^)(([0-9]{1,2}[./-]+){2}|([0-9]{1,2}){2})[0-9]{4}\s+(([0-9]{1,2}[./-]+){2}|([0-9]{1,2}){2})[0-9]{4}(?=$)", lambda date_str: date(re.sub(r"[./\-]", "", re.sub(r".*\s+", "", date_str)), "%d%m%Y"), None),
				# abb/y abb/y TODO: capture and save first date
				(r"(?<=^)([A-Za-z]{3}[./-]+[0-9]{2})\s+([A-Za-z]{3}[./-]+[0-9]{2})(?=$)", lambda date_str: parse_date_abb(re.sub(r".*\s+", "", date_str)), None),
				# diversas
				(r"(?i)(?<=^)diversas(?=$)", lambda date_str: None, None),
				# month names
				(r".*", parse_date_abb, None)
			]

			for regex, parse_func, date_formats in regex_list:
				if re.match(regex, date_str):
					if date_formats:
						for format_str in date_formats:
							try:
								final_date = parse_func(date_str, format_str)
								break
							except ValueError as e:
								pass
					else:
						final_date = parse_func(date_str)
					
					break
		except ValueError as e:
			if date_str in ["??", "váriasdatas"] or str(e) in ["day is out of range for month"]:
				print(f"date error: {date_str} setting null")
				final_date = None
			else:
				print(f"date error: {date_str}")
				raise ValueError

	return final_date

def check_length(excel_path):
	df = pd.read_excel(excel_path)
	longest_row = {col: 0 for col in columns}

	for _, row in df.iterrows():
		for col in columns:
			if (length:=len(str(row[col]))) > longest_row[col]: longest_row[col] = length

	return longest_row

def create_tables():
	with db:
		db.create_tables([ArchiveBox])

def excel_to_db(excel_path):
	df = pd.read_excel(excel_path)
	print(df)

	df_columns = {}
	for column in columns:
		df_columns[column] = df[column].tolist()

	df_rows = []
	for i in range(0, len(df_columns["CX"])):
		row = {}
		for column in columns:
			row[column] = df_columns[column][i]

		df_rows.append(row)

	# return df_rows

	with db.atomic():
		for row in df_rows:
			print(f"row: {row}")
			params = {}
			
			# FIRST TEXT GROUP
			if pd.isna(row["CX"]): continue
			params["cx"] = str(row["CX"]).strip()

			if pd.isna(row["ITEM"]):
				params["item"] = ""
			else:
				params["item"] = str(row["ITEM"]).strip() if str(row["ITEM"]).strip() != "N/A" else ""

			params["descricao"] = str(row["DESCRIÇÃO"]).strip() if not pd.isna(row["DESCRIÇÃO"]) else ""

			# DATE GROUP
			# DATA INÍCIO
			if isinstance(row["DATA INÍCIO"], pd.Timestamp):
				params["data_inicio"] = row["DATA INÍCIO"].to_pydatetime().replace(tzinfo=timezone(timedelta(hours=-3))) if not pd.isna(row["DATA INÍCIO"]) else None
			elif isinstance(row["DATA INÍCIO"], datetime):
				params["data_inicio"] = row["DATA INÍCIO"].replace(tzinfo=timezone(timedelta(hours=-3))) if not pd.isna(row["DATA INÍCIO"]) else None
			else:
				params["data_inicio"] = parse_date(str(row["DATA INÍCIO"]).strip()) if not pd.isna(row["DATA INÍCIO"]) else None

			# DATA FIM
			if isinstance(row["DATA FIM"], pd.Timestamp):
				params["data_fim"] = row["DATA FIM"].to_pydatetime().replace(tzinfo=timezone(timedelta(hours=-3))) if not pd.isna(row["DATA FIM"]) else None
			elif isinstance(row["DATA FIM"], datetime):
				params["data_fim"] = row["DATA FIM"].replace(tzinfo=timezone(timedelta(hours=-3))) if not pd.isna(row["DATA FIM"]) else None
			else:
				params["data_fim"] = parse_date(str(row["DATA FIM"]).strip()) if not pd.isna(row["DATA FIM"]) else None

			# CONF.
			if isinstance(row["CONF."], pd.Timestamp):
				params["conf"] = row["CONF."].to_pydatetime().replace(tzinfo=timezone(timedelta(hours=-3))) if not pd.isna(row["CONF."]) else None
			elif isinstance(row["CONF."], datetime):
				params["conf"] = row["CONF."].replace(tzinfo=timezone(timedelta(hours=-3))) if not pd.isna(row["CONF."]) else None
			else:
				params["conf"] = parse_date(str(row["CONF."]).strip()) if not pd.isna(row["CONF."]) else None

			# INTEGER GROUP
			params["arq"] = int(row["ARQ."]) if not pd.isna(row["ARQ."]) else None
			params["est"] = int(row["EST."]) if not pd.isna(row["EST."]) else None
			params['prat'] = int(row['PRAT.']) if not pd.isna(row['PRAT.']) else None
			params['dest'] = int(row['DEST.']) if not pd.isna(row['DEST.']) or row['DEST.'] == "N/A" else -1

			# BOOLEAN GROUP
			params["dig"] = False if pd.isna(row["DIG."]) else True

			if pd.isna(row["MIC."]):
				params["mic"] = False
			else:
				params["mic"] = False if str(row["MIC."]).strip() in ["N", "X"] else True

			if pd.isna(row['Descarte']):
				params["descarte"] = False
			else:
				params["descarte"] = True

			# SECOND TEXT GROUP
			if pd.isna(row["RET."]):
				params["ret"] = ""
			else:
				params["ret"] = str(row["RET."]).strip() if str(row["RET."]).strip() != "N/A" else ""

			params["empresa"] = str(row["EMPRESA"]).strip() if not pd.isna(row["EMPRESA"]) else ""

			params["microfilme"] = str(row["MICROFILME"]).strip() if not pd.isna(row["MICROFILME"]) else ""

			params["observacao"] = str(row["OBSERVAÇÃO"]).strip() if not pd.isna(row["OBSERVAÇÃO"]) else ""

			print(f"params: {params}\n")
			ArchiveBox.create(**params)

if __name__ == '__main__':
	if not ArchiveBox.table_exists():
		ArchiveBox.create_table()
	
	r=excel_to_db('Catálogo_Caixas BOX.xls')
	
	print("Data imported successfully!")

# if __name__ == '__main__':
# 	create_tables()
# 	print("Tables created successfully!")
