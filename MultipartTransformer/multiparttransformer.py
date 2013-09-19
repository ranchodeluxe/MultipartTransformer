# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from multiparttransformerdialog import MultipartTransformerDialog
import os, glob, re, sys 

#
#
#  Thread class for identifying multi-part geometries
#  *and* for converting multi-part geometries to single-part
#
#
class GeomProcessingThread( QThread ):
    #
    # SIGNALS
    #
    geom_m2s = pyqtSignal( int, str )
    finished = pyqtSignal()
    general_error = pyqtSignal( str )
    log_message = pyqtSignal( str )
    status_update = pyqtSignal( str )
    add_2_widget = pyqtSignal( object, str, object ) # icon, message, QgsVectorLayer

    def __init__( self, parent_thread, lyr, func_name, list_type ):
        QThread.__init__( self, parent_thread )
        self.lyr = lyr
        self.func_signature2run = func_name
        self.abspath = os.path.dirname( os.path.abspath( __file__ ) )
        self.list_type = list_type

    def run( self ):
        self.running = True

        try:
            work_method = getattr( self, self.func_signature2run )
        except AttributeError:
            reply = QMessageBox.critical( self.iface.mainWindow(), "Critical",
                    "The method %s was not found on the GeomProcessingThread class " % self.func_signature2run )
            self.finished.emit()
            return # break

        success = work_method()
        self.finished.emit()

    def inspectForMultipart( self ):

        try:
            #  determine if the layer has multipart features, then give it the right icon
            icon = QIcon( os.path.join( self.abspath, 'single_icon.png' ) ) # default icon
            feat = QgsFeature()
            while self.lyr.dataProvider().nextFeature(feat):

                #  TODO: we don't handle these, maybe we should mention bad things to user
                if feat.geometry() != None and not feat.geometry().isGeosEmpty():
                    if feat.geometry().isMultipart():
                        icon = QIcon( os.path.join( self.abspath, 'multi_icon.png' ) )
                        break

            display_text = str( self.lyr.name() )
            if self.list_type == 'browse':
                display_text = os.path.split( str(self.lyr.dataProvider().dataSourceUri()).split( "|" )[0] )[1] 
            self.add_2_widget.emit( icon, display_text, self.lyr )

        except Exception, e:
            self.general_error.emit( "[ INSPECT ERROR ]: %s" % str( e ) )
            return False


    def extractAsSingle( self, geom ):
        multi_geom = QgsGeometry()
        temp_geom = []
        if geom.type() == 0:
          if geom.isMultipart():
            multi_geom = geom.asMultiPoint()
            for i in multi_geom:
              temp_geom.append( QgsGeometry().fromPoint ( i ) )
          else:
            temp_geom.append( geom )
        elif geom.type() == 1:
          if geom.isMultipart():
            multi_geom = geom.asMultiPolyline()
            for i in multi_geom:
              temp_geom.append( QgsGeometry().fromPolyline( i ) )
          else:
            temp_geom.append( geom )
        elif geom.type() == 2:
          if geom.isMultipart():
            multi_geom = geom.asMultiPolygon()
            for i in multi_geom:
              temp_geom.append( QgsGeometry().fromPolygon( i ) )
          else:
            temp_geom.append( geom )
        return temp_geom


    def multipart2Singlepart( self ):
        try:
            #
            #  dataProviders and geometries have already been checked over before
            #  so we don't need to worry about NULL providers or geoms
            #
            vprovider = self.lyr.dataProvider()
            allAttrs = vprovider.attributeIndexes()
            vprovider.select( allAttrs )
            fields = vprovider.fields()
            geomType = QGis.WKBPolygon

            shp_path = os.path.split( str( self.lyr.dataProvider().dataSourceUri() ).split("|")[0] )[0]
            shp_name = os.path.splitext( os.path.split( str( self.lyr.dataProvider().dataSourceUri() ).split("|")[0] )[1] )[0] + "_w_singleparts.shp"
            writer = QgsVectorFileWriter(
                os.path.join( shp_path, shp_name ),
                "CP1250",
                fields,
                geomType,
                vprovider.crs()
            )

            if writer.hasError() != QgsVectorFileWriter.NoError:
                QMessageBox.critical(None, self.tr("Geom Processing"),
                        self.tr("There was an error creating the shapefile:\n\n\t%1").arg( str( writer.hasError() ) ),
                        QMessageBox.Ok | QMessageBox.Default,
                        QMessageBox.NoButton)
                raise Exception( "[ CREATE ERROR ]: writing shapefile %s" % os.path.join( shp_path, shp_name ) )

            inFeat = QgsFeature()
            outFeat = QgsFeature()
            inGeom = QgsGeometry()
            outGeom = QgsGeometry()
            nFeat = vprovider.featureCount()
            nElement = 0
            while vprovider.nextFeature( inFeat ):
              nElement += 1
              inGeom = inFeat.geometry()
              atMap = inFeat.attributeMap()
              featList = self.extractAsSingle( inGeom )
              outFeat.setAttributeMap( atMap )
              for i in featList:
                outFeat.setGeometry( i )
                writer.addFeature( outFeat )
            del writer

            # emit event/singal that everything was successful so we can 
            # add layer to the map
            self.geom_m2s.emit( 1, os.path.join( shp_path, shp_name ) ) # binary True/False

            return True
        except Exception, e:
            self.general_error.emit( "[ M2S ERROR ]: %s" % str( e ) )
            return False

    def stop( self ):
        self.running = False
        pass

    def cleanUp( self):
        pass




