# Versiones de desarrollo
Versión de desarrollo diseñada para que la carpeta de salidad de los datos en kml, capas provenientes de registros de otra capa, se seleccione del sistema operativo
mediante un menú de carpetas propio del SO.

# versión folder 2.0 (trabajando en ella)

Es funcional pero necesitamos lo siguiente:
1. esto no está funcionando: 
```python
    nombre_sin_extension, extension = os.path.splitext(nombre_kml)
```
2. Necesitamos una sobrecarga de **GenerarNombreCapaSalida_Contador()** en el que el nombre se genere mediante la combinación de los campos OID y el elegido, en vez de por conteo si está repetido

3. Hay que comprobar si el métod **ComprobarExistenciaCapaTemporalTOC** es realmente necesario