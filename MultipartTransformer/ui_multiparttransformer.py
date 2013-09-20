# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_multiparttransformer.ui'
#
# Created: Thu Sep 19 17:34:06 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MultipartTransformer(object):
    def setupUi(self, MultipartTransformer):
        MultipartTransformer.setObjectName(_fromUtf8("MultipartTransformer"))
        MultipartTransformer.resize(394, 362)
        MultipartTransformer.setToolTip(_fromUtf8(""))
        self.btnBrowse = QtGui.QPushButton(MultipartTransformer)
        self.btnBrowse.setGeometry(QtCore.QRect(10, 50, 171, 31))
        self.btnBrowse.setIconSize(QtCore.QSize(25, 25))
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.listWidget = QtGui.QListWidget(MultipartTransformer)
        self.listWidget.setGeometry(QtCore.QRect(10, 90, 371, 261))
        self.listWidget.setStyleSheet(_fromUtf8("border-bottom-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));"))
        self.listWidget.setSelectionRectVisible(True)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.btnTOC = QtGui.QPushButton(MultipartTransformer)
        self.btnTOC.setGeometry(QtCore.QRect(190, 50, 41, 31))
        self.btnTOC.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("layers_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnTOC.setIcon(icon)
        self.btnTOC.setIconSize(QtCore.QSize(30, 30))
        self.btnTOC.setAutoRepeat(False)
        self.btnTOC.setObjectName(_fromUtf8("btnTOC"))
        self.label = QtGui.QLabel(MultipartTransformer)
        self.label.setGeometry(QtCore.QRect(10, 0, 381, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(MultipartTransformer)
        QtCore.QMetaObject.connectSlotsByName(MultipartTransformer)

    def retranslateUi(self, MultipartTransformer):
        MultipartTransformer.setWindowTitle(QtGui.QApplication.translate("MultipartTransformer", "InaSAFE Multipart Transformer", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setToolTip(QtGui.QApplication.translate("MultipartTransformer", "browse to a directory of shapefiles", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setText(QtGui.QApplication.translate("MultipartTransformer", "  Browse to Shapefiles", None, QtGui.QApplication.UnicodeUTF8))
        self.btnTOC.setToolTip(QtGui.QApplication.translate("MultipartTransformer", "use TOC layers", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MultipartTransformer", "Inspect polygon shapefiles for multi-part geometries.\n"
"Double click ones you want to convert to single-part geometries", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
