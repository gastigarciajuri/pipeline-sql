# metadata_service.py
import json
import logging
import os
from datetime import datetime
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class MetadataService:
    def __init__(self, db_manager: DatabaseManager, checkpoint_file='last_run.json'):
        self.db = db_manager
        self.checkpoint_file = checkpoint_file
        # Lista blanca de tipos de archivo permitidos para la IA
        self.allowed_mimetypes = [
            'application/pdf', 
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]

    def get_last_checkpoint(self):
        """Lee la fecha del checkpoint para saber desde dónde empezar."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f).get('last_run')
            except Exception as e:
                logger.warning(f"No se pudo leer el checkpoint: {e}")
        return None

    def update_checkpoint(self, timestamp):
        """Guarda la nueva marca temporal en el archivo JSON."""
        with open(self.checkpoint_file, 'w') as f:
            # Formato compatible con SQL Server: YYYY-MM-DD HH:MM:SS.mmm
            json.dump({'last_run': timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}, f)

    def get_incremental_documents(self):
        """Extrae documentos nuevos o modificados y procesa seguridad híbrida."""
        last_run = self.get_last_checkpoint()
        start_date = last_run if last_run else "1900-01-01 00:00:00"
        
        query = """
            SELECT 
                d.DataID, 
                v.Version AS VersionNumber,
                d.Name, 
                v.DataSize AS FileSize,
                d.ModifyDate,
                p.providerData + '.dat' AS EFSRelativePath,
                v.MimeType,
                acl.RightID,
                acl.See AS AccessLevel,
                CASE 
                    WHEN k.Type = 0 THEN 'User'
                    WHEN k.Type = 1 THEN 'Group'
                    WHEN acl.RightID = -1 THEN 'Public'
                    WHEN acl.RightID = -2 THEN 'Admin'
                    ELSE 'Special/System'
                END AS SubjectType
            FROM DTreeCore d
            INNER JOIN DVersData v ON d.DataID = v.DocID AND d.VersionNum = v.Version
            INNER JOIN ProviderData p ON v.ProviderId = p.providerID
            LEFT JOIN DTreeACL acl ON d.DataID = acl.DataID AND acl.See >= 1
            LEFT JOIN KUAF k ON acl.RightID = k.ID
            WHERE d.SubType = 144 
            AND d.ModifyDate > :start_date
            ORDER BY d.ModifyDate ASC
        """
        
        raw_rows = self.db.execute_query(query, {"start_date": start_date})
        
        documents = {}
        max_modify_date = None

        for row in raw_rows:
            if row['MimeType'] not in self.allowed_mimetypes:
                continue

            data_id = row['DataID']

            if not max_modify_date or row['ModifyDate'] > max_modify_date:
                max_modify_date = row['ModifyDate']

            # Inicialización del documento en el diccionario
            if data_id not in documents:
                documents[data_id] = {
                    "DataID": data_id,
                    "Version": row['VersionNumber'], # <-- INCLUIDO AQUÍ
                    "Name": row['Name'],
                    "MimeType": row['MimeType'],
                    "FileSize": row['FileSize'],
                    "ModifyDate": row['ModifyDate'],
                    "EFSRelativePath": row['EFSRelativePath'],
                    "SecurityTokens": []
                }
            
            # Formato Híbrido de Seguridad: "T:ID:N"
            if row['RightID'] is not None:
                type_initial = row['SubjectType'][0] # U, G, P, A o S
                token = f"{type_initial}:{row['RightID']}:{row['AccessLevel']}"
                
                # Evitar duplicados en la lista de tokens
                if token not in documents[data_id]["SecurityTokens"]:
                    documents[data_id]["SecurityTokens"].append(token)
        
        return list(documents.values()), max_modify_date

    def save_to_json(self, data, filename):
        """Guarda la lista de documentos en un archivo JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, default=str)
            logger.info(f"✅ Exportación exitosa: {len(data)} documentos en {filename}")
        except Exception as e:
            logger.error(f"Error al guardar el archivo JSON: {e}")