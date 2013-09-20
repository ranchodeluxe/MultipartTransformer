# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_multiparttransformer.ui'
#
# Created: Fri Sep 20 12:03:21 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import os

class Ui_MultipartTransformer(object):
    def setupUi(self, MultipartTransformer):
        self.abspath = os.path.dirname( os.path.abspath( __file__ ) ) 
        MultipartTransformer.setObjectName( unicode("MultipartTransformer") )
        MultipartTransformer.resize(394, 408)
        MultipartTransformer.setToolTip(unicode(""))
        self.listWidget = QtGui.QListWidget(MultipartTransformer)
        self.listWidget.setGeometry(QtCore.QRect(10, 90, 371, 261))
        self.listWidget.setStyleSheet(unicode("border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));"))
        self.listWidget.setSelectionRectVisible(True)
        self.listWidget.setObjectName(unicode("listWidget"))
        self.label = QtGui.QLabel(MultipartTransformer)
        self.label.setGeometry(QtCore.QRect(10, 0, 381, 41))
        font = QtGui.QFont()
        font.setFamily(unicode("Sans Serif"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName(unicode("label"))
        self.progressBar = QtGui.QProgressBar(MultipartTransformer)
        self.progressBar.setGeometry(QtCore.QRect(10, 370, 371, 23))
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(unicode("progressBar"))
        self.btnBrowse = QtGui.QPushButton(MultipartTransformer)
        self.btnBrowse.setGeometry(QtCore.QRect(10, 40, 191, 41))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(unicode(os.path.join( self.abspath, "icons/browser_button.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnBrowse.setIcon(icon)
        self.btnBrowse.setIconSize(QtCore.QSize(25, 25))
        self.btnBrowse.setObjectName(unicode("btnBrowse"))
        self.btnTOC = QtGui.QPushButton(MultipartTransformer)
        self.btnTOC.setGeometry(QtCore.QRect(210, 40, 51, 41))
        self.btnTOC.setText(unicode(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(unicode(os.path.join( self.abspath, "icons/layers_button.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnTOC.setIcon(icon1)
        self.btnTOC.setIconSize(QtCore.QSize(30, 30))
        self.btnTOC.setObjectName(unicode("btnTOC"))

        self.retranslateUi(MultipartTransformer)
        QtCore.QMetaObject.connectSlotsByName(MultipartTransformer)

    def retranslateUi(self, MultipartTransformer):
        MultipartTransformer.setWindowTitle(QtGui.QApplication.translate("MultipartTransformer", "InaSAFE Multipart Transformer", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MultipartTransformer", "Inspect polygon shapefiles for multi-part geometries.\n"
"Double click ones you want to convert to single-part geometries", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setToolTip(QtGui.QApplication.translate("MultipartTransformer", "browse to a shapefile directory", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setText(QtGui.QApplication.translate("MultipartTransformer", "   Browse for Shapefiles", None, QtGui.QApplication.UnicodeUTF8))
        self.btnTOC.setToolTip(QtGui.QApplication.translate("MultipartTransformer", "use toc layers", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
