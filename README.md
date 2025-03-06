# VERSIONES
## verión 3.1
tiene lo mismo que la 3.0 pero también permite exportar a Geopackage, filtrando.

## versión 3.0
Tiene la funcionalidad:

1. Feature 2 kml
2. Feature 2 GDB 

## versión 2.0
La versión 2.0 se crea porque siendo totalmente ya la ultima subversión 1.x, se quiere mejorar en varios aspectos, siendo el principal el de que la carpeta de salida se obtenga mediante diálogo de carpeta del S.O.

Funcionalidad de features 2 KML completa incluyendo el que se seleccione la carpeta de salida según el objetivo planteado.

## Mejoras potenciales
1. conseguir controlar los mensajes de forma más adecuada
2. Validar los parámetros
3. validar la post ejecución
4. controlar el idioma de los mensajes y interfaz ----> es probable que nos lleve a paquetizar.
5. Debe redactarse una diferencia entre esta rama y la rama *fet2kml-folder* desde el punto de vista del interés para el desarrollo de python.

------------------------------------------------------------------------------------------------

# USO DE LAS HERRAMIENTAS Y DETALLES DE INTERÉS PARA EL DESARROLLO

# 1. Extraer Features

## 1.1 Feature To KML

### Descripción

Extrae entidades de una capa para crear una nueva capa KML por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario.

### Parámetros
1. <u>Capa de entrada</u>: Capa de tipo <u>GPFeatureLayer</u> (Obligatorio).
2. <u>Campo de identificación de las entidades</u>: Campo de tipo <u>Field</u>, con filtro para tipos <u>Text, GUID, GlobalID, Date, TimeOnly, DateOnly, TimestampOffset</u>. Depende de la capa de entrada (Obligatorio).
3. <u>Encabezado del nombre de salida</u>: Texto con valor por defecto *ExtraccionesKML_* (Obligatorio).
4. <u>Carpeta de salida de los resultados</u>: Carpeta de tipo <u>DEFolder</u> (Obligatorio).

### acciones sobre los parámetros 
#### updateMessages

1. Comprueba si la carpeta de salida está vacía. Si no está vacía, lanza un mensaje de error.
2. Si la carpeta no es accesible, también lanza error.

### Comentarios sobre la ejecución

1. Comprueba si existe la capa temporal y la elimina si existe.

2. Crea una capa temporal para cada registro con la consulta SQL OBJECTID = valor.

3. Convierte la capa a KML con arcpy.conversion.LayerToKML().

4. Borra la capa temporal creada.

5. En *<u>GenerarNombreCapaSalida()</u>* crea el nombre del archivo KML añadiendo el OID si el nombre ya existe.

6. como alternativa al anterior, en *<u>GenerarNombreCapaSalida_Contador()</u>* crea el nombre del archivo KML añadiendo un contador correlativo si el nombre ya existe.


## 1.2 Feature To GDB

### Descripción

Extraer entidades de una capa para crear una nueva capa GDB por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario.

### Parámetros

1. <u>Capa de entrada</u>: Capa de tipo <u>GPFeatureLayer</u> (Obligatorio).

2. <u>Campo de identificación de las entidades</u>: Campo de tipo <u>Field</u>, con filtro para tipos <u>Text, GUID, GlobalID, Date, TimeOnly, DateOnly, TimestampOffset</u>. Depende de la capa de entrada (Obligatorio).

3. <u>GDB de salida de los resultados</u>: Carpeta de tipo <u>DEWorkspace</u> (Obligatorio).

4. <u>Nombre del Feature Dataset contenedor</u>: Texto con valor por defecto *feat2gdb*(Obligatorio).

### Acciones sobre los parámetros
#### updateMessages

1. Comprueba que la salida sea una geodatabase.

2. Comprueba que el nombre del Feature Dataset:

   a. No tenga espacios,

   b. No empiece por números y 

   c. sólo contenga letras, números o guiones bajos.

3. Comprueba que no exista un *Feature Dataset* con el mismo nombre en la GDB.

#### updateParameters

 1. **<u>Desactiva el parámetro</u>** del nombre del Feature Dataset si la salida es un GeoPackage.

### Comentarios sobre la ejecución

1. Obtiene el sistema de referencia de la capa o del mapa.

2. Crea el Feature Dataset <u>si no es GeoPackage</u>.

3. Usa un cursor para recorrer los registros de la capa de entrada.

4. Extrae cada registro a una Feature Class con la consulta SQL OBJECTID = valor.

5. Genera el nombre de la Feature Class eliminando caracteres no válidos.

6. Añade el OID si el nombre ya existe.