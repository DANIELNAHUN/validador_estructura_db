# Validador de Estructura de Base de Datos

Este proyecto es una herramienta desarrollada en Python para analizar, extraer y comparar la estructura de dos bases de datos MySQL. Genera un reporte detallado en Excel que permite identificar discrepancias entre los esquemas de las bases de datos.

## Características

*   **Conexión a Múltiples Bases de Datos**: Se conecta a dos instancias de MySQL definidas en las variables de entorno.
*   **Extracción de Metadatos**: Obtiene información detallada de todas las tablas, incluyendo:
    *   Nombre de la tabla
    *   Nombre de la columna
    *   Tipo de dato
    *   Si permite valores nulos (Nullable)
    *   Valor por defecto
*   **Comparación Automática**: Compara la Base de Datos 1 (Master) con la Base de Datos 2 y detecta:
    *   Tablas faltantes o adicionales.
    *   Columnas faltantes o adicionales.
    *   Diferencias en tipos de datos.
    *   Diferencias en propiedades de nulabilidad.
*   **Reporte en Excel**: Genera un archivo `estructura_base_datos.xlsx` con cuatro hojas:
    1.  **DB1**: Estructura completa de la Base de Datos 1.
    2.  **DB2**: Estructura completa de la Base de Datos 2.
    3.  **Combinado**: Vista unificada de ambas estructuras.
    4.  **Diferencias**: Reporte de discrepancias encontradas.

## Requisitos Previos

*   Python 3.8 o superior.
*   Acceso a las bases de datos MySQL que se desean analizar.

## Instalación

1.  Clona este repositorio o descarga los archivos.
2.  Instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

Las dependencias principales son:
*   `sqlalchemy`: Para la conexión y abstracción de la base de datos.
*   `pymysql`: Driver de MySQL para Python.
*   `python-dotenv`: Para manejar variables de entorno.
*   `pandas`: Para manipulación de datos y generación de Excel.
*   `openpyxl`: Motor para escribir archivos Excel.

## Configuración

Crea un archivo `.env` en la raíz del proyecto (si no existe) y configura las URLs de conexión a tus bases de datos. Puedes usar el archivo de ejemplo como guía.

El formato de las variables debe ser:

```env
DATABASE_URL1="mysql+pymysql://usuario:password@host:puerto/nombre_db1"
DATABASE_URL2="mysql+pymysql://usuario:password@host:puerto/nombre_db2"
```

*   `DATABASE_URL1`: Base de datos principal o "Master" (la fuente de la verdad).
*   `DATABASE_URL2`: Base de datos secundaria a comparar.

## Uso

Ejecuta el script principal con Python:

```bash
python db_validator.py
```

Al finalizar, el script generará un archivo llamado `estructura_base_datos.xlsx` en el mismo directorio.

## Interpretación del Reporte de Diferencias

La hoja "Diferencias" del Excel muestra las discrepancias encontradas. Las columnas clave son:

*   **Difference Type**:
    *   `Missing Table in DB2`: La tabla existe en DB1 pero no en DB2.
    *   `Extra Table in DB2`: La tabla existe en DB2 pero no en DB1.
    *   `Missing Column in DB2`: La columna existe en la tabla de DB1 pero no en la de DB2.
    *   `Extra Column in DB2`: La columna existe en la tabla de DB2 pero no en la de DB1.
    *   `Type Mismatch`: El tipo de dato es diferente (ej. `INTEGER` vs `VARCHAR`).
    *   `Nullable Mismatch`: La propiedad de permitir nulos es diferente.
*   **DB1 Value**: Valor encontrado en la Base de Datos 1.
*   **DB2 Value**: Valor encontrado en la Base de Datos 2.
