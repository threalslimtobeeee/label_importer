# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataDefinedLabelImporter
                                 A QGIS plugin
 Helps you to import Labeldata, stored in an auxiliary Layer from another Project.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-10
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Tobias
        email                : heitob903@outlook.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.utils import iface
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QMessageBox
from label_importer.core.label_data_exporter  import labelDataExporter
from label_importer.core.label_data_importer  import labelDataImporter
from label_importer.gui.label_importer_dialog import DataDefinedLabelImporterDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog

import os.path

class DataDefinedLabelImporter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DataDefinedLabelImporter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Auxiliary Labeldata Importer')
        self.first_start = None
        self.run_button_connected = False
        self.dlg = None
        self.exporter = None  # Added to track exporter instance
        self.importer = None  # Added to track importer instance
        self.auxiliary_layer = None  # Track auxiliary layer to clean up if necessary

 

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DataDefinedLabelImporter', message)


    def addAction(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/label_importer/icon.png'
        self.addAction(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Auxiliary Labeldata Importer'),
                action)
            self.iface.removeToolBarIcon(action)

    def showConfirmationDialog(self):
        """Shows a dialog if data will be overwritten"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmation")
        msg_box.setText("""This tool will delete the auxiliary layer of the selected targer layer and overwrite its label settings. Are you sure you want to proceed?""")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        result = msg_box.exec_()
        if result == QMessageBox.Yes:
            return True
        else:
            return False
           
    def run(self):
        """Run method that performs all the real work"""
        self.run_button_connected = ''

        if self.first_start:
            self.first_start = False
            
        self.dlg = DataDefinedLabelImporterDialog()
        self.dlg.show()
        self.dlg.buttonBox.accepted.connect(self.initiateProcess)
        self.dlg.buttonBox.rejected.connect(lambda: self.dlg.close())

    def initiateProcess(self):
        """Call Confirmation Dialog if necessary"""
        target_layer = self.dlg.targetLayer.currentLayer()
        if target_layer.auxiliaryLayer():
            if self.showConfirmationDialog():
                self.runProcess(target_layer)
        else:
            self.runProcess(target_layer)
    
    def runProcess(self, target_layer):
        """Run Process
            export auxiliary data and qml
            import auxiliary data and qml"""
        project_file_path = self.dlg.projectFile.filePath()
        source_layer = self.dlg.LayerToCopyWidget.treeWidget.currentItem().data(0, 1)
        self.dlg.progressBar.setValue(20)

        # initiate exporter
        exporter = labelDataExporter(project_file_path, source_layer)
        sqlite_path, label_fields_table, output_layer_name = exporter.exportAuxiliaryLayer()
        self.dlg.progressBar.setValue(40)
        if self.dlg.checkBox.checkState() == 2:
            qml_path = exporter.styleExport(True)
        else:
            qml_path = exporter.styleExport()
        self.dlg.progressBar.setValue(80)
        id_field = self.dlg.targetIdField.currentField()

        # initiate importer
        importer = labelDataImporter(target_layer, id_field, sqlite_path, label_fields_table, output_layer_name, qml_path)
        importer.importAuxiliaryLayer()
        target_layer.loadNamedStyle(qml_path)
        # refresh the layer tree view and map canvas
        target_layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(target_layer.id())
        iface.mapCanvas().refresh()
        self.dlg.progressBar.setValue(100)

