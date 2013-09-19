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
        self.setFixedSize(394,362) # dimensions in ui_multiparttransformer.py
        self.fileDialog = QtGui.QFileDialog(self)
        self.ui.listWidget.clear() # default to empty
        self.abspath = os.path.dirname( os.path.abspath( __file__ ) ) 
        self.fileDialogState = None # default
     
    #   
    #   
    #  dialog interface
    #   
    #   
    
    #   
    #  TODO: for some reasone saving QFileDialog.saveState() using
    #  binary options does not work, this is a jenky workaround for now
    #  make it better later
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
        #self.dialogLogger( str( self.selected_filepath ) )
        if not self.selected_filepath or self.selected_filepath == '': 
            return

        # resave the state always cause we're nice
        self.fileDialogState = self.selected_filepath 
        self.setFileDialogState()
    
        #  get all shapefiles in this directory
        shps = glob.glob( os.path.join( self.selected_filepath, "*.shp" ) ) 
        if not shps or len(shps) == 0:
            # clear the listWidget box
            self.ui.listWidget.clear()
            return
     
        # return exec to controller
        #self.addListWidgetItems( shps, 'browse' )
        self.shapefiles_found.emit( 'browse', shps )


    def add2ListWidget( self, icon, text, layer_instance ):
        #self.dialogLogger( "[ DISPLAY TEXT ]: %s" % str( text ) )
        item = QtGui.QListWidgetItem( icon, text, parent=self.ui.listWidget )
        # attempt to store layer state on the object
        item.layer_instance = layer_instance


    def dialogLogger( self, message ):
        QgsMessageLog.logMessage( str( message ), "MULTIPOLY DIALOG" )
