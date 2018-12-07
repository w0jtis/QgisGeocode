# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Geocode
Description          : Plugins that allows user with following services:Pelias,
                       Nominatim(OSM), GoogleV3, Photon.
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

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Geocode class from file geocoding.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .geocoding import Geocode
    return Geocode(iface)
