# config.py
import os
from dotenv import load_dotenv

# Esto debe estar arriba de todo
load_dotenv()

DB_CONFIG = {
    'server': os.getenv('SERVER'),
    'database': os.getenv('DATABASE'),
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'driver': os.getenv('DB_DRIVER')
}

PIPELINE_SETTINGS = {
    'output_file': 'metadata_export.json',
    'days_back': 30  # Ajusta según necesites
}