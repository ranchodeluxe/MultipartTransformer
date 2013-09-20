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
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


#
#
#  Thread class for identifying multi-part geometries
#  *and* for converting multi-part geometries to single-part
#
#
class GeomProcessingThread( QThread ):

    #
    #
    # EVENTS/SIGNALS
    #
    #
    geom_m2s = pyqtSignal( int, str )
    geom_status_update = pyqtSignal( int )
    finished = pyqtSignal()
    update_widget_colors = pyqtSignal()
    general_error = pyqtSignal( str, int )
    log_message = pyqtSignal( str )
    status_update = pyqtSignal( int )
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
            reply = QMessageBox.critical( None, "Critical",
            "The method %s was not found on the GeomProcessingThread class " % 
            self.func_signature2run )
            self.finished.emit()
            return # break

        success = work_method()
        self.finished.emit()

    def inspectForMultipart( self ):

        try:
            all_attributes = self.lyr.dataProvider().attributeIndexes()
            self.lyr.dataProvider().select( all_attributes )
            #  determine if the layer has multipart features, then give it the right icon
            icon = QIcon( os.path.join( self.abspath, 'single_icon.png' ) ) # default icon
            feat = QgsFeature()
            while self.lyr.dataProvider().nextFeature(feat):

                #  TODO: we don't handle these, maybe we should mention bad things to user
                #if feat.geometry().isGeosEmpty() or not feat.geometry().isGeosValid():
                feat_geom = feat.geometry()
                if feat_geom.isMultipart():
                    icon = QIcon( os.path.join( self.abspath, 'multi_icon.png' ) )
                    break

            display_text = str( self.lyr.name() )
            if self.list_type == 'browse':
                display_text = os.path.split( 
                    str(self.lyr.dataProvider().dataSourceUri()).split( "|" )[0] 
                )[1] 

 
            self.status_update.emit( 1 )
            self.add_2_widget.emit( icon, display_text, self.lyr )
            return True

        except Exception, e:
            self.status_update.emit( 1 )
            self.general_error.emit( "[ INSPECT ERROR ]: %s" % str( e ), 2 )
            reply = QMessageBox.critical( 
                None, 
                "Critical", 
                "[ ERROR ] there was a cricitcal error during geometry inspection in the GeomProcessingThread"
            )
            return False


    def extract( self, geom ):
        multi_geom = QgsGeometry()
        temp_geom = []
        if geom.type() == 2:
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
            all_attributes = vprovider.attributeIndexes()
            vprovider.select( all_attributes )
            fields = vprovider.fields()
            geom_type = QGis.WKBPolygon

            shp_path = os.path.split( 
                str( self.lyr.dataProvider().dataSourceUri() ).split("|")[0] 
            )[0]
            shp_name = os.path.splitext( 
                os.path.split( 
                    str( self.lyr.dataProvider().dataSourceUri() ).split("|")[0] 
                )[1] 
            )[0] + "_w_singleparts.shp"
            writer = QgsVectorFileWriter(
                os.path.join( shp_path, shp_name ),
                "CP1250",
                fields,
                geom_type,
                vprovider.crs()
            )

            if writer.hasError() != QgsVectorFileWriter.NoError:
                QMessageBox.critical(None, self.tr("Geometry Processing"),
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

            self.geom_status_update.emit( 0 ) # just to make sure
            while vprovider.nextFeature( inFeat ):
                nElement += 1
                inGeom = inFeat.geometry()
                atMap = inFeat.attributeMap()
                featList = self.extract( inGeom )
                outFeat.setAttributeMap( atMap )
                for i in featList:
                    outFeat.setGeometry( i )
                    writer.addFeature( outFeat )

                # only update progress bar every so many features
                if (( nElement % 10 ) == 0 ) or nElement == nFeat: 
                    self.geom_status_update.emit( nElement )
            del writer

            #
            # emit event/singal that everything was successful so we can 
            # add layer to the map
            #
            self.geom_m2s.emit( 1, os.path.join( shp_path, shp_name ) ) # binary True/False

            return True
        except Exception, e:
            self.status_update.emit( nFeat ) # drive it to the end
            self.general_error.emit( "[ M2S ERROR ]: %s" % str( e ), 2 )
            reply = QMessageBox.critical( 
                None, 
                "Critical",
                "[ ERROR ] there was a cricitcal error during geometry transformation in the GeomProcessingThread" 
            )
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
        self.abspath = os.path.dirname( os.path.abspath( __file__ ) )


        #
        #
        #  worker thread pools
        #
        #
        self.geom_worker_threads = []
        self.worker_threads =  []

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(QPixmap(_fromUtf8(os.path.join( self.abspath, "icon2.png")))),
            u"Multipart Transform: convert multi-part polygons with style!", self.iface.mainWindow())
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
        self.iface.addPluginToMenu(u"&Multipart Transformer", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Multipart Transformer", self.action)
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

    def isTargetLayerType( self, lyr ):
        if ( lyr.type() != QgsMapLayer.VectorLayer or
             str( lyr.dataProvider().name() ) != 'ogr' or
             lyr.dataProvider().geometryType() not in 
             ( QGis.WKBPolygon, QGis.WKBMultiPolygon, QGis.WKBMultiPolygon25D, QGis.WKBPolygon25D ) ):
             return False
        return True

    def addListWidgetItems( self, list_type, list_of_items ):
        ''' 
            set up each item in our list as a QWidgetListItem
        '''
        filtered = []
        if list_type == 'browse':
            for item in list_of_items:
                try:
                    lyr = QgsVectorLayer( item,  os.path.splitext( os.path.split( item )[1] )[0] , "ogr" )
                except Exception, e:
                    self.logger( "[ ERROR ]: QgsVectorLayer cannot be created > %s" % str( e ), level=2 )
                    continue

                if not lyr:
                    continue

                if not lyr.dataProvider():
                    continue

                if not self.isTargetLayerType( lyr ):
                    continue

                filtered.append( lyr )

        elif list_type == 'toc':
            filtered = list_of_items # already filtered

        #
        # make sure to terminate worker threads
        # from previous runs before we create new ones
        #
        self.cleanWorkers()

        self.dlg.ui.listWidget.clear()
        self.dlg.number_to_process = len( filtered )
        self.dlg.number_processed = 0
        self.dlg.ui.progressBar.setMaximum( self.dlg.number_to_process )
        #self.logger( "[ TO PROCESS ]: %i" % self.dlg.number_to_process )

        for lyr in filtered:

            #   
            #   
            #  reading *big* shapefiles can bog down the fileDialog.
            #  Read each layer's features in a QThread
            #  and emit signal on completion so
            #  layerinfo can be added to listWidget
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
            worker_thread.status_update.connect( self.dlg.handleProgressUpdate )
            worker_thread.start()
            self.worker_threads.append( worker_thread )

    def unbindWidgetItemClicks( self ):
        try:
            self.dlg.ui.listWidget.itemDoubleClicked.disconnect( self.handleItemDblClick )
        except TypeError, te: # it's not connected
            pass

    def updateWidgetItems( self ):
        for item in self.dlg.iterWidgetItems():
            item.setBackground( QBrush( Qt.white ) )
            item.setForeground( QBrush( Qt.black ) )

    def handleItemSelectionChanged( self ):
        pass

    def hasRunningThreads( self ):
        '''
        if the GUI currently has threads executing
        then return True else False
        '''
        for wthread in self.worker_threads:
            if wthread.isRunning():
                return True

        for wthread in self.geom_worker_threads:
            if wthread.isRunning():
                return True
        return False

    def handleItemDblClick( self, widget_item ):
        if self.hasRunningThreads():
            QMessageBox.information( self.dlg, self.dlg.tr("Stop Doing That!"),
                self.dlg.tr( "Looks like there's already work in progress...give it a second dude" ) )
            return # do nada
        

        convert = QMessageBox.question( self.dlg, self.dlg.tr("Process Geometry"),
                   self.dlg.tr("Would you like to convert the layers:\n\n%1\n\nfrom a multi-part geometry to a single-part?").arg( str(widget_item.layer_instance.name()) ),
                   QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton )

        if convert == QMessageBox.Yes:
            # make sure to terminate other threads before running
            self.cleanWorkers( wtype='geom_workers' )

            # update the dialog with total number of items 
            self.dlg.number_to_process = widget_item.layer_instance.dataProvider().featureCount()
            self.dlg.number_processed = 0
            self.dlg.ui.progressBar.setMaximum( self.dlg.number_to_process )
            #self.logger( "[ TO PROCESS ]: %i" % self.dlg.number_to_process )


            #   
            #   
            #  reading *big* shapefiles can bog down the fileDialog.
            #  Thread reading through a layer's features 
            #  and emit a signal when geom processing is done 
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
            worker_thread.geom_status_update.connect( self.dlg.handleProgressUpdate )
            worker_thread.start()
            self.geom_worker_threads.append( worker_thread )
        else:
            return # do nada

    def loadLayer2TOC( self, int_bool, new_lyr_path ):

        if int_bool: # success
            self.dlg.ui.progressBar.reset()

            QMessageBox.information( self.dlg,
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
            if not self.isTargetLayerType( lyr ):
                continue
            filtered.append( lyr )

        self.dlg.ui.listWidget.clear()
        if len( filtered ) == 0:
            QMessageBox.information( self.dlg,
                self.dlg.tr("No Multi-part Polygons"),
                self.dlg.tr("There were no multi-part polygons found in the TOC") )
        self.addListWidgetItems( 'toc', filtered )


    def handleLayerChange(self, layer):

        #
        #  update the current layer
        #
        self.cLayer = self.canvas.currentLayer()

    def logger(self, message, level=0 ):
        QgsMessageLog.logMessage( str(message), 'MTrans', level )

