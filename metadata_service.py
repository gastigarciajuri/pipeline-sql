# metadata_service.py
import json
import logging
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class MetadataService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_recent_documents(self, days):
        query = """
            SELECT 
                d.DataID, 
                d.Name, 
                v.DataSize AS FileSize,
                d.ModifyDate,
                p.providerData + '.dat' AS EFSRelativePath,
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
            AND d.ModifyDate >= DATEADD(day, :days, GETDATE())
            ORDER BY d.DataID
        """
        
        raw_rows = self.db.execute_query(query, {"days": -days})
        
        # Diccionario para agrupar los permisos por cada documento único
        documents = {}

        for row in raw_rows:
            data_id = row['DataID']
            
            # Si el documento no está en el diccionario, lo creamos
            if data_id not in documents:
                documents[data_id] = {
                    "DataID": data_id,
                    "Name": row['Name'],
                    "FileSize": row['FileSize'],
                    "ModifyDate": row['ModifyDate'],
                    "EFSRelativePath": row['EFSRelativePath'],
                    "SecurityInfo": []
                }
            
            # Agregamos la información de seguridad solo si existe un RightID
            if row['RightID'] is not None:
                documents[data_id]["SecurityInfo"].append({
                    "ID": row['RightID'],
                    "Type": row['SubjectType'],
                    "AccessLevel": row['AccessLevel']
                })
        
        # Retornamos solo la lista de valores (documentos procesados)
        return list(documents.values())

    def save_to_json(self, data, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # default=str maneja las fechas ModifyDate para el JSON
                json.dump(data, f, indent=4, default=str)
            logger.info(f"✅ Pipeline exitoso: {len(data)} documentos únicos exportados a {filename}")
        except Exception as e:
            logger.error(f"Error al guardar el archivo JSON: {e}")