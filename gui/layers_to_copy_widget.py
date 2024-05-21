# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AttachmentNamingTableWidget
                                 A QGIS plugin
 Sync your projects to QField
                             -------------------
        begin                : 2023-02-26
        git sha              : $Format:%H$
        copyright            : (C) 2023 by OPENGIS.ch
        email                : info@opengis.ch
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

import os
from pathlib import Path
from typing import Dict, Optional

from qgis.PyQt.QtWidgets import  QWidget
from qgis.PyQt.uic import loadUiType

LayersConfigWidgetUi, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), r"../ui/layers_to_copy_widget.ui")
)

DirsToCopySettings = Dict[str, bool]

class LayerToCopyWidget(QWidget, LayersConfigWidgetUi):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)