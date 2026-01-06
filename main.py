# main.py
import logging
from config import DB_CONFIG, PIPELINE_SETTINGS
from database_manager import DatabaseManager
from metadata_service import MetadataService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_pipeline():
    # 1. Inicializar componentes
    db = DatabaseManager(DB_CONFIG)
    service = MetadataService(db)
    
    # 2. Extraer datos
    data = service.get_recent_documents(PIPELINE_SETTINGS['days_back'])
    
    # 3. Guardar resultados
    if data:
        service.save_to_json(data, PIPELINE_SETTINGS['output_file'])
        print(f"✅ Pipeline finalizado. {len(data)} archivos listos para procesar.")
    else:
        print("⚠️ No se encontraron archivos nuevos.")

if __name__ == "__main__":
    run_pipeline()  