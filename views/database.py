from peewee import PostgresqlDatabase
import os

# Load environment variables
DB_HOST = 'californio'
DB_PORT = 5432
DB_NAME = 'caixas_box'
DB_USER = os.getenv('caixas_box_db_user')
DB_PASSWORD = os.getenv('caixas_box_db_password')

db = PostgresqlDatabase(
	DB_NAME,
	user=DB_USER,
	password=DB_PASSWORD,
	host=DB_HOST,
	port=DB_PORT
)

IS_READ_ONLY = not (DB_USER == "caixas_box_user" or DB_USER == "devel")
