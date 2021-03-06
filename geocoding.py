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


from __future__ import division
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import resources
from geocoding_dialog import Geocoding_dialog
from other_dialogs import *
from qgis.gui import QgsGenericProjectionSelector
import os
import sys



class Geocode:

    def __init__(self, iface):
        self.pelias_domain='localhost:4000'
        self.epsg=4326
        self.selected_geocoder=''
        self.id_layer=''
        self.encode_addr=''
        self.iface = iface
        self.canvas=iface.mapCanvas()
        libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs')
        if not libpath in sys.path:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs'))
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = Geocoding_dialog()
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Geocode_{}.qm'.format(locale))


        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)




        self.actions = []
        self.menu = self.tr(u'&Geocode')
        self.toolbar = self.iface.addToolBar(u'Geocode')
        self.toolbar.setObjectName(u'Geocode')
        self.dlg.pelias_domain.setPlaceholderText("Enter domain without http index e.g. 'localhost:4000'")
        self.dlg.service_api.setPlaceholderText("Enter your Google or Bing Maps api key")
        self.dlg.epsg_data.setPlaceholderText("Enter EPSG code of reference data, default : 4326")


    def __del__(self):
        pass


    def tr(self, message):
        return QCoreApplication.translate('Geocode', message)


    def add_action(
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


        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        icon_path = ':/plugins/Geocode/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Geocoding'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Geocode'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def choose_geocoder(self):
        geocoder_list = ["Pelias","GoogleV3","Nominatim", "Bing"]
        return geocoder_list

    def set_projection(self):
        proj_selector = QgsGenericProjectionSelector()
        proj_selector.setMessage(theMessage=u'Select the projection for geocoded addresses and for map canvas')
        proj_selector.exec_()
        sel_crs = proj_selector.selectedAuthId()
        return  sel_crs

    def coord_transformation(self,point,proj):
        act_crs = QgsCoordinateReferenceSystem()
        if len(self.dlg.epsg_data.text())>=4:
            self.epsg=int(self.dlg.epsg_data.text())
        act_crs.createFromSrid(self.epsg)
        dest_crs = QgsCoordinateReferenceSystem(proj)
        tr = QgsCoordinateTransform(act_crs,dest_crs)
        point_after_transformation = tr.transform(point)
        return point_after_transformation


    def geocoder_instacne(self):

        service_api = self.dlg.service_api.text()
        if len(self.dlg.pelias_domain.text())>0:
            self.pelias_domain = self.dlg.pelias_domain.text()
        geocoder_list=self.choose_geocoder()
        self.selected_geocoder= geocoder_list[self.dlg.geocoder_box.currentIndex()]
        geocoder_class = self.selected_geocoder
        try:
            self.geocoders
        except:
            from geopy import geocoders
            self.geocoders = geocoders
        geocoder = getattr(self.geocoders,geocoder_class)
        if self.selected_geocoder == u'Pelias':
            return geocoder(domain = self.pelias_domain,timeout=20,scheme='http'),self.selected_geocoder
        elif self.selected_geocoder == u'GoogleV3' or self.selected_geocoder ==u'Bing':
            return geocoder(api_key=service_api,timeout=20),self.selected_geocoder
        elif self.selected_geocoder==u'Nominatim':
            return geocoder(user_agent="Geocode_Qgis_Plugin",timeout=20),self.selected_geocoder
        else:
            return geocoder(timeout=20), self.selected_geocoder

    def proccesing_point(self,point,place):
        self.point_lon_lat=point
        point = QgsPoint(point[1], point[0])
        self.iface.mapCanvas().mapRenderer().setDestinationCrs(QgsCoordinateReferenceSystem(self.sel_proj))
        if self.epsg == self.sel_proj:
            point_trf = point
        else:
            point_trf = self.coord_transformation(point,self.sel_proj)
        self.canvas.setCenter(point_trf)
        self.canvas.zoomScale(1000)
        self.canvas.refresh()
        self.create_layer(point_trf,unicode(place))

    def create_layer(self,point,address):
        if not QgsMapLayerRegistry.instance().mapLayer(self.id_layer):
            self.layer= QgsVectorLayer("Point","Results of Geocoding", "memory")
            self.provider = self.layer.dataProvider()
            self.layer.setCrs(self.canvas.mapRenderer().destinationCrs())
            self.provider.addAttributes([QgsField("Address information from layer", QVariant.String)])
            self.provider.addAttributes([QgsField("Address result", QVariant.String)])
            self.provider.addAttributes([QgsField("X_coordinate", QVariant.Double)])
            self.provider.addAttributes([QgsField("Y_coordinate", QVariant.Double)])
            self.provider.addAttributes([QgsField("LON_WGS84", QVariant.Double)])
            self.provider.addAttributes([QgsField("LAT_WGS84", QVariant.Double)])
            self.provider.addAttributes([QgsField("Name of geocoding service", QVariant.String)])

            self.layer.updateFields()
            QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        self.id_layer = self.layer.id()

        field = self.layer.pendingFields()
        feat = QgsFeature(field)
        feat.setGeometry(QgsGeometry.fromPoint(point))
        feat['Address information from layer']=self.encode_addr.decode('utf-8')
        feat['Address result'] = address
        feat['X_coordinate'] = point[0]
        feat['Y_coordinate'] = point[1]
        feat['LON_WGS84']=self.point_lon_lat[0]
        feat['LAT_WGS84']=self.point_lon_lat[1]
        feat['Name of geocoding service']= self.geocoder_instacne()[1]
        self.provider.addFeatures([ feat ])
        self.layer.updateExtents()
        self.canvas.refresh()


    def prepare_to_geocode(self):
        self.dlg.geocoder_box.clear()
        self.dlg.layer_combo.clear()
        layers = [layer for layer in self.iface.legendInterface().layers() if layer.type() == QgsMapLayer.VectorLayer]
        layer_list=[]
        for layer in layers:
            if layer.type() == 0:
                typ = QgsWKBTypes.displayString(int(layer.wkbType()))
                if typ in ('Point','NoGeometry'):
                    layer_list.append(layer.name())
        self.dlg.layer_combo.addItems(layer_list)

        def layer_field ():
            self.dlg.column_combo.clear()
            slected_layer_index = self.dlg.layer_combo.currentIndex()
            self.selected_layer= layers[slected_layer_index]
            fields = self.selected_layer.pendingFields()
            field_names = []
            for field in fields:
                self.dlg.column_combo.clear()
                field_names.append(field.name())
                self.dlg.column_combo.addItems(field_names)
            return fields
        self.selcted_layer_field=layer_field()
        self.dlg.layer_combo.currentIndexChanged.connect(layer_field)
        self.dlg.geocoder_box.addItems(self.choose_geocoder())
        self.dlg.show()
        execute = self.dlg.exec_()
        return execute

    def check_that_layer_field_is_string(self):
        field=self.selected_layer.pendingFields()
        if field[self.dlg.column_combo.currentIndex()].type()==10:
            return True
        else:
            message_layer_field = QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate(u'Geocode',u'Check that type of selected column is a "String"'),\
                                                          QCoreApplication.translate(u'Geocdoe',u' You have to choose a column whose type is a "String"     '))
            return message_layer_field

    def check_the_geocoding_result(self,result_from_geocoder):

        import json
        from shapely.geometry import shape, Point
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Utils')
        file_to_open=file_path + '/'+'Poland_AL2.GeoJson'
        checked_result=[]
        with open(file_to_open,'r') as file_with_boundary:
            js=json.load(file_with_boundary)


        if result_from_geocoder != None:
            for place,point in result_from_geocoder:
                for feature in js['features']:
                    polygon = shape(feature['geometry'])
                    point_to_check=Point(point[1],point[0])
                    if polygon.contains(point_to_check):
                        checked_result.append((place, point))
            if len(checked_result)>0:
                return checked_result
            else:
                return None
        else:
            return None



    def geocoding(self,execute):


        if execute and self.check_that_layer_field_is_string()==True :
            self.sel_proj = self.set_projection()
            list_of_ungeocoded_address=[]
            number_of_all_addresses = self.selected_layer.featureCount()
            for feat in self.selected_layer.getFeatures():
                result_places = {}
                attrs = feat.attributes()
                geocoder = self.geocoder_instacne()[0]
                str_addr =attrs[self.dlg.column_combo.currentIndex()]
                encode_addr= str_addr.encode('utf-8')
                self.encode_addr=encode_addr
                try :
                    geocoding_result = geocoder.geocode(encode_addr, exactly_one=False)
                    #pelias_geocoding_result=geocoder.geocode(encode_addr, exactly_one=False) dopracować to itd

                except Exception,self.exception:
                    QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate(u'Geocode',u'Gecoder encounter some problem'),\
                    QCoreApplication.translate(u'Geocode',
                    u'1) Check your intennet connection.\n2) Chcek that you have given a suitable url address of Pelias instance.\n3) Check that you have given correct api key for Bing or Google service.'))
                    break
                try:
                    geocoding_result_checked=self.check_the_geocoding_result(geocoding_result)
                except ImportError :
                    QMessageBox.information(self.iface.mainWindow(),QCoreApplication.translate(u'Geocode', u'Geocoder can not import the Shapely library'),\
                    QCoreApplication.translate(u'Geocode', u'Check that Shapely library is in Utils folder in plugin dictionary'))
                    break

                if geocoding_result_checked:
                    if self.geocoder_instacne()[1] == u'Pelias':
                        cnt = 0
                        for place, point in geocoding_result:
                            raw_result = geocoding_result[cnt]
                            place = raw_result.raw[u'properties'][u'label']  + u', county: '+ raw_result.raw[u'properties'][u'county']+\
                                    u', accuracy parameters '+ u'[ match type:' + raw_result.raw[u'properties'][u'match_type'] + u' source '+raw_result.raw[u'properties'][u'source']+u' ]'
                            result_places[place] = point
                            cnt += 1
                    else:
                        for place, point in geocoding_result_checked:
                            result_places[place] = point

                    if len(result_places) == 1:
                        self.proccesing_point(point, place)
                    else:
                        QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate(u'Geocode',u'Geocoder found more than one location'),\
                                                QCoreApplication.translate(u'Geocdoe',u'Geocoder found more than one loaction for searched address : %s' % str_addr,encoding = 1))
                        place_sel_dlg=select_box()
                        place_sel_dlg.select_appropriate_address.addItems(result_places.keys())
                        place_sel_dlg.show()
                        result=place_sel_dlg.exec_()
                        if result:
                            point = result_places[unicode(place_sel_dlg.select_appropriate_address.currentText())]
                            self.proccesing_point(point,place_sel_dlg.select_appropriate_address.currentText())
                        else:
                            list_of_ungeocoded_address.append(encode_addr.decode('utf-8'))
                else:
                    list_of_ungeocoded_address.append(encode_addr.decode('utf-8'))

            if len(result_places)>0:
                matched_addresses = number_of_all_addresses-len(list_of_ungeocoded_address)
                match_rate = matched_addresses/number_of_all_addresses*100
                finish_dlg=finish_dialog()
                finish_dlg.pBar.setValue(match_rate)
                expresion= '%d / %d' % (matched_addresses,number_of_all_addresses)
                finish_dlg.amount.setText(expresion)
                finish_dlg.exec_()

            if len(list_of_ungeocoded_address)>=1:
                ungeocoded=ungeocoded_list()
                ungeocoded.un_address.append('The geocoder has not found the following addresses :')
                ungeocoded.un_address.append('\n'.join(list_of_ungeocoded_address))
                ungeocoded.exec_()




    ''' To do - add some dialog box to geocode addresses which user type in specific field
    def type_to_geocode(self):
        self.dlg.find_address.clear()
        type_addr=self.dlg.find_address.text()

        return type_addr
    '''


    def run(self):

        self.geocoding(self.prepare_to_geocode())

        return
