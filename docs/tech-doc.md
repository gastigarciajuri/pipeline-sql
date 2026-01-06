# Resumen para Implementación en Producción

Este documento establece los mapeos de tablas y relaciones validadas durante la fase de ingeniería inversa en el entorno de pruebas.

## 📋 Diccionario de Tablas Reales
Debido a la sensibilidad de capitalización (*case-sensitivity*) en el servidor, se deben usar estos nombres literales:

| Propósito Técnico | Nombre Estándar | Nombre en Servidor Actual |
| :--- | :--- | :--- |
| Núcleo de objetos | `DTree` | `DTreeCore` |
| Datos de Versiones | `DVersData` | `DVersData` |
| Control de Acceso | `DTreeACL` | `DTreeACL` |
| Relación Usuario/Grupo | `KUAFCHILDREN` | `KUAFChildren` |
| Almacenamiento Físico | `ProviderData` | `ProviderData` |

## 🔗 Mapa de Relaciones (JOINs)

### 📄 Documento -> Versión Activa
Garantiza la extracción exclusiva del archivo más reciente:
`DTreeCore.DataID = DVersData.DocID AND DTreeCore.VersionNum = DVersData.Version`

### 💾 Versión -> Almacenamiento Físico (EFS)
*Importante:* Se detectó capitalización asimétrica en las claves:
`DVersData.ProviderId = ProviderData.providerID` (Nótese 'd' minúscula vs 'ID' mayúscula).

### 🔐 Documento -> Seguridad (Tokens)
`DTreeCore.DataID = DTreeACL.DataID`

---

## 📝 Nota de Seguridad para el Motor de IA

### Estructura de `SecurityTokens`
Cada documento exportado contiene una lista de IDs autorizados.

1. **Identificadores (RightID):**
   - **Valores > 0:** IDs de Usuarios o Grupos específicos (ej: `GRP_101`, `USR_500`).
   - [cite_start]**Valores Negativos:** Roles globales (ej: `-1` para Acceso Público, `-2` para Administradores). [cite: 81, 142]

2. [cite_start]**Niveles de Acceso (Basado en columna `See`):** [cite: 81, 143]

| Valor | Nivel | Acción Permitida para la IA |
| :--- | :--- | :--- |
| 1 | See | [cite_start]**Solo existencia.** No indexar contenido. [cite: 81, 143] |
| 2 | See Contents | [cite_start]**Lectura autorizada.** Nivel ideal para RAG. [cite: 81, 143] |
| 3 | Modify | [cite_start]**Edición.** Nivel seguro para lectura. [cite: 81, 143] |
| 4 | Delete | [cite_start]**Control Total.** [cite: 81, 144] |

### 🔑 Lógica de Validación (Capa de Aplicación)
Se recomienda que la IA obtenga las "llaves" del usuario (membresías de grupo) una sola vez por sesión desde la tabla `KUAFChildren`.
- [cite_start]**Match de Seguridad:** El acceso se concede si el `UserID` o sus `GroupIDs` están presentes en los tokens del documento con un nivel de acceso **>= 2**. [cite: 81]