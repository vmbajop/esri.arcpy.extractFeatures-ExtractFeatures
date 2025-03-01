# Versiones de desarrollo

## versión 1.3 (trabajando en ella)
1. conseguir controlar los mensajes de forma más adecuada
2. Validar los parámetros
3. validar la post ejecución
4. controlar el idioma de los mensajes y interfaz ----> es probable que nos lleve a paquetizar.
5. Debe redactarse una diferencia entre esta rama y la rama *fet2kml-folder* desde el punto de vista del interés para el desarrollo de python.

## versión 1.2

1. Se controla el progreso de la tarea gráficamente en vez de numéricamente

## versión 1.1.1

1. Mejora interna en el manejo de la carpeta de salida como variable.
Ahora es unparámetro derivado del parámetros _"nombre de carpeta de salida"_ que introduce el usuario. Se gestiona internamente en el método

```python
updateParameters(self, parameters)
```

y ya no se controla mediante una propiedad de alcance de clase como 

```python
self.carpeta_resultados
```

## versión 1.1
funcionalidad añadida:
1. Permite al usuario introducir el nombre de la carpeta de salida

## versión 1

Funcionalidad general conseguida.
1. Extrae las features a capas en kml
2. Crea la carpeta de salidad con **nombre fijo** preconfigurado internamente
3. Comprueba si la carpeta con el **nombre fijo** ya existe. 
4. Si existe, comprueba si tiene contenido
5. Si existe y si tiene contenido, *renombra la existente* y a la nueva la pone el *nombre fijo*
6. Si existe y no tiene contenido, la reutiliza
