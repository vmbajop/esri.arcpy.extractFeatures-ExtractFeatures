# Versiones de desarrollo 

## versión 1.1.1 (trabajando en ella)

Objetivos:

1. conseguir que

```python

self.carpeta_resultado = os.path.join(os.path.dirname(self.ruta_proyecto), parameters[3].valueAsText)

```

se pueda controlar desde

```python

updateParameters(self, parameters)

```

La idea es ver si se puede construir como parámetro oculto dependiente del param3

2. conseguir controlar el progreso de la tarea gráficamente en vez de numéricamente
3. conseguir controlar los mensajes a través del métoco específico

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
