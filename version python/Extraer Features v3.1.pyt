'''FUENTES
Plantilla: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-template-for-python-toolboxes.htm'''

import arcpy
import os
import datetime
import re

class Toolbox(object):
    def __init__(self):
        self.label = "Extraer Features"
        self.alias = "ExtraerFeatures"

        # Lista de tools en la toolbox
        self.tools = [FeatureToKML, FeatureToGDB]

# region KML
class FeatureToKML(object):
    def __init__(self):
        # self.name = "FeatureToKML"
        self.version = "2.0.1"
        self.label = "Feature To KML v" + self.version
        self.alias = "Feature2KML"        
        
        #DUDA DE SI SIRVEN
        self.description = "Extraer entidades de una capa para crear una nueva capa KML por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario."
        self.canRunInBackground = False
        

        #-------------------------------------
        # propiedades parametrizables
        #-------------------------------------
        self.nombre_capa_temporal = "capa_temporal"
        # self.salto_mensaje_porcentajes = 5

        #-------------------------------------
        # constantes
        #-------------------------------------
        proyecto = arcpy.mp.ArcGISProject("CURRENT")
        self.mapa = proyecto.listMaps()[0]
        self.ruta_proyecto = proyecto.homeFolder
         #-------------------------------------    

    def getParameterInfo(self):
        """Define the tool parameters."""
        param0 = arcpy.Parameter(
            name="InputFeatureLayer",
            displayName="Capa de entrada",
            direction="Input",
            parameterType="Required",
            datatype="GPFeatureLayer"
        )

        param1 = arcpy.Parameter(
            name="CampoIdentificativo",
            displayName="Campo de identificación de las entidades",
            direction="Input",
            parameterType="Required",
            datatype="Field"
        )
        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["Text", "GUID", "GlobalID", "Date", "TimeOnly", "DateOnly", "TimestampOffset"]

        param2 = arcpy.Parameter(
            name="EncabezadoNombre",
            displayName="Encabezado del nombre de salida",
            direction="Input",
            parameterType="Required",
            datatype="GPString"
        )
        param2.value = "ExtraccionesKML_"

        param3 = arcpy.Parameter(
            name="CarpetaResultados",
            displayName="Carpeta de salidad de los resultados",
            direction="Input",
            parameterType="Required",
            datatype="DEFolder"
        )
        
        params =[param0, param1, param2, param3]
        return params

    def isLicensed(self): # Es opcional
        # La herramienta usada (arcpy.conversion.LayerToKML()) está disponible en Basic, por tanto siempre está licenciado
        return True
    
    def updateMessages(self, parameters):
        # Solo si el usuario ha cambiado el parámetro y ha seleccionado una carpeta        
        if parameters[3].altered and parameters[3].valueAsText:
            parameters[3].clearMessage()
            try:
                if os.listdir(parameters[3].valueAsText):
                    parameters[3].setErrorMessage("La carpeta contiene archivos y sin embargo debería estar vacía.")
                else:
                    parameters[3].clearMessage()
            except Exception as e:
                parameters[3].setErrorMessage(f"Error al acceder a la carpeta: {e}")
                return

        return

    def updateParameters(self, parameters):
        
        return

    def execute(self, parameters, messages):
        arcpy.AddMessage(f"\n{self.label}:\n\n{self.description}")
        arcpy.AddMessage(f"\nLa carpeta de salidad es \n{parameters[3].value}")
        try:           
            self.numero_registros = arcpy.management.GetCount(parameters[0].value)
            arcpy.SetProgressor("step", f"Comienza el procesado de {self.numero_registros} registros", 0, int(self.numero_registros.getOutput(0)), 1)

            self.ComprobarExistenciaCapaTemporalTOC()

            self.ExtraerFeature2KML(parameters)
        except Exception as e:
            arcpy.AddError(f"ERROR En EXECUTE >>> '{e}")
            return
    
    def ComprobarExistenciaCapaTemporalTOC(self):
        for capa in self.mapa.listLayers():
            if capa.name == self.nombre_capa_temporal:
                self.mapa.removeLayer(capa)
                arcpy.AddMessage(f"\nEliminada una capa con nombre '{self.nombre_capa_temporal}'")
        arcpy.AddMessage("\nComprobada la existencia de una capa temporal previa.")

    def ExtraerFeature2KML(self, parameters):
        try:
            # Parámetros
            capa_entrada = parameters[0].value
            campo_nombre = parameters[1].valueAsText
            # prenombre_capa_salida = parameters[2].valueAsText

            # cursor con los registros de la capa de entrada, de la que se cogen dos campos: OID/ID y el campo seleccionado para dar nombre a las capas
            with arcpy.da.SearchCursor(capa_entrada, ['OID@', campo_nombre]) as cursor:
                arcpy.AddMessage("\nIniciado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
                i = 1
                for row in cursor:
                    # cogemos el registro actual mediante una sentencia SQL que dice: ObjectID = al valor del campo [0] del registro actual.
                    # El campo [0] es OID, el elegido en la intefaz es el [1]
                    sql = f"OBJECTID = {row[0]}"
                    #nombre_kml = self.GenerarNombreCapaSalida_Contador(parameters, row)
                    nombre_kml = self.GenerarNombreCapaSalida(parameters, row)
                    
                    # Separar la extension kml del nombre del archivo
                    nombre_sin_extension, extension = os.path.splitext(nombre_kml)

                    nombre_sin_extension = nombre_sin_extension + "_FL"

                    arcpy.management.MakeFeatureLayer(capa_entrada, nombre_sin_extension, sql)

                    arcpy.conversion.LayerToKML(nombre_sin_extension, parameters[3].valueAsText + "\\" + nombre_kml)
                    arcpy.AddMessage(f"Creada la capa {nombre_kml}")
                    arcpy.management.Delete(nombre_sin_extension)
                    arcpy.SetProgressorLabel(f"Procesados {i} de {self.numero_registros} registros")
                    arcpy.SetProgressorPosition(i)
                    i = i + 1
                    
                arcpy.AddMessage("\nFinalizado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
        except Exception as e:
            arcpy.AddError(f"\nERROR EN LA EXTRACCIÓN >>> '{e}")
            return

    '''Crea el nombre de salida iterando si ya existe un nombre igual o no. Si existe, le añade un número correlativo'''
    def GenerarNombreCapaSalida_Contador(self, parameters, row):
        nombre_kml = parameters[2].valueAsText + f"{row[1]}" + ".kml"
        # Comprobar si existe el nombre y renombrar
        count = 1
        while arcpy.Exists(os.path.join(parameters[3].valueAsText, nombre_kml)):
            nombre_kml = parameters[2].valueAsText + f"{row[1]}" + str(count) + ".kml"
            count += 1
        return nombre_kml
    
    '''Crea el nombre de salida añadiendo el OID'''
    def GenerarNombreCapaSalida(self, parameters, row):
        nombre_kml = parameters[2].valueAsText + f"{row[1]}" + ".kml"
        while arcpy.Exists(os.path.join(parameters[3].valueAsText, nombre_kml)):
            nombre_kml = parameters[2].valueAsText + f"{row[1]}" + f"{row[0]}" + ".kml"
        # Comprobar si existe el nombre y renombrar
        return nombre_kml

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
# endregion


# region "GDB"
class FeatureToGDB(object):
    def __init__(self):
        # self.name = "FeatureToKML"
        self.version = "2.0"
        self.label = "Feature To GDB v" + self.version
        self.alias = "Feature2GDB"        
        
        #DUDA DE SI SIRVEN
        self.description = "Extraer entidades de una capa para crear una nueva capa GDB por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario."
        self.canRunInBackground = False

        #-------------------------------------
        # constantes
        #-------------------------------------
        proyecto = arcpy.mp.ArcGISProject("CURRENT")
        self.mapa = proyecto.listMaps()[0]
        self.ruta_proyecto = proyecto.homeFolder
         #-------------------------------------    

    def getParameterInfo(self):
        """Define the tool parameters."""
        param0 = arcpy.Parameter(
            name="InputFeatureLayer",
            displayName="Capa de entrada",
            direction="Input",
            parameterType="Required",
            datatype="GPFeatureLayer"
        )

        param1 = arcpy.Parameter(
            name="CampoIdentificativo",
            displayName="Campo de identificación de las entidades",
            direction="Input",
            parameterType="Required",
            datatype="Field"
        )
        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["Text", "GUID", "GlobalID", "Date", "TimeOnly", "DateOnly", "TimestampOffset"]        

        param2 = arcpy.Parameter(
            name="GDBSalida",
            displayName="GDB de salidad de los resultados",
            direction="Input",
            parameterType="Required",
            datatype="DEWorkspace"
        )

        param3 = arcpy.Parameter(
            name="nombreFeatureDataset",
            displayName="Nombre del Feature Dataset contenedor",
            direction="Input",
            parameterType="Required",
            datatype="GPString"
        )
        param3.value = "feat2gdb"
        
        params =[param0, param1, param2, param3]
        return params

    def isLicensed(self): # Es opcional
        # La herramienta usada (arcpy.conversion.LayerToKML()) está disponible en Basic, por tanto siempre está licenciado
        return True
    
    def updateMessages(self, parameters):
        # Comprobar que la salida es una GeoDatabase y no una carpeta        
        if parameters[2].altered and parameters[2].value:
            parameters[2].clearMessage()
            try:
                desc = arcpy.Describe(parameters[2].value)
                if desc.dataType != "Workspace" or not (desc.workspaceType in ["LocalDatabase", "RemoteDatabase"]):
                    parameters[2].setErrorMessage("\nDebe seleccionar una Geodatabase")
                #if desc.extension.lower() == "gpkg":
                #    parameters[2].setErrorMessage("\nLa salida no puede ser una Base de Datos de GeoPackage")
            except Exception as e:
                parameters[2].setErrorMessage(f"\nError al comprobar el Workspace de salida: {e}")
                return
        if parameters[3].altered:
            parameters[3].clearMessage()
            if " " in parameters[3].valueAsText:
                parameters[3].setErrorMessage("El nombre del Feature Dataset no puede contener espacios en blanco")
            elif parameters[3].valueAsText[0].isdigit():
                parameters[3].setErrorMessage("El nombre del Feature Dataset no puede comenzar por un número")
            elif not re.match(r'^[A-Za-z0-9_]+$', parameters[3].valueAsText):
                parameters[3].setErrorMessage("El nombre del Feature Dataset sólo puede contener letras y números")
            else:
                arcpy.env.workspace = parameters[2].valueAsText
                fds_existentes = arcpy.ListDatasets("*", "Feature")                
                if parameters[3].valueAsText in fds_existentes:
                    parameters[3].setErrorMessage(f"Ya existe un Feature Dataset con el mismo nombre que se indica en la opción.")
        return

    def updateParameters(self, parameters):
        # desactivar el parámetro del nombre del feature dataset si se elige una BBDD Geopackage
        parameters[3].enabled = True
        if parameters[2].altered and parameters[2].value:
            desc = arcpy.Describe(parameters[2].value)
            if desc.extension.lower() == "gpkg":
                parameters[3].enabled = False
        return
    
    def execute(self, parameters, messages):
        arcpy.AddMessage(f"\n{self.label}:\n\n{self.description}")
        try:
            arcpy.AddMessage(f"Inicio de la ejecución de {self.alias}")
            self.numero_registros = arcpy.management.GetCount(parameters[0].value)
            arcpy.SetProgressor("step", f"Comienza el procesado de {self.numero_registros} registros", 0, int(self.numero_registros.getOutput(0)), 1)
            self.ExtraerFeratures2GDB(parameters)
            arcpy.AddMessage(f"Fin correcto de la ejecución")
        except Exception as ex:
            arcpy.AddError(f"ERROR En EXECUTE >>> {ex}")
            return

    def ExtraerFeratures2GDB(self, parameters):
        # Si la capa de entrada tiene sistema de referencia, el sr del feature dataset será ese y si no, el del mapa
        try:
            desc = arcpy.Describe(parameters[0].value)
            if desc.spatialReference:
                sr = desc.spatialReference
            else:
                sr = self.mapa.spatialReference
            
            # crear FeatureDataset
            try:
                desc = arcpy.Describe(parameters[2].value)
                if desc.extension.lower() == "gpkg": # si es un GeoPackage, no se crea el featDS
                    featDS = None
                else:
                    featDS = arcpy.management.CreateFeatureDataset(parameters[2].value, parameters[3].valueAsText, sr).getOutput(0)
                    arcpy.AddMessage(f"\nFeature Dataset creado en: {featDS}")
            except Exception as fdex:
                arcpy.AddError(f"\nError al crear el Feature Dataser: {fdex}")
                return

            # Seleccionar entidad y sacarla a GDB
            with arcpy.da.SearchCursor(parameters[0].value, ['OID@', parameters[1].valueAsText]) as cursor:
                i = 1
                for row in cursor:
                    featureClass, nombreFC = self.ObtenerFeatureClass(row[1], str(row[0]), featDS, parameters[2].valueAsText)
                    sql = f"OBJECTID = {row[0]}"
                    arcpy.conversion.ExportFeatures(parameters[0].value, featureClass, sql)
                    arcpy.SetProgressorPosition(i)
                    arcpy.SetProgressorLabel(f"Procesados {i} de {self.numero_registros} registros")
                    arcpy.AddMessage(f"creada la capa {nombreFC}")
                    i+=1
        except Exception as ex:
            arcpy.AddError(f"ERROR en Extración de entidades a GDB >>> {ex}")
            return

    def ObtenerFeatureClass(self, nombre, oid, featDS, gdb):
        nombre = str(nombre).strip() if nombre else ""                          # si nombre contiene algo .strip elimina espacios en blanco al principio y al final, si no le asigna valor ""
        if not nombre or re.match(r'^\d', nombre):                              # si nombre "" o vacío o empieza (^) por dígito del 0 al 9 
            nombre = "SN_" + f"{oid}"
        
        nombre = re.sub(r'[^a-zA-Z0-9_]', "_", nombre)                          # re --> regex (expresiones regulares) .sub (susituir) r'[^a-zA-Z0-9_]' es el patrón que no permite espacio, ni tildes ni símbolos, ni ñ y lo sustituye por "_"
        
        nombre_salida = nombre
        if featDS is not None:                                                   # si es un geopackage featDS vendrá como none
            i = 1            
            while arcpy.Exists(os.path.join(os.path.dirname(featDS), nombre_salida)):      # os.path.dirname(featDS) es el directorio del featDatSet, que es la GDB
                i += 1
                nombre_salida = f"{nombre}_{i}"                
            
            featureClass = os.path.join(featDS, nombre_salida)
        else:
            nombre_salida = f"{nombre}_{oid}"
            featureClass = os.path.join(gdb, nombre_salida)
        
        return featureClass, nombre_salida

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
# endregion