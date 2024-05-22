import os
import pandas as pd
from qgis.core import QgsProject, QgsMapLayer, QgsVectorFileWriter, QgsField, QgsVectorLayer,  QgsFeature, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling, QgsTextFormat, QgsVectorLayerUtils
from qgis.PyQt.QtCore import QVariant
import sqlite3
import tempfile
import uuid

class label_data_importer():
    def __init__(self, layer, id_field, sqlite_path, label_fields_table, aux_data_layer_name, qml_file_path = None):
        self.layer              = layer
        self.id_field           = id_field
        self.sqlite_path        = sqlite_path
        self.label_fields_table = label_fields_table
        self.aux_data_layer_name  = aux_data_layer_name
        self.qml_file_path      = qml_file_path

    def import_auxiliary_layer(self):
        idx           = self.layer.fields().indexOf(self.id_field)
        aux_key_field = self.layer.fields().field(idx)
        aux_storage   = QgsProject.instance().auxiliaryStorage()
        aux_Layer     = aux_storage.createAuxiliaryLayer(aux_key_field, self.layer)
        self.layer.setAuxiliaryLayer(aux_Layer)


        # Connect to the GeoPackage file
        conn = sqlite3.connect(self.sqlite_path)

        # Create a cursor object
        cursor = conn.cursor()

        layer_settings  = QgsPalLayerSettings()

        text_format = QgsTextFormat()

        label_settings = QgsPalLayerSettings()
        label_settings.setFormat(text_format)

        # Apply labeling settings to the layer
        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        self.layer.setLabeling(labeling)
        self.layer.setLabelsEnabled(True)


        aux_properties = cursor.execute(f"SELECT * FROM {self.label_fields_table}")
        cols = [column[0] for column in aux_properties.description]
        results= pd.DataFrame.from_records(data  = aux_properties.fetchall(), columns = cols)
        for index, row in results.iterrows():
            name = row["name"]
            if name != None and name != '':
                print(name)
                aux_Layer.createProperty(getattr(QgsPalLayerSettings, name), self.layer, True)
        aux_Layer.createProperty(QgsPalLayerSettings.PositionX, self.layer, True)



        label_rows = cursor.execute(f"SELECT * FROM {self.aux_data_layer_name}")
#
        cols = [column[0] for column in label_rows.description]
        results= pd.DataFrame.from_records(data  = label_rows.fetchall(), columns = cols)
        for index, row in results.iterrows():
                feature = QgsVectorLayerUtils.createFeature(aux_Layer)
                for col in cols:
                    try:
                        feature.setAttribute(col, row[col])
                    except:
                        pass
                aux_Layer.addFeature(feature)


        aux_Layer.commitChanges()
        aux_Layer.updateExtents()
        aux_Layer.save()

    def style_import(self):
        pass