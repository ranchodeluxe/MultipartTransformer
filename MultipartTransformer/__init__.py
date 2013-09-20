# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MultipartTransformer
                                 A QGIS plugin
 Converts multi-part shapefile polygons into single-part geometries
                             -------------------
        begin                : 2013-09-19
        copyright            : (C) 2013 by Greg Corradini, ChopShop
        email                : gregcorradini@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "InaSAFE Multipart Transformer"


def description():
    return "Converts multi-part shapefile polygons into single-part geometries"


def version():
    return "Version 0.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"

def author():
    return "Greg Corradini, ChopShop"

def email():
    return "gregcorradini@gmail.com"

def classFactory(iface):
    # load MultipartTransformer class from file MultipartTransformer
    from multiparttransformer import MultipartTransformer
    return MultipartTransformer(iface)
