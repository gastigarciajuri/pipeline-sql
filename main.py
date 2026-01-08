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
    
    # 2. Obtener documentos incrementales
    data, new_timestamp = service.get_incremental_documents()
    
    # 3. Guardar resultados
    if data:
        # Intentamos guardar el archivo
        service.save_to_json(data, PIPELINE_SETTINGS['output_file'])
        
        # SOLO SI EL GUARDADO FUE EXITOSO, actualizamos el checkpoint
        if new_timestamp:
            service.update_checkpoint(new_timestamp)
            
        print(f"✅ Pipeline finalizado. {len(data)} archivos listos para procesar.")
    else:
        print("⚠️ No se encontraron archivos nuevos.")

if __name__ == "__main__":
    run_pipeline()  