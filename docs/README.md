# Metadata Pipeline for Content Server (Experimental LAB)

Este proyecto es un pipeline modular desarrollado en Python para la extracción, transformación y exportación de metadatos desde un entorno experimental de Content Server hacia un formato JSON consumible por procesos de IA/RAG.

## 🛠 Arquitectura del Sistema

El pipeline se divide en componentes desacoplados para garantizar mantenibilidad y escalabilidad:

1.  **`config.py`**: Gestión de entorno y carga de variables mediante `python-dotenv`.
2.  **`database_manager.py`**: Orquestador de la capa de datos. Utiliza `SQLAlchemy` para la gestión del ciclo de vida de la conexión y `pyodbc` como driver de bajo nivel.
3.  **`metadata_service.py`**: Capa de lógica de negocio. Contiene la inteligencia de las consultas SQL y la lógica de serialización a JSON.
4.  **`main.py`**: Punto de entrada (Entry Point) que orquesta el flujo completo.

## 📊 Diccionario de Datos (LAB Schema)

Durante la fase de experimentación, se identificaron las siguientes entidades críticas en la base de datos:

| Tabla | Función | Columnas Clave |
| :--- | :--- | :--- |
| `DTreeCore` | Almacén de nodos del sistema. | `DataID` (PK), `Name`, `ModifyDate`, `SubType` |
| `DVersData` | Detalle técnico de archivos. | `DocID` (FK), `DataSize` |
| `DTreeACL` | Matriz de permisos (ACL). | `DataID` (FK), `RightID`, `See` |

## 🚀 Instalación y Uso

1. Configurar el archivo `.env` con las credenciales del entorno.
2. Asegurar la disponibilidad del driver `ODBC SQL Server Driver`.
3. Ejecutar el pipeline:
   ```bash
   python main.py


| Entidad    | Tabla en el Servidor (LAB) | Relación Clave                                      |
|-----------|----------------------------|----------------------------------------------------|
| Objetos   | DTreeCore                  | Base de todo el árbol de documentos.               |
| Versiones | DVersData                  | DocID + Version para la versión activa.            |
| ACL       | DTreeACL                   | DataID para obtener los SecurityTokens.            |
| EFS       | ProviderData               | providerID para la ruta física del archivo.        |
| Usuarios  | KUAFChildren               | ChildID para validar membresías a grupos.          |