class MultipartTransformer:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # Save reference to map canvas
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/multiparttransformer"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale").toString()[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/multiparttransformer_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = MultipartTransformerDialog()

        # create a list to hold our selected feature ids
        self.selectList = []
        # current layer ref (set in handleLayerChange)
        self.cLayer = None
        # current layer dataProvider ref (set in handleLayerChange)
        self.provider = None
        # database connection
        self.conn = None
        self.crs = None


        #
        #
        #  worker thread pool
        #
        #
        self.geom_worker_threads = []
        self.worker_threads =  []

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/multiparttransformer/icon.png"),
            u"convert multi-part polygons with style!", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        #
        #
        #  EVENT/SIGNAL handlers
        #
        #

        #  layer change handler
        self.iface.currentLayerChanged.connect( self.handleLayerChange )
        #  browse button handler
        self.dlg.ui.btnBrowse.clicked.connect( self.dlg.openFileBrowserDialog )
        #  toc button handler
        self.dlg.ui.btnTOC.clicked.connect( self.loadTOCLayers )
        #  listWidget items
        self.dlg.ui.listWidget.itemDoubleClicked.connect( self.handleItemDblClick )
        self.dlg.ui.listWidget.itemSelectionChanged.connect( self.handleItemSelectionChanged )
        #  connect to browse shapefiles found 
        self.dlg.shapefiles_found.connect( self.addListWidgetItems )

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&InaSAFE Multipart Transformer", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&InaSAFE Multipart Transformer", self.action)
        self.iface.removeToolBarIcon(self.action)


    # run method that performs all the real work
    def run(self):
        self.dlg.show()
        self.dlg.guiSetup()

        # dialog
        result = self.dlg.exec_()
        if result == 0: # someone clicked the exit X
            self.cleanWorkers()
            self.cleanWorkers( wtype='geom_workers' )


    #
    #
    #  CUSTOM
    #
    #

    def cleanWorkers( self, wtype='normal' ):
        if wtype == 'normal':
            # make sure to clean up any hanging threads
            for wthread in self.worker_threads:
                thread_name = ' '.join( str( wthread ).split( ' ' )[1:] )
                if not wthread.isFinished():
                    self.logger( "thread <%s isRunning = %s" % ( thread_name, str( wthread.isRunning() ) ) )
                    self.logger( "terminating thread <%s" % ( str( thread_name ) ) )
                    wthread.terminate()
            self.worker_threads = []
        else:
            # make sure to clean up any hanging threads
            for wthread in self.geom_worker_threads:
                thread_name = ' '.join( str( wthread ).split( ' ' )[1:] )
                if not wthread.isFinished():
                    self.logger( "thread <%s isRunning = %s" % ( thread_name, str( wthread.isRunning() ) ) )
                    self.logger( "terminating thread <%s" % ( str( thread_name ) ) )
                    wthread.terminate()
            self.geom_worker_threads = []

    def addListWidgetItems( self, list_type, list_of_items ):
        ''' 
            set up each item in our list as a QWidgetListItem
        '''
        # make sure to clean worker threads
        # from previous runs before we create new ones
        self.cleanWorkers()
        # clear the listWidget box
        self.dlg.ui.listWidget.clear()

        for item in list_of_items:
            # either item is already a QgsVectorLayer or it is a shapefile path
            lyr = item
            if list_type == 'browse':
                #self.logger( "[ PATH ]: %s" % item )   
                # overwrite lyr with true QgsVectorLayer
                lyr = QgsVectorLayer( item,  os.path.splitext( os.path.split( item )[1] )[0] , "ogr" )
                #self.logger( "[ LAYER ]: %s" % str( lyr ))  

                if not lyr:
                    continue

                if not lyr.dataProvider():
                    continue

                # use non-short-circut OR here to filter out things we don't want 
                if ( lyr.type() != QgsMapLayer.VectorLayer or
                     str( lyr.dataProvider().name() ) != 'ogr' or
                     lyr.dataProvider().geometryType() not in [ QGis.WKBPolygon, QGis.WKBMultiPolygon ] ):
                    continue


            #   
            #   
            #  reading *big* shapefiles can bog down the fileDialog.
            #  Thread this section below and emit signal for each
            #  layer that finishes so layerinfo can be added to listWidget
            #   
            #   
            worker_thread = GeomProcessingThread(
                self.iface.mainWindow() ,
                lyr ,
                'inspectForMultipart' ,
                list_type
            )
            worker_thread.general_error.connect( self.logger )
            worker_thread.log_message.connect( self.logger )
            worker_thread.finished.connect( worker_thread.quit )
            worker_thread.add_2_widget.connect( self.dlg.add2ListWidget )
            worker_thread.start()
            self.worker_threads.append( worker_thread )

    def handleItemSelectionChanged( self ):
        pass

    def handleItemDblClick( self, widget_item ):
        self.logger( "[ ITEM CLICKED ]: %s" % str( widget_item.layer_instance) )
        convert = QMessageBox.question( self.iface.mainWindow(), self.dlg.tr("Process Geometry"),
                   self.dlg.tr( """Would you like to convert the layers:\n\n%1\n\nfrom a multi-part geometry to a single-part?""").arg( str(widget_item.layer_instance.name()) ),
                   QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton )

        if convert == QMessageBox.Yes:
            # cleanup other processing threads before doing this one
            self.cleanWorkers( wtype='geom_workers' )
            #   
            #   
            #  reading *big* shapefiles can bog down the fileDialog.
            #  Thread this section below and emit signal for each
            #  layer that finishes converting multi-part to single-part
            #   
            #   
            worker_thread = GeomProcessingThread(
                self.iface.mainWindow() ,
                widget_item.layer_instance ,
                'multipart2Singlepart' ,
                'toc'
            )
            worker_thread.general_error.connect( self.logger )
            worker_thread.log_message.connect( self.logger )
            worker_thread.finished.connect( worker_thread.quit )
            worker_thread.geom_m2s.connect( self.loadLayer2TOC )
            worker_thread.start()
            self.geom_worker_threads.append( worker_thread )
        else:
            return # do nada

    def loadLayer2TOC( self, int_bool, new_lyr_path ):

        if int_bool: # success
            QMessageBox.information( self.iface.mainWindow(),
                self.dlg.tr("Valid Geometry Conversion!"),
                self.dlg.tr("The conversion was successful. The new shapefile is located here path:\n\n%1\n\nAnd it will be added to this Qgis mapfile now!").arg( new_lyr_path ) )

            self.iface.addVectorLayer(
                new_lyr_path,
                os.path.splitext( os.path.split( str(new_lyr_path) )[1] )[0],
                "ogr"
            )

    def loadTOCLayers( self ):
        filtered = []
        for lyr in self.canvas.layers():
            # make sure to use non-short-circut OR to filter
            if ( lyr.type() != QgsMapLayer.VectorLayer or
                 str( lyr.dataProvider().name() ) != 'ogr' or
                 lyr.dataProvider().geometryType() not in [ QGis.WKBPolygon, QGis.WKBMultiPolygon ] ):
                continue
            filtered.append( lyr )

        self.dlg.ui.listWidget.clear()
        self.addListWidgetItems( 'toc', filtered )


    def handleLayerChange(self, layer):

        #
        #  update the current layer
        #
        self.cLayer = self.canvas.currentLayer()

    def logger(self, message ):
        QgsMessageLog.logMessage( str(message), 'InaSAFE' )


