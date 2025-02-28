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
        self.label = "Feature To KML"
        self.alias = "Feature2KML"        
        
        #DUDA DE SI SIRVEN
        self.description = "Extraer entidades de una capa para crear una nueva capa KML por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario."
        self.canRunInBackground = False
        self.version = "1.1.1"

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
        self.ruta_proyecto = proyecto.filePath
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
            name="NombreCarpetaResultados",
            displayName="Nombre de la carpeta de salidad de los resultados",
            direction="Input",
            parameterType="Required",
            datatype="GPString"
        )
        param3.value="Feature2KML_resultados"

        param4 = arcpy.Parameter(
            name="CarpetaResultados",
            displayName="Carpeta de salidad de los resultados",
            direction="Output",
            parameterType="Derived",
            datatype="DEFolder"
        )

        params =[param0, param1, param2, param3, param4]
        return params
    
# region NO USADOS
    def isLicensed(self): # Es opcional
        # La herramienta usada (arcpy.conversion.LayerToKML()) está disponible en Basic, por tanto siempre está licenciado
        return True
    
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[3].value:
            parameters[4].value = os.path.join(os.path.dirname(self.ruta_proyecto), parameters[3].valueAsText)
        else:
            # self.carpeta_resultado = os.path.join(os.path.dirname(self.ruta_proyecto), parameters[3].valueAsText)
            arcpy.AddError(f"\nNo hay carpeta de salida")
        return
# endregion    

# region EXECUTE
    def execute(self, parameters, messages):
        arcpy.AddMessage(f"\n{self.label}:\n{self.description}\nversion: {self.version}")
        arcpy.AddMessage(f"\nLa carpeta de salidad es {parameters[4].value}")
        try:           
            self.numero_registros = arcpy.management.GetCount(parameters[0].value)
            arcpy.SetProgressor("step", f"Comienza el procesado de {self.numero_registros} registros", 0, int(self.numero_registros.getOutput(0)), 1)

            self.ComprobarExistenciaCapaTemporalTOC()
            self.ComprobarExistenciaCarpetaResultados(parameters[3].valueAsText, parameters[4].valueAsText)

            self.ExtraerFeature2KML(parameters)
        except Exception as e:
            arcpy.AddError(f"ERROR En EXECUTE >>> '{e}")
    
    def ComprobarExistenciaCapaTemporalTOC(self):
        for capa in self.mapa.listLayers():
            if capa.name == self.nombre_capa_temporal:
                self.mapa.removeLayer(capa)
                arcpy.AddMessage(f"\nEliminada una capa con nombre '{self.nombre_capa_temporal}'")
        arcpy.AddMessage("\nComprobada la existencia de una capa temporal previa.")

    def ComprobarExistenciaCarpetaResultados(self, nombreCarpeta, carpeta_resultado):
        try:  
            if os.path.exists(carpeta_resultado):
                if not os.listdir(carpeta_resultado):
                    arcpy.AddMessage(f"\nLa carpeta '{carpeta_resultado}' existe, está vacía y se va a reutilizar")
                else:
                    fh = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    nuevo_nombre = f"{nombreCarpeta}_{fh}"
                    nueva_ruta = os.path.join(os.path.dirname(carpeta_resultado), nuevo_nombre)
                    os.rename(carpeta_resultado, nueva_ruta)
                    arcpy.AddWarning(f"\nExiste una carpeta con el nombre '{nombreCarpeta}' con contenido, por lo que se ha renombrada como '{nuevo_nombre}'")
                    self.CrearCarpetaResultados(nombreCarpeta, carpeta_resultado)
            else:
                self.CrearCarpetaResultados(nombreCarpeta, carpeta_resultado)
            
        except Exception as e:
            arcpy.AddError(f"\nERROR en COMPROBAR CARPETA >>> '{e}'")

    def CrearCarpetaResultados(self, nombreCarpeta, carpeta_resultado):
        os.makedirs(carpeta_resultado)
        arcpy.AddMessage(f"\nSe ha creado la carpeta '{nombreCarpeta}'")

    def ExtraerFeature2KML(self, parameters):
        try:
            capa_entrada = parameters[0].value
            campo_nombre = parameters[1].valueAsText
            prenombre_capa_salida = parameters[2].valueAsText

            with arcpy.da.SearchCursor(capa_entrada, ['OID@', campo_nombre]) as cursor:
                arcpy.AddMessage("\nIniciado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
                i = 1
                for row in cursor:
                    sql = f"OBJECTID = {row[0]}"
                    arcpy.management.MakeFeatureLayer(capa_entrada, self.nombre_capa_temporal, sql)
                    nombre_kml = prenombre_capa_salida + f"{row[1]}" + ".kml"
                    # Comprobar si existe el nombre y renombrar
                    count = 1
                    while arcpy.Exists(os.path.join(parameters[4].valueAsText, nombre_kml)):
                        nombre_kml = prenombre_capa_salida + f"{row[1]}"+ str(count) + ".kml"
                        count += 1
                    # -----------------------------------------
                    arcpy.conversion.LayerToKML(self.nombre_capa_temporal, parameters[4].valueAsText + "\\" + nombre_kml)
                    arcpy.management.Delete(self.nombre_capa_temporal)
                    arcpy.SetProgressorLabel(f"Procesados {i} de {self.numero_registros} registros")
                    arcpy.SetProgressorPosition(i)
                    i = i + 1
                    
                arcpy.AddMessage("\nFinalizado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
        except Exception as e:
            arcpy.AddError(f"\nERROR EN LA EXTRACCIÓN >>> '{e}")
# endregion

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return