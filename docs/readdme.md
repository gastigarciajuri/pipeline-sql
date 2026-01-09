```markdown
# Informe de Ingeniería Inversa y Diseño de Pipeline: Content Server

## 1. Contexto y Objetivos

El objetivo de este proyecto fue realizar una ingeniería inversa sobre un entorno de **OpenText Content Server (Livelink)** para extraer metadatos de documentos y sus permisos de seguridad. Esta información se procesa y exporta en un formato **JSON optimizado** para ser consumido por un motor de búsqueda semántica (**RAG**) con validación de seguridad por tokens.


## 2. Hallazgos del Esquema de Base de Datos

A través de la inspección directa del servidor, se identificaron las tablas y columnas críticas. Se detectó que el servidor es **sensible a mayúsculas y minúsculas (case-sensitive)**, por lo que se deben usar los nombres exactos listados a continuación.

### 📋 Mapeo de Tablas

| Entidad             | Tabla Estándar | Nombre Real (LAB) | Propósito Técnico                                                                 |
|---------------------|----------------|-------------------|-----------------------------------------------------------------------------------|
| Nodos / Objetos     | DTree          | DTreeCore         | Tabla principal que contiene el árbol de objetos del sistema.                      |
| Versiones           | DVersData      | DVersData         | Detalles técnicos (tamaño, tipo de archivo) de cada versión del documento.         |
| Seguridad (ACL)     | DTreeACL       | DTreeACL          | Matriz de control de acceso (quién tiene qué permiso).                             |
| Usuarios / Grupos   | KUAF           | KUAF              | Directorio de usuarios y grupos.                                                   |
| Membresías          | KUAFCHILDREN   | KUAFChildren      | Tabla de relación que indica a qué grupos pertenece cada usuario.                  |
| Almacenamiento      | ProviderData   | ProviderData      | Información sobre la ubicación física del archivo en el servidor de archivos (EFS). |

---

## 3. Lógica de Relaciones y Pipeline

El pipeline reconstruye la identidad de un documento mediante los siguientes cruces de datos (**JOINs**):

- **Extracción de Versión Activa**  
  Se vincula `DTreeCore` con `DVersData` usando `DataID = DocID` y `VersionNum = Version`. Esto garantiza obtener únicamente el archivo vigente y evitar documentos obsoletos.

- **Ruta Física del Archivo**  
  Se vincula `DVersData` con `ProviderData` mediante una relación de capitalización asimétrica:  
  `DVersData.ProviderId = ProviderData.providerID`.  
  El archivo físico en disco se localiza añadiendo el sufijo `.dat` al nombre encontrado en `providerData`.

- **Extracción de Permisos**  
  Se recolectan todos los registros de `DTreeACL` asociados al `DataID` donde el nivel de permiso (**See**) sea igual o superior a **1**.

---

## 4. El Modelo de Seguridad por Tokens

Uno de los puntos más valiosos de la ingeniería inversa fue el descifrado del sistema de permisos para su uso en **IA**.

### Estructura de Tokens Híbridos

Cada documento se exporta con una lista de **SecurityTokens** bajo el formato:

- **T (Tipo)**:  
  - `U` (Usuario)  
  - `G` (Grupo)  
  - `P` (Público)  
  - `A` (Admin)

- **ID**:  
  Identificador numérico del sujeto (positivos para usuarios/grupos reales, negativos para roles de sistema como **-1** para acceso público).

- **N (Nivel)**:  
  Valor de la columna **See** (1 a 4).

### Matriz de Permisos (AccessLevel)

| Valor | Nivel         | Acción Permitida para la IA                          |
|------:|---------------|------------------------------------------------------|
| 1     | See           | Solo existencia. No se debe indexar el contenido.    |
| 2     | See Contents  | Nivel Ideal para RAG. Lectura autorizada del contenido. |
| 3     | Modify        | Lectura y edición autorizada.                        |
| 4     | Delete        | Control total sobre el objeto.                       |

---

## 5. Implementación Técnica (Pipeline)

El código desarrollado implementa estas reglas mediante una arquitectura modular:

- **database_manager.py**  
  Maneja la conexión robusta vía **SQLAlchemy** y **pyodbc**.

- **metadata_service.py**  
  Ejecuta la consulta compleja que agrupa los metadatos y serializa la información de seguridad en el formato híbrido optimizado.

- **Carga Incremental**  
  El sistema utiliza un archivo de checkpoint (`last_run.json`) para procesar únicamente los documentos modificados desde la última ejecución exitosa, optimizando el rendimiento y los recursos del servidor.
```
