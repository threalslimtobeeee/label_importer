import pandas as pd
import sqlite3
from qgis.core import (
    QgsProject, QgsDataSourceUri,
    QgsPalLayerSettings, QgsVectorLayerSimpleLabeling, 
    QgsTextFormat, QgsVectorLayerUtils
)


class labelDataImporter:
    def __init__(self, layer, id_field, sqlite_path, label_fields_table, aux_data_layer_name, qml_file_path=None):
        self.layer = layer
        self.id_field = id_field
        self.sqlite_path = sqlite_path
        self.label_fields_table = label_fields_table
        self.aux_data_layer_name = aux_data_layer_name
        self.qml_file_path = qml_file_path

    def importAuxiliaryLayer(self):
        # Drop the auxiliary layer before creating a new one
        aux_layer = self.layer.auxiliaryLayer()
        aux_storage = QgsProject.instance().auxiliaryStorage()
        if aux_layer:
            aux_layer = self.layer.auxiliaryLayer()
            provider = aux_layer.dataProvider()
            uri_string = provider.dataSourceUri()
            uri = QgsDataSourceUri(uri_string)
            aux_storage.deleteTable(uri)
            aux_layer = None

        idx = self.layer.fields().indexOf(self.id_field)
        aux_key_field = self.layer.fields().field(idx)
        aux_layer = aux_storage.createAuxiliaryLayer(aux_key_field, self.layer)
        self.layer.setAuxiliaryLayer(aux_layer)

        # Connect to the GeoPackage file
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        layer_settings = QgsPalLayerSettings()
        text_format = QgsTextFormat()
        label_settings = QgsPalLayerSettings()
        label_settings.setFormat(text_format)

        # Apply labeling settings to the layer
        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        self.layer.setLabeling(labeling)
        self.layer.setLabelsEnabled(True)

        aux_properties = cursor.execute(f"SELECT * FROM {self.label_fields_table}")
        cols = [column[0] for column in aux_properties.description]
        results = pd.DataFrame.from_records(data=aux_properties.fetchall(), columns=cols)
        for index, row in results.iterrows():
            name = row["name"]
            if name:
                aux_layer.createProperty(getattr(QgsPalLayerSettings, name), self.layer, True)

        label_rows = cursor.execute(f"SELECT * FROM {self.aux_data_layer_name}")
        cols = [column[0] for column in label_rows.description]
        results = pd.DataFrame.from_records(data=label_rows.fetchall(), columns=cols)
        for index, row in results.iterrows():
            feature = QgsVectorLayerUtils.createFeature(aux_layer)
            for col in cols:
                if col != 'fid':
                    try:
                        feature.setAttribute(col, row[col])
                    except Exception as e:
                        print(f"Error setting attribute {col}: {e}")
            aux_layer.addFeature(feature)

        aux_layer.commitChanges()
        aux_layer.updateExtents()
        aux_layer.save()

        if aux_layer:
            QgsProject.instance().removeMapLayer(aux_layer.id())
            aux_layer = None

        conn.close()

