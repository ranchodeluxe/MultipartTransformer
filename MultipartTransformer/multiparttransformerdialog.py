# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from qgis.core import QgsMessageLog 
from ui_multiparttransformer import Ui_MultipartTransformer
import sys, os, glob, re

class MultipartTransformerDialog(QtGui.QDialog):

    #   
    #   
    #  EVENTS/SIGNALS
    #   
    #   
    shapefiles_found = QtCore.pyqtSignal( str, list ) # for emitting shapefiles found in browse

    def __init__(self):
        QtGui.QDialog.__init__( self, None, QtCore.Qt.WindowStaysOnTopHint )
        # Set up the user interface from Designer.
        self.ui = Ui_MultipartTransformer()
        self.ui.setupUi(self)
        self.setFixedSize(394,434) # dimensions in ui_multiparttransformer.py
        self.fileDialog = QtGui.QFileDialog(self)
        self.ui.listWidget.clear() # default to empty
        self.abspath = os.path.dirname( os.path.abspath( __file__ ) ) 
        self.fileDialogState = None # default
        self.items_to_process = None 
     
    #   
    #  TODO: for unknown reasons saving QFileDialog.saveState() using
    #  binary options does not work, this is a jenky workaround 
    #  where we save state to the plugin directory in a textfile. 
    #   
    def getFileDialogState( self ):
        try:
            with open( os.path.join( self.abspath, 'dialog_state.txt' ),'r' ) as f:
                self.fileDialogState = f.readline()
        except IOError, ie: 
            pass
        except Exception, e:
            self.dialogLogger( "[ READ ERROR ]: %s" % str( e ) ) 

    def setFileDialogState( self ):
        try:
            with open( os.path.join( self.abspath, 'dialog_state.txt' ),'w' ) as f:
                if self.fileDialogState: f.write( self.fileDialogState )
        except Exception, e:
            self.dialogLogger( "[ WRITE ERROR ]: %s" % str( e ) ) 

    def guiSetup( self ):
        self.clearDialogs()

    def clearDialogs( self ):
        self.ui.listWidget.clear()

    def setListWidget( self, text ):
        self.ui.listWidget.setText(text)

    def openFileBrowserDialog( self ):
        self.getFileDialogState()
        self.selected_filepath  = str( self.fileDialog.getExistingDirectory(self, "Select Directory", 
                                    ( '' if not self.fileDialogState else self.fileDialogState )) )

        if not self.selected_filepath or self.selected_filepath == '': 
            return

        # always resave the state cause we're nice
        self.fileDialogState = self.selected_filepath 
        self.setFileDialogState()
    
        #  get all shapefiles in this directory
        shps = glob.glob( os.path.join( self.selected_filepath, "*.shp" ) ) 
        if len(shps) == 0:
            self.ui.listWidget.clear()
            QMessageBox.information( self.dlg,
                self.dlg.tr("No Multi-part Polygons"),
                self.dlg.tr("There were no multi-part polygon shapefilesfound in the selected directory") )
            return
     
        # return exec to controller
        self.shapefiles_found.emit( 'browse', shps )

    def add2ListWidget( self, icon, text, layer_instance ):
        item = QtGui.QListWidgetItem( icon, text )
        # set default brush strokes
        item.setBackground( QtGui.QBrush(QtCore.Qt.white) )
        item.setForeground( QtGui.QBrush(QtCore.Qt.black) )
        self.ui.listWidget.addItem( item )
        #
        # attempt to store layer state 
        # on the listWidgetItem for later use 
        # on click hnadlers
        #
        item.layer_instance = layer_instance

    def iterWidgetItems( self ):
        for i in range( self.ui.listWidget.count() ):
            yield self.ui.listWidget.item( i )

    def handleProgressUpdate( self, status):
        self.number_processed += status
        #self.dialogLogger( "[ PROCESSED ]: %i" % self.number_processed )
        self.ui.progressBar.setValue( self.number_processed )
        if self.number_processed == self.number_to_process:
            #self.dialogLogger( "[ FINAL ] %i" % self.number_processed )
            self.ui.progressBar.reset()

    def dialogLogger( self, message ):
        QgsMessageLog.logMessage( str( message ), "MTransGUI" )


