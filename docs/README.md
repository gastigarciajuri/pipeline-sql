# Metadata Pipeline for Content Server (Universal Architecture)

Pipeline modular en Python diseñado para la extracción, transformación y exportación de metadatos desde un entorno de Gestión de Contenido Empresarial (ECM) hacia estructuras JSON optimizadas para arquitecturas de IA (RAG).

## 🛠 Arquitectura del Sistema
El pipeline utiliza componentes desacoplados para facilitar la migración entre entornos:
1. **`config.py`**: Gestión de variables de entorno (usar `.env` localmente).
2. **`database_manager.py`**: Capa de persistencia con `SQLAlchemy` y `pyodbc`.
3. **`metadata_service.py`**: Lógica de extracción, filtrado de versiones y serialización.
4. **`main.py`**: Orquestador del flujo de datos.

## 📊 Diccionario de Entidades (Esquema General)
Durante el desarrollo se identificaron las siguientes entidades críticas:

| Entidad | Propósito | Columnas Clave |
| :--- | :--- | :--- |
| Nodos | Árbol principal de objetos. | `DataID`, `Name`, `ModifyDate`, `SubType` |
| Versiones | Datos técnicos de archivos. | `DocID`, `Version`, `DataSize` |
| Seguridad | Matriz de permisos (ACL). | `DataID`, `RightID`, `AccessLevel` |

## 🚀 Instalación
1. Clonar el repositorio.
2. Configurar el archivo `.env` siguiendo la plantilla `example.env` (sin subir credenciales reales).
3. Asegurar la disponibilidad del driver `ODBC SQL Server Driver`.
4. Ejecutar: `python main.py`