# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Geocode
Description          : This plugin allows user to geocode with following services : 
                       Pelias, Nominatim(OSM), GoogleV3, Bing.The results are 
                       stored in temporary layer, that contains address information, 
                       XY coordinates in specific coordinate reference system,
                       XY coordinates from reference database and geocoder service name.
Date                 : 15/August/2018
copyright            : Wojciech Sukta
email                : suktaa.wojciech@gmail.com
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

from PyQt4 import QtGui, uic



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Select_address_dialog.ui'))

FORM_CLASS_2, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Ungeocoded_list.ui'))

FORM_CLASS_3, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Finish_dialog.ui'))

class select_box(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(select_box, self).__init__(parent)
        self.setupUi(self)

class ungeocoded_list(QtGui.QDialog, FORM_CLASS_2):
    def __init__(self, parent=None):
        super(ungeocoded_list, self).__init__(parent)
        self.setupUi(self)

class finish_dialog(QtGui.QDialog, FORM_CLASS_3):
    def __init__(self, parent=None):
        super(finish_dialog, self).__init__(parent)
        self.setupUi(self)


