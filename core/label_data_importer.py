import os
from qgis.core import QgsProject, QgsMapLayer, QgsVectorFileWriter, QgsField, QgsVectorLayer,  QgsFeature
from qgis.PyQt.QtCore import QVariant
import tempfile
import uuid

class label_data_importer():
    def __init__(self, layer, id_field, sqlite_path, label_fields_table, output_layer_name, qml_file_path = None):
        self.layer              = layer
        self.id_field           = id_field
        self.sqlite_path        = sqlite_path
        self.label_fields_table = label_fields_table
        self.output_layer_name  = output_layer_name
        self.qml_file_path      = qml_file_path

    def import_auxiliary_layer(self):
        #aux_key_field = self.layer.fields().field(self.layer.fields().indexOf(uniqe_identifier))
        aux_storage   = QgsProject.instance().auxiliaryStorage()
        aux_Layer     = aux_storage.createAuxiliaryLayer(self.id_field, self.layer)
        self.layer.setAuxiliaryLayer(aux_Layer)

    def style_import(self):
        pass