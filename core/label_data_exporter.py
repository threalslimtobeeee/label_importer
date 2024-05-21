import os
from qgis.core import QgsProject, QgsMapLayer, QgsVectorFileWriter, QgsField, QgsVectorLayer,  QgsFeature
from qgis.PyQt.QtCore import QVariant
import tempfile
import uuid

class label_data_exporter():
    def __init__(self, project_file_path, layer_id):
        self.project_file_path = project_file_path
        self.project = QgsProject()
        self.project.read(project_file_path)
        self.layer  = self.project.mapLayer(layer_id)

        self.temp_dir = tempfile.gettempdir()
        self.export_id = str(uuid.uuid1()).replace('-','')

    def export_auxiliary_layer(self):
        aux_layer = self.layer.auxiliaryLayer()
        aux_layer.selectAll()
        output_layer_name = 'aux_ly_'+ self.export_id
        self.sqlite_path = os.path.join(self.temp_dir, self.export_id +'.gpkg')

        aux_layer.selectAll()
        options                      = QgsVectorFileWriter.SaveVectorOptions()
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        options.EditionCapability    = QgsVectorFileWriter.CanAddNewLayer  
        options.layerName            = output_layer_name
        options.fileEncoding         = "UTF-8"
        options.driverName           = "GPKG"
        context = QgsProject.instance().transformContext()

        if not os.path.exists(self.sqlite_path ): # if the ouput file doesn't already exist
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        QgsVectorFileWriter.writeAsVectorFormatV3(aux_layer, self.sqlite_path ,context,options)

        label_fields_table = 'aux_fi_'+ self.export_id
        
        fields = fields = [
            QgsField('id', QVariant.Int),  # Example field
            QgsField('name', QVariant.String)]
            
        n = 0
        field_names = []
        for field in aux_layer.fields():
            field_pro_def = aux_layer.propertyDefinitionFromField(field)
            insert_statement = f"{field.type()} ('{field_pro_def.name()}')"
            print(insert_statement)
            new_field = QgsField(field_pro_def.name())
            new_field.setType(field.type())
            field_names.append([n,field_pro_def.name()])
            n += 1 
        
        
        # Create a QgsVectorLayer with the desired fields and no geometry
        temp_layer = QgsVectorLayer('None?crs=epsg:4326', label_fields_table, 'memory')
        temp_layer_data_provider = temp_layer.dataProvider()
        
        # Add fields to the layer
        for field in fields:
            temp_layer.addAttribute(field)
            
        temp_layer_data_provider.addAttributes(fields)
        # Create the table in the GeoPackage
        temp_layer_data_provider.createAttributeIndex(0)
        temp_layer.updateFields()
            
        # Start editing
        temp_layer.startEditing()
        
        # Insert features
        for row in field_names:
            feature = QgsFeature()
            feature.setFields(temp_layer.fields())
            feature.setAttributes(row)
            temp_layer_data_provider.addFeature(feature)
        
        # Commit changes
        temp_layer.commitChanges()
        # processing.run("native:package", {'LAYERS': temp_layer, 'OUTPUT': sqlite_path, 'OVERWRITE': False})
        
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        options.EditionCapability = QgsVectorFileWriter.CanAddNewLayer  
        options.layerName = label_fields_table
        options.fileEncoding = "UTF-8"
        options.driverName = "GPKG"
        context = QgsProject.instance().transformContext()
        
        if not os.path.exists(self.sqlite_path ): # if the ouput file doesn't already exist
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        
        QgsVectorFileWriter.writeAsVectorFormatV3(temp_layer, self.sqlite_path ,context,options)

        sqlite_path = self.sqlite_path
        return (sqlite_path)

    def style_export(self):
        file_path =  os.path.join(self.temp_dir, f"{self.export_id}.qml")
        self.layer.saveNamedStyle(file_path, categories = QgsMapLayer.Symbology | QgsMapLayer.Labeling | QgsMapLayer.Forms)
