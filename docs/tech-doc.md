# Resumen para una futura implementacion

## Dejaremos establecidos los nombres de tablas correctos.

# 📋 Diccionario de Tablas y Nombres Reales 
###### A continuación, se detallan los nombres estándar según la documentación y los nombres reales que descubrimos en tu servidor:

| Proposito tecnico          | Nombre Estándar  | Nombre Real en LAB    |
| -----------------          |:---------------: | ---------------:      |
| Nucleo de objetos          | DTree            | DTreeCore             |
| Datos de Versiones         | DVersData        | DVersData             |
| Control de Acceso (ACL)    | DTreeACL         | DTreeACL              |
| Relacion de Usuarios/Grupo | KUAFCHILDREN     | KUAFChildren          |
| Informacion de Usuarios    | KUAF             | KUAF                  |
| Almacenamiento Físico      | ProviderData     | ProviderData          |




# 🔗 Mapa de Relaciones para el Pipeline

## 📌 Objetivo
Para reconstruir la información completa del documento hacia la **base de datos vectorial**, se detallan a continuación las **uniones (JOINs) exactas validadas** y las reglas asociadas para una futura implementación.

---

## 🔄 Relaciones Validadas (JOINs)

### 📄 De Documento a Versión Activa

```sql
DTreeCore.DataID = DVersData.DocID
DTreeCore.VersionNum = DVersData.Version
````

**Nota:**
Esta relación asegura que solo se extraiga el **archivo más reciente** del documento.

---

### 💾 De Versión a Almacenamiento Físico (EFS)

```sql
DVersData.ProviderId = ProviderData.providerID
```

**Importante (LAB):**
Se detectó sensibilidad a mayúsculas y minúsculas:

* `ProviderId` → con **d minúscula** en `DVersData`
* `providerID` → con **ID mayúscula** en `ProviderData`

---

### 🔐 De Documento a Seguridad (Tokens)

```sql
DTreeCore.DataID = DTree
```




## 📝 Nota de Seguridad RAG

## Estructura de `SecurityInfo`

Cada documento en el JSON contiene una lista de objetos de seguridad con tres componentes clave.

---

## 1. ID (Identificador de Sujeto)

Representa la entidad a la cual se le ha otorgado el permiso.

- **Valores Positivos (> 0):**  
  Corresponden al `ID` único de un **Usuario** (identidad individual) o un **Grupo** (departamento, equipo) en el sistema.

- **Valores Negativos:**  
  Roles estructurales del sistema:
  - **-1 / -3:** **Public Access**  
    Indica que cualquier usuario autenticado en el banco puede acceder al archivo.
  - **-2 / -4:** **Administradores**  
    Usuarios con privilegios globales de sistema.

---

## 2. Type (Tipo de Sujeto)

Define la naturaleza del ID para determinar qué tabla de validación debe consultarse.

- **User:**  
  El permiso fue asignado directamente a una persona (por ejemplo, el dueño del archivo).

- **Group:**  
  El acceso se hereda por pertenencia a un grupo funcional.

- **Public / Admin:**  
  Roles especiales que no requieren validación de membresía grupal específica para el acceso general.

---

## 3. AccessLevel (Nivel de Acceso)

Valor entero extraído de la columna `See` de la base de datos que determina las capacidades del sujeto sobre el archivo.

| Valor | Nivel | Descripción para el RAG |
| --- | --- | --- |
| **1** | **See** | **Mínimo:** El usuario sabe que el archivo existe, pero la IA **no** debe leer su contenido. |
| **2** | **See Contents** | **Ideal:** Permite que la IA extraiga texto del archivo para generar respuestas. |
| **3** | **Modify** | **Intermedio:** Incluye lectura y capacidad de edición de metadatos. |
| **4** | **Delete** | **Máximo:** Control total sobre el ciclo de vida del documento. |

---

## Lógica de Validación para la IA

Para validar si un usuario puede realizar una consulta sobre un documento, el motor de búsqueda debe:

1. Obtener el `UserID` del consultante y sus `GroupIDs` desde la tabla `KUAFChildren`.
2. Verificar si alguno de esos IDs (o el token `-1`) existe en la lista `SecurityInfo`.
3. Confirmar que el `AccessLevel` asociado a ese ID sea **2 o superior**.
```

