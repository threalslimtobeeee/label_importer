import uuid
import tempfile
import os
from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer, QgsField, QgsFeature, QgsMapLayer
from PyQt5.QtCore import QVariant

class labelDataExporter:
    """gets necessary information to 
       save the label-placement-settings of
        a vector layer to a temporary sqlite-database """
    def __init__(self, project_file_path, layer_id):
        self.project_file_path = project_file_path
        self.project = QgsProject()
        self.project.read(project_file_path)
        self.layer = self.project.mapLayer(layer_id)
        self.temp_dir = tempfile.gettempdir()
        self.export_id = str(uuid.uuid1()).replace('-', '')

    def exportAuxiliaryLayer(self):
        """exports label-placement-settings to sqlite-database """
        aux_layer = self.layer.auxiliaryLayer()
        aux_layer.selectAll()
        output_layer_name = 'aux_ly_' + self.export_id
        self.sqlite_path = os.path.join(self.temp_dir, self.export_id + '.gpkg')

        # Export auxiliary layer to GeoPackage
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.fileEncoding = "UTF-8"
        options.driverName = "GPKG"
        options.layerName = output_layer_name
        options.EditionCapability = QgsVectorFileWriter.CanAddNewLayer
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        context = QgsProject.instance().transformContext()
        QgsVectorFileWriter.writeAsVectorFormatV3(aux_layer, self.sqlite_path, context, options)
        
        # Prepare the second table
        label_fields_table = 'aux_fi_' + self.export_id
        fields = [
            QgsField('id', QVariant.Int),
            QgsField('name', QVariant.String)
        ]
        field_names = []
        for n, field in enumerate(aux_layer.fields()):
            field_pro_def = aux_layer.propertyDefinitionFromField(field)
            field_names.append([n, field_pro_def.name()])

        temp_layer = QgsVectorLayer('None?crs=epsg:4326', label_fields_table, 'memory')
        temp_layer_data_provider = temp_layer.dataProvider()
        temp_layer_data_provider.addAttributes(fields)
        temp_layer.updateFields()
        temp_layer.startEditing()

        for row in field_names:
            feature = QgsFeature()
            feature.setFields(temp_layer.fields())
            feature.setAttributes(row)
            temp_layer_data_provider.addFeature(feature)

        temp_layer.commitChanges()

        # Add the second table to the same GeoPackage
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        options.layerName = label_fields_table
        options.EditionCapability = QgsVectorFileWriter.CanAddNewLayer
        QgsVectorFileWriter.writeAsVectorFormatV3(temp_layer, self.sqlite_path, context, options)

        return self.sqlite_path, label_fields_table, output_layer_name

        
    def styleExport(self, symbology_y_n=False):
        '''exports the layer style information either with or without symbology'''
        qml_file_path =  os.path.join(self.temp_dir, f"{self.export_id}.qml")
        if symbology_y_n:
            self.layer.saveNamedStyle(qml_file_path, categories = QgsMapLayer.Symbology | QgsMapLayer.Labeling)
        else:
            self.layer.saveNamedStyle(qml_file_path, categories = QgsMapLayer.Labeling)
        return qml_file_path
