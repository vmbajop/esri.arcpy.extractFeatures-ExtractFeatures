'''FUENTES
Plantilla: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-template-for-python-toolboxes.htm'''

import arcpy
import os
import datetime

class Toolbox(object):
    def __init__(self):
        self.label = "Extraer Features"
        self.alias = "ExtraerFeatures"

        # Lista de tools en la toolbox
        self.tools = [FeatureToKML]

class FeatureToKML(object):
    def __init__(self):
        # self.name = "FeatureToKML"
        self.version = "2.0"
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
            displayName="Campo identificativo",
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
    
# region NO USADOS
    def isLicensed(self): # Es opcional
        # La herramienta usada (arcpy.conversion.LayerToKML()) está disponible en Basic, por tanto siempre está licenciado
        return True
    
    def updateMessages(self, parameters):
        # Solo si el usuario ha cambiado el parámetro y ha seleccionado una carpeta
        parameters[3].clearMessage()
        if parameters[3].altered and parameters[3].valueAsText:
            try:
                if os.listdir(parameters[3].valueAsText):
                    parameters[3].setErrorMessage("La carpeta contiene archivos y sin embargo debería estar vacía.")
                else:
                    parameters[3].clearMessage()
            except Exception as e:
                parameters[3].setErrorMessage(f"Error al acceder a la carpeta: {e}")

        return

    def updateParameters(self, parameters):
        
        return
# endregion    

# region EXECUTE
    def execute(self, parameters, messages):
        arcpy.AddMessage(f"\n{self.label}:\n{self.description}\nversion: {self.version}")
        arcpy.AddMessage(f"\nLa carpeta de salidad es {parameters[3].value}")
        try:           
            self.numero_registros = arcpy.management.GetCount(parameters[0].value)
            arcpy.SetProgressor("step", f"Comienza el procesado de {self.numero_registros} registros", 0, int(self.numero_registros.getOutput(0)), 1)

            self.ComprobarExistenciaCapaTemporalTOC()

            self.ExtraerFeature2KML(parameters)
        except Exception as e:
            arcpy.AddError(f"ERROR En EXECUTE >>> '{e}")
    
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

                    # arcpy.management.MakeFeatureLayer(capa_entrada, self.nombre_capa_temporal, sql)
                    """ nombre_kml = prenombre_capa_salida + f"{row[1]}" + ".kml"
                    # Comprobar si existe el nombre y renombrar
                    count = 1
                    while arcpy.Exists(os.path.join(parameters[3].valueAsText, nombre_kml)):
                        nombre_kml = prenombre_capa_salida + f"{row[1]}"+ str(count) + ".kml"
                        count += 1 """
                    nombre_kml = self.GenerarNombreCapaSalida_Contador(parameters, row)
                    # -----------------------------------------
                    
                    # Separar la extension kml del nombre del archivo
                    nombre_sin_extension, extension = os.path.splitext(nombre_kml)

                    arcpy.management.MakeFeatureLayer(capa_entrada, nombre_sin_extension + "fl", sql)

                    arcpy.conversion.LayerToKML(nombre_sin_extension + "fl", parameters[3].valueAsText + "\\" + nombre_kml)
                    arcpy.management.Delete(nombre_sin_extension + "fl")
                    arcpy.SetProgressorLabel(f"Procesados {i} de {self.numero_registros} registros")
                    arcpy.SetProgressorPosition(i)
                    i = i + 1
                    
                arcpy.AddMessage("\nFinalizado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
        except Exception as e:
            arcpy.AddError(f"\nERROR EN LA EXTRACCIÓN >>> '{e}")

    def GenerarNombreCapaSalida_Contador(self, parameters, row):
        nombre_kml = parameters[2].valueAsText + f"{row[1]}" + ".kml"
        # Comprobar si existe el nombre y renombrar
        count = 1
        while arcpy.Exists(os.path.join(parameters[3].valueAsText, nombre_kml)):
            nombre_kml = parameters[2].valueAsText + f"{row[1]}"+ str(count) + ".kml"
            count += 1
        return nombre_kml
# endregion

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return