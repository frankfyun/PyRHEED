from my_widgets import LabelSlider
from process import Image, FitFunctions, FitBroadening
from PyQt5 import QtCore, QtWidgets, QtGui, QtChart
import configparser
import generate_report
import glob
import manual_fit
import numpy as np
import os
import profile_chart

class Window(QtCore.QObject):

    #Public Signals
    STATUS_REQUESTED = QtCore.pyqtSignal()
    PROGRESS_ADVANCE = QtCore.pyqtSignal(int,int,int)
    PROGRESS_END = QtCore.pyqtSignal()
    CONNECT_TO_CANVAS = QtCore.pyqtSignal()
    DRAW_LINE_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,bool)
    DRAW_RECT_REQUESTED = QtCore.pyqtSignal(QtCore.QPointF,QtCore.QPointF,float,bool)
    COLOR = ['magenta','cyan','darkCyan','darkMagenta','darkRed','darkBlue','darkGray','green','darkGreen','darkYellow','yellow','black']
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)
    STOP_WORKER = QtCore.pyqtSignal()

    def __init__(self):
        super(Window,self).__init__()
        self.analysisRegion = [0,0,0,0,0]
        self.config = configparser.ConfigParser()
        self.config.read('./configuration.ini')
        self.image_worker = Image()
        self.fit_worker = Fit()

    def refresh(self,config):
            self.config = config
            try:
                self.chart.refresh(config)
                self.costChart.refresh(config)
            except:
                pass

    def main(self,path):
        self.startIndex = "0"
        self.endIndex = "3"
        self.range = "5"
        self.FTol = '1e-6'
        self.XTol = '1e-4'
        self.GTol = '1e-6'
        self.numberOfSteps = "20"
        self.defaultFileName = "Broadening"
        self.file_has_been_created = False
        self.path = os.path.dirname(path)
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.Dialog = QtWidgets.QWidget()
        self.Grid = QtWidgets.QGridLayout(self.Dialog)
        self.LeftFrame = QtWidgets.QFrame()
        self.RightFrame = QtWidgets.QFrame()
        self.LeftGrid = QtWidgets.QGridLayout(self.LeftFrame)
        self.RightGrid = QtWidgets.QGridLayout(self.RightFrame)
        self.chooseSource = QtWidgets.QGroupBox("Source Directory")
        self.chooseSource.setStyleSheet('QGroupBox::title {color:blue;}')
        self.sourceGrid = QtWidgets.QGridLayout(self.chooseSource)
        self.sourceGrid.setAlignment(QtCore.Qt.AlignTop)
        self.chooseSourceLabel = QtWidgets.QLabel("The source directory is:\n"+self.currentSource)
        self.chooseSourceButton = QtWidgets.QPushButton("Browse...")
        self.chooseSourceButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseSourceButton.clicked.connect(self.choose_source)
        self.sourceGrid.addWidget(self.chooseSourceLabel,0,0)
        self.sourceGrid.addWidget(self.chooseSourceButton,0,1)
        self.chooseDestination = QtWidgets.QGroupBox("Save Destination")
        self.chooseDestination.setStyleSheet('QGroupBox::title {color:blue;}')
        self.destinationGrid = QtWidgets.QGridLayout(self.chooseDestination)
        self.chooseDestinationLabel = QtWidgets.QLabel("The save destination is:\n"+self.currentSource)
        self.destinationNameLabel = QtWidgets.QLabel("The file name is:")
        self.destinationNameEdit = QtWidgets.QLineEdit(self.defaultFileName)
        self.fileTypeLabel = QtWidgets.QLabel("Type of file is:")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItem(".txt",".txt")
        self.fileType.addItem(".xlsx",".xlsx")
        self.chooseDestinationButton = QtWidgets.QPushButton("Browse...")
        self.chooseDestinationButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.chooseDestinationButton.clicked.connect(self.choose_destination)
        self.saveResultLabel = QtWidgets.QLabel("Save Results?")
        self.saveResult = QtWidgets.QCheckBox()
        self.saveResult.setChecked(False)
        self.destinationGrid.addWidget(self.chooseDestinationLabel,0,0)
        self.destinationGrid.addWidget(self.chooseDestinationButton,0,1)
        self.destinationGrid.addWidget(self.destinationNameLabel,1,0)
        self.destinationGrid.addWidget(self.destinationNameEdit,1,1)
        self.destinationGrid.addWidget(self.fileTypeLabel,2,0)
        self.destinationGrid.addWidget(self.fileType,2,1)
        self.destinationGrid.addWidget(self.saveResultLabel,3,0)
        self.destinationGrid.addWidget(self.saveResult,3,1)
        self.destinationGrid.setAlignment(self.chooseDestinationButton,QtCore.Qt.AlignRight)
        self.parametersBox = QtWidgets.QGroupBox("Choose Image")
        self.parametersBox.setStyleSheet('QGroupBox::title {color:blue;}')
        self.parametersGrid = QtWidgets.QGridLayout(self.parametersBox)
        self.startImageIndexLabel = QtWidgets.QLabel("Start Image Index")
        self.startImageIndexEdit = QtWidgets.QLineEdit(self.startIndex)
        self.endImageIndexLabel = QtWidgets.QLabel("End Image Index")
        self.endImageIndexEdit = QtWidgets.QLineEdit(self.endIndex)
        self.rangeLabel = QtWidgets.QLabel("Range (\u212B\u207B\u00B9)")
        self.rangeEdit = QtWidgets.QLineEdit(self.range)
        self.parametersGrid.addWidget(self.startImageIndexLabel,0,0)
        self.parametersGrid.addWidget(self.startImageIndexEdit,0,1)
        self.parametersGrid.addWidget(self.endImageIndexLabel,1,0)
        self.parametersGrid.addWidget(self.endImageIndexEdit,1,1)
        self.parametersGrid.addWidget(self.rangeLabel,2,0)
        self.parametersGrid.addWidget(self.rangeEdit,2,1)

        self.appearance = QtWidgets.QGroupBox("Appearance")
        self.appearance.setMaximumHeight(100)
        self.appearance.setStyleSheet('QGroupBox::title {color:blue;}')
        self.appearanceGrid = QtWidgets.QGridLayout(self.appearance)
        self.fontListLabel = QtWidgets.QLabel("Change Font")
        self.fontList = QtWidgets.QFontComboBox()
        self.fontList.setCurrentFont(QtGui.QFont("Arial"))
        self.fontList.currentFontChanged.connect(self.refresh_font_name)
        self.fontSizeLabel = QtWidgets.QLabel("Adjust Font Size ({})".format(12))
        self.fontSizeLabel.setFixedWidth(160)
        self.fontSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(1)
        self.fontSizeSlider.setMaximum(100)
        self.fontSizeSlider.setValue(12)
        self.fontSizeSlider.valueChanged.connect(self.refresh_font_size)
        self.appearanceGrid.addWidget(self.fontListLabel,0,0)
        self.appearanceGrid.addWidget(self.fontList,0,1)
        self.appearanceGrid.addWidget(self.fontSizeLabel,1,0)
        self.appearanceGrid.addWidget(self.fontSizeSlider,1,1)
        self.fitOptions = QtWidgets.QGroupBox("Fit Options")
        self.fitOptions.setStyleSheet('QGroupBox::title {color:blue;}')
        self.fitOptionsGrid = QtWidgets.QGridLayout(self.fitOptions)
        self.numberOfPeaksLabel = QtWidgets.QLabel("Number of Gaussian Peaks")
        self.numberOfPeaksLabel.setFixedWidth(160)
        self.numberOfPeaksCombo = QtWidgets.QComboBox()
        self.numberOfPeaksCombo.addItem('1','1')
        self.numberOfPeaksCombo.addItem('3','3')
        self.numberOfPeaksCombo.addItem('5','5')
        self.numberOfPeaksCombo.addItem('7','7')
        self.numberOfPeaksCombo.addItem('9','9')
        self.numberOfPeaksCombo.addItem('11','11')
        self.numberOfPeaksCombo.currentIndexChanged.connect(self.number_of_peaks_changed)
        self.includeBG = QtWidgets.QLabel("Include Gaussian Background?")
        self.BGCheck = QtWidgets.QCheckBox()
        self.BGCheck.setChecked(False)
        self.BGCheck.stateChanged.connect(self.background_check_changed)
        self.FTolLabel = QtWidgets.QLabel("Cost Function Tolerance")
        self.FTolEdit = QtWidgets.QLineEdit(self.FTol)
        self.XTolLabel = QtWidgets.QLabel("Variable Tolerance")
        self.XTolEdit = QtWidgets.QLineEdit(self.XTol)
        self.GTolLabel = QtWidgets.QLabel("Gradient Tolerance")
        self.GTolEdit = QtWidgets.QLineEdit(self.GTol)
        self.methodLabel = QtWidgets.QLabel("Algorithm")
        self.methodLabel.setFixedWidth(160)
        self.method = QtWidgets.QComboBox()
        self.method.addItem('Trust Region Reflective','trf')
        self.method.addItem('Dogleg','dogbox')
        self.lossLabel = QtWidgets.QLabel("Loss Function")
        self.lossLabel.setFixedWidth(160)
        self.loss = QtWidgets.QComboBox()
        self.loss.addItem('Linear','linear')
        self.loss.addItem('Soft l1','soft_l1')
        self.loss.addItem('Huber','huber')
        self.loss.addItem('Cauchy','cauchy')
        self.loss.addItem('Arctan','arctan')
        self.ManualFitButton = QtWidgets.QPushButton("Manual Fit")
        self.ManualFitButton.clicked.connect(self.show_manual_fit)
        self.offset = LabelSlider(0,100,0,100,'Offset')
        self.fitOptionsGrid.addWidget(self.numberOfPeaksLabel,0,0)
        self.fitOptionsGrid.addWidget(self.numberOfPeaksCombo,0,1)
        self.fitOptionsGrid.addWidget(self.methodLabel,1,0)
        self.fitOptionsGrid.addWidget(self.method,1,1)
        self.fitOptionsGrid.addWidget(self.lossLabel,2,0)
        self.fitOptionsGrid.addWidget(self.loss,2,1)
        self.fitOptionsGrid.addWidget(self.includeBG,3,0)
        self.fitOptionsGrid.addWidget(self.BGCheck,3,1)
        self.fitOptionsGrid.addWidget(self.offset,4,0,1,2)
        self.fitOptionsGrid.addWidget(self.FTolLabel,5,0)
        self.fitOptionsGrid.addWidget(self.FTolEdit,5,1)
        self.fitOptionsGrid.addWidget(self.XTolLabel,6,0)
        self.fitOptionsGrid.addWidget(self.XTolEdit,6,1)
        self.fitOptionsGrid.addWidget(self.GTolLabel,7,0)
        self.fitOptionsGrid.addWidget(self.GTolEdit,7,1)
        self.fitOptionsGrid.addWidget(self.ManualFitButton,8,0,1,2)
        self.statusBar = QtWidgets.QGroupBox("Log")
        self.statusBar.setStyleSheet('QGroupBox::title {color:blue;}')
        self.statusGrid = QtWidgets.QGridLayout(self.statusBar)
        self.statusBar.setFixedHeight(150)
        self.statusBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setFixedHeight(12)
        self.progressBar.setFixedWidth(800)
        self.progressBar.setVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBarSizePolicy = self.progressBar.sizePolicy()
        self.progressBarSizePolicy.setRetainSizeWhenHidden(True)
        self.progressBar.setSizePolicy(self.progressBarSizePolicy)
        self.PROGRESS_ADVANCE.connect(self.progress)
        self.PROGRESS_END.connect(self.progress_reset)
        self.logBox = QtWidgets.QTextEdit(QtCore.QTime.currentTime().toString("hh:mm:ss")+\
                                    "\u00A0\u00A0\u00A0\u00A0Initialized!")
        self.logBox.ensureCursorVisible()
        self.logBox.setAlignment(QtCore.Qt.AlignTop)
        self.logBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.logBoxScroll = QtWidgets.QScrollArea()
        self.logBoxScroll.setWidget(self.logBox)
        self.logBoxScroll.setWidgetResizable(True)
        self.logBoxScroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.statusGrid.addWidget(self.logBoxScroll,0,0)
        self.statusGrid.setAlignment(self.progressBar,QtCore.Qt.AlignRight)
        self.ButtonBox = QtWidgets.QDialogButtonBox()
        self.ButtonBox.addButton("Start",QtWidgets.QDialogButtonBox.ActionRole)
        self.ButtonBox.addButton("Stop",QtWidgets.QDialogButtonBox.ActionRole)
        self.ButtonBox.addButton("Reset",QtWidgets.QDialogButtonBox.ResetRole)
        self.ButtonBox.addButton("Quit",QtWidgets.QDialogButtonBox.DestructiveRole)
        self.ButtonBox.setCenterButtons(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].clicked.\
            connect(self.start)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].clicked. \
            connect(self.stop)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].clicked.\
            connect(self.reset)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].clicked.\
            connect(self.reject)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.GenerateReportButton = QtWidgets.QPushButton("Generate Report")
        self.GenerateReportButton.setEnabled(False)
        self.GenerateReportButton.clicked.connect(self.generate_broadening_report)
        self.chartTitle = QtWidgets.QLabel('Profile')
        self.chart = profile_chart.ProfileChart(self.config)
        self.chart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.FONTS_CHANGED.connect(self.chart.adjust_fonts)
        self.costChartTitle = QtWidgets.QLabel('Cost Function')
        self.costChart = profile_chart.ProfileChart(self.config)
        self.costChart.set_fonts(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.FONTS_CHANGED.connect(self.costChart.adjust_fonts)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('C'))
        self.table.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('C_Low'))
        self.table.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem('C_High'))
        self.table.setHorizontalHeaderItem(3,QtWidgets.QTableWidgetItem('H'))
        self.table.setHorizontalHeaderItem(4,QtWidgets.QTableWidgetItem('H_Low'))
        self.table.setHorizontalHeaderItem(5,QtWidgets.QTableWidgetItem('H_High'))
        self.table.setHorizontalHeaderItem(6,QtWidgets.QTableWidgetItem('W'))
        self.table.setHorizontalHeaderItem(7,QtWidgets.QTableWidgetItem('W_Low'))
        self.table.setHorizontalHeaderItem(8,QtWidgets.QTableWidgetItem('W_High'))
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setBackgroundRole(QtGui.QPalette.Highlight)
        self.table.setMinimumHeight(200)
        self.table.setRowCount(int(self.numberOfPeaksCombo.currentData()))
        self.table_auto_initialize()
        for i in range(1,int(self.numberOfPeaksCombo.currentData())+1):
            item = QtWidgets.QTableWidgetItem('Peak {}'.format(i))
            item.setForeground(QtGui.QColor(self.COLOR[i-1]))
            self.table.setVerticalHeaderItem(i-1,item)
        self.LeftGrid.addWidget(self.chooseSource,0,0)
        self.LeftGrid.addWidget(self.chooseDestination,1,0)
        self.LeftGrid.addWidget(self.parametersBox,2,0)
        self.LeftGrid.addWidget(self.appearance,3,0)
        self.LeftGrid.addWidget(self.fitOptions,4,0)
        self.LeftGrid.addWidget(self.ButtonBox,5,0)
        self.LeftGrid.addWidget(self.GenerateReportButton,6,0)
        self.RightGrid.addWidget(self.chartTitle,0,0)
        self.RightGrid.addWidget(self.costChartTitle,0,1)
        self.RightGrid.addWidget(self.chart,1,0)
        self.RightGrid.addWidget(self.costChart,1,1)
        self.RightGrid.addWidget(self.table,2,0,1,2)
        self.RightGrid.addWidget(self.statusBar,3,0,1,2)
        self.RightGrid.addWidget(self.progressBar,4,0,1,2)
        self.Grid.addWidget(self.LeftFrame,0,0)
        self.Grid.addWidget(self.RightFrame,0,1)
        self.Dialog.setWindowTitle("Broadening Analysis")
        self.Dialog.setMinimumHeight(800)
        self.Dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.Dialog.showNormal()
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry(self.Dialog)
        center = desktopRect.center()
        self.Dialog.move(center.x()-self.Dialog.width()*0.5,center.y()-self.Dialog.height()*0.5)

    def choose_source(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose source directory",self.currentSource,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentSource = path
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)

    def choose_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"choose save destination",self.currentDestination,QtWidgets.QFileDialog.ShowDirsOnly)
        self.currentDestination = path
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)

    def refresh_font_size(self):
        self.fontSizeLabel.setText("Adjust Font Size ({})".format(self.fontSizeSlider.value()))
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def refresh_font_name(self):
        self.FONTS_CHANGED.emit(self.fontList.currentFont().family(),self.fontSizeSlider.value())

    def prepare(self):
        if self.table_is_ready():
            self.STATUS_REQUESTED.emit()
            self.windowDefault = dict(self.config['windowDefault'].items())
            self.logBox.clear()
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                    self.status["endY"] == "" \
                    or self.status["width"] =="": pass
            else:
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")
            path = os.path.join(self.currentSource,'*.nef')
            autoWB = self.status["autoWB"]
            brightness = self.status["brightness"]
            blackLevel = self.status["blackLevel"]
            VS = int(self.windowDefault["vs"])
            HS = int(self.windowDefault["hs"])
            image_crop = [1200+VS,2650+VS,500+HS,3100+HS]
            scale_factor = self.status["sensitivity"]/np.sqrt(self.status["energy"])
            startIndex = int(self.startImageIndexEdit.text())
            endIndex = int(self.endImageIndexEdit.text())
            saveFileName = self.destinationNameEdit.text()
            fileType = self.fileType.currentData()
            analysisRange = float(self.rangeEdit.text())
            self.initialparameters = self.initial_parameters()
            self.reportPath = self.currentDestination+"/"+saveFileName+fileType
            if self.saveResult.checkState() == 2:
                self.output = open(self.reportPath,mode='w')
                self.output.write(QtCore.QDateTime.currentDateTime().toString("MMMM d, yyyy  hh:mm:ss ap")+"\n")
                self.output.write("The source directory is: "+self.currentSource+"\n")
            index = []
            for index_i in range(1,int(self.numberOfPeaksCombo.currentData())+1):
                index.append(str(index_i))
            if self.BGCheck.checkState():
                index.append('BG')
            information = self.status
            information['AnalysisRange'] = analysisRange
            information['NumberOfPeaks'] = int(self.numberOfPeaksCombo.currentData())
            information['BGCheck'] = self.BGCheck.checkState()
            information['FTol'] = float(self.FTolEdit.text())
            information['XTol'] = float(self.XTolEdit.text())
            information['GTol'] = float(self.GTolEdit.text())
            information['method'] = self.method.currentData()
            information['loss_function'] = self.loss.currentData()
            if self.saveResult.checkState() == 2:
                self.output.write(str(information))
                self.output.write('\n\n')
                results_head =str('Phi').ljust(12)+'\t'+str('Kperp').ljust(12)+'\t'+'\t'.join(str(label+i).ljust(12)+'\t'+str(label+i+'_error').ljust(12) for label in ['H','C','W'] for i in index )+'\t'+str('Offset').ljust(12)+'\t'+str('Offset_error').ljust(12)+'\n'
                self.output.write(results_head)
            if self.status["startX"] == "" or self.status["startY"] == "" or self.status["endX"] == "" or \
                    self.status["endY"] == ""\
                or self.status["width"] =="":
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0ERROR: Please choose the region!")
                self.raise_error("Please choose the region!")
                return False
            elif self.status["choosedX"] == "" or self.status["choosedY"] == "":
                self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0ERROR: Please choose the origin!")
                self.raise_error("Please choose the origin!")
                return False
            else:
                self.CONNECT_TO_CANVAS.emit()
                start = QtCore.QPointF()
                end = QtCore.QPointF()
                origin = QtCore.QPointF()
                origin.setX(self.status["choosedX"])
                origin.setY(self.status["choosedY"])
                start.setX(self.status["startX"])
                start.setY(self.status["startY"])
                end.setX(self.status["endX"])
                end.setY(self.status["endY"])
                width = self.status["width"]*scale_factor
                self.broadening_worker = FitBroadening(path,self.initialparameters,startIndex,endIndex,origin,start,end,width,analysisRange,scale_factor,autoWB,brightness,blackLevel,image_crop,\
                                                       int(self.numberOfPeaksCombo.currentData()),self.BGCheck.checkState(),self.saveResult.checkState(),self.guess,(self.bound_low,self.bound_high),float(self.FTolEdit.text()),\
                                                        float(self.XTolEdit.text()),float(self.GTolEdit.text()),self.method.currentData(),self.loss.currentData())
                self.broadening_worker.UPDATE_RESULTS.connect(self.update_results)
                self.broadening_worker.UPDATE_LOG.connect(self.update_log)
                self.broadening_worker.WRITE_OUTPUT.connect(self.write_results)
                self.broadening_worker.CLOSE_OUTPUT.connect(self.close_results)
                self.broadening_worker.ATTENTION.connect(self.raise_attention)
                self.broadening_worker.PROGRESS_ADVANCE.connect(self.progress)
                self.broadening_worker.PROGRESS_END.connect(self.progress_reset)
                self.broadening_worker.FINISHED.connect(self.process_finished)
                self.broadening_worker.DRAW_LINE_REQUESTED.connect(self.DRAW_LINE_REQUESTED)
                self.broadening_worker.DRAW_RECT_REQUESTED.connect(self.DRAW_RECT_REQUESTED)
                self.broadening_worker.ADD_COST_FUNCTION.connect(self.plot_cost_function)
                self.broadening_worker.ADD_PLOT.connect(self.plot_results)

                self.thread = QtCore.QThread()
                self.broadening_worker.moveToThread(self.thread)
                self.broadening_worker.FINISHED.connect(self.thread.quit)
                self.thread.started.connect(self.broadening_worker.run)
                self.STOP_WORKER.connect(self.broadening_worker.stop)
                return True
        else:
            return False

    def start(self):
        self.worker_is_ready = self.prepare()
        if self.worker_is_ready:
            self.thread.start()
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(True)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(False)
            self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(False)
            self.GenerateReportButton.setEnabled(False)
            self.fitOptions.setEnabled(False)

    def stop(self):
        self.STOP_WORKER.emit()
        if self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.fitOptions.setEnabled(True)
        self.file_has_been_created = False

    def write_results(self,results):
        self.output.write(results)

    def close_results(self):
        self.output.close()
        self.GenerateReportButton.setEnabled(True)

    def process_finished(self):
        self.progress_reset()
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[0].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[1].setEnabled(False)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[2].setEnabled(True)
        self.ButtonBox.findChildren(QtWidgets.QPushButton)[3].setEnabled(True)
        self.fitOptions.setEnabled(True)

    def update_log(self,message):
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0" + message)

    def reject(self):
        self.Dialog.close()

    def initial_parameters(self):
        para = []
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                para.append(float(self.table.item(i,j).text()))
        para.append(float(self.offset.get_value()))
        return para

    def update_results(self,results):
        index=0
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                value = np.round(results[index],2)
                item = QtWidgets.QTableWidgetItem('{}'.format(value))
                variation = [0.5,0.5,0.5,0.5,0.5,0.5]
                #Height
                if j == 3:
                    item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[0],2))))
                    item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[1],2)))
                #Center
                elif j == 0:
                    item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0,np.round(value-variation[2],2))))
                    item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[3],2)))
                #Width
                else:
                    item2 = QtWidgets.QTableWidgetItem('{}'.format(max(0.1,np.round(value-variation[4],2))))
                    item3 = QtWidgets.QTableWidgetItem('{}'.format(np.round(value+variation[5],2)))
                item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item2.setTextAlignment(QtCore.Qt.AlignCenter)
                item3.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(i,j,item)
                self.table.setItem(i,j+1,item2)
                self.table.setItem(i,j+2,item3)
                index+=1
        self.offset.set_value(results[-1])

    def plot_cost_function(self,iteration,cost,text):
        self.costChart.add_chart(iteration,cost,text)

    def plot_results(self,x0,y0,Kperp,nimg):
        if not self.file_has_been_created:
            if self.BGCheck.isChecked() and self.saveResult.isChecked():
                self.map_without_background = np.array([0,0,0,0])
                self.save_path_without_background = self.currentDestination+"/2D_map_without_background.txt"
                self.file_has_been_created = True
        self.chart.add_chart(x0,y0)
        total = np.full(len(x0),float(self.offset.get_value()))
        total_min = 100
        for i in range(self.table.rowCount()):
            center = float(self.table.item(i,0).text())
            height = float(self.table.item(i,3).text())
            width = float(self.table.item(i,6).text())
            offset = float(self.offset.get_value())
            fit = self.fit_worker.gaussian(x0,height,center,width,offset)
            fit0 = self.fit_worker.gaussian(x0,height,center,width,0)
            total = np.add(total,fit0)
            maxH = self.fit_worker.gaussian(center,height,center,width,offset)
            minH1 = self.fit_worker.gaussian(x0[0],height,center,width,offset)
            minH2 = self.fit_worker.gaussian(x0[-1],height,center,width,offset)
            if min(minH1,minH2) < total_min:
                total_min = min(minH1,minH2)
            pen = QtGui.QPen(QtCore.Qt.DotLine)
            pen.setColor(QtGui.QColor(self.COLOR[i]))
            pen.setWidth(2)
            series_fit = QtChart.QLineSeries()
            series_fit.setPen(pen)
            for x,y in zip(x0,fit):
                series_fit.append(x,y)
            self.chart.profileChart.addSeries(series_fit)
            for ax in self.chart.profileChart.axes():
                series_fit.attachAxis(ax)
            self.chart.profileChart.axisY().setRange(min(minH1,minH2,min(y0)),max(maxH,max(y0)))
            if i == self.table.rowCount()-1:
                if self.BGCheck.isChecked() and self.saveResult.isChecked():
                    maxPos = np.argmax(y0)
                    phi = np.full(len(x0),nimg*1.8)
                    radius = np.abs(x0-x0[maxPos])
                    for iphi in range(0,maxPos):
                        phi[iphi]=nimg*1.8+180
                    K = np.full(len(x0),Kperp)
                    self.map_without_background = np.vstack((self.map_without_background,np.vstack((radius,phi,K,y0-fit)).T))
        if self.BGCheck.isChecked() and self.saveResult.isChecked():
            np.savetxt(self.save_path_without_background,np.delete(self.map_without_background,0,0),fmt='%4.3f')
        pen = QtGui.QPen(QtCore.Qt.DotLine)
        pen.setColor(QtGui.QColor('red'))
        pen.setWidth(2)
        series_total = QtChart.QLineSeries()
        series_total.setPen(pen)
        for x,y in zip(x0,total):
            series_total.append(x,y)
        self.chart.profileChart.addSeries(series_total)
        for ax in self.chart.profileChart.axes():
            series_total.attachAxis(ax)
        self.chart.profileChart.axisY().setRange(min(total[0],total[-1],np.amin(y0),total_min),max(np.amax(total),np.amax(y0)))
        QtCore.QCoreApplication.processEvents()

    def reset(self):
        self.currentSource = self.path
        self.currentDestination = self.currentSource
        self.numberOfPeaksCombo.setCurrentText('1')
        self.chooseSourceLabel.setText("The source directory is:\n"+self.currentSource)
        self.chooseDestinationLabel.setText("The save destination is:\n"+self.currentDestination)
        self.destinationNameEdit.setText(self.defaultFileName)
        self.startImageIndexEdit.setText(self.startIndex)
        self.endImageIndexEdit.setText(self.endIndex)
        self.fileType.setCurrentText(".txt")
        self.logBox.clear()
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Reset Successful!")
        self.logBox.append(QtCore.QTime.currentTime().toString("hh:mm:ss")+"\u00A0\u00A0\u00A0\u00A0Ready to Start!")

    def table_auto_initialize(self):
        self.table.disconnect()
        for r in range(0,self.table.rowCount()):
            valueList = ['1','0','5','1','0','5','1','0','5']
            for c in range(0,self.table.columnCount()):
                item = QtWidgets.QTableWidgetItem(valueList[c])
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if c == 0 or c == 3 or c == 6:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                self.table.setItem(r,c,item)
        self.save_table_contents()
        self.table.cellChanged.connect(self.save_table_contents)

    def table_is_ready(self):
        B = True
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                if not (float(self.table.item(i,j).text()) >= float(self.table.item(i,j+1).text()) \
                        and float(self.table.item(i,j).text()) <= float(self.table.item(i,j+2).text())):
                    self.raise_error('Wrong table entry at cell ({},{})'.format(i,j))
                    B = False
        return B

    def save_table_contents(self,row=0,column=0):
        self.guess = []
        self.bound_low = []
        self.bound_high = []
        for j in [3,0,6]:
            for i in range(self.table.rowCount()):
                self.guess.append(float(self.table.item(i,j).text()))
        for j in [4,1,7]:
            for i in range(self.table.rowCount()):
                self.bound_low.append(float(self.table.item(i,j).text()))
        for j in [5,2,8]:
            for i in range(self.table.rowCount()):
                self.bound_high.append(float(self.table.item(i,j).text()))
        self.guess.append(float(self.offset.get_value()))
        self.bound_low.append(0)
        self.bound_high.append(1)

    def number_of_peaks_changed(self):
        self.table.setRowCount(int(self.numberOfPeaksCombo.currentData()))
        for i in range(1,int(self.numberOfPeaksCombo.currentData())+1):
            item = QtWidgets.QTableWidgetItem('Peak {}'.format(i))
            item.setForeground(QtGui.QColor(self.COLOR[i-1]))
            self.table.setVerticalHeaderItem(i-1,item)
        if self.BGCheck.checkState() == 2:
            self.table.setRowCount(self.table.rowCount()+1)
            item = QtWidgets.QTableWidgetItem('BG')
            item.setForeground(QtGui.QColor(self.COLOR[self.table.rowCount()-1]))
            self.table.setVerticalHeaderItem(self.table.rowCount()-1,item)
        self.table_auto_initialize()

    def background_check_changed(self,state):
        if state == 2:
            self.table.setRowCount(self.table.rowCount()+1)
            item = QtWidgets.QTableWidgetItem('BG')
            item.setForeground(QtGui.QColor(self.COLOR[self.table.rowCount()-1]))
            self.table.setVerticalHeaderItem(self.table.rowCount()-1,item)
        elif state == 0:
            self.table.removeRow(self.table.rowCount()-1)
        self.table_auto_initialize()


    def generate_broadening_report(self):
        self.broadeningReport = generate_report.Window()
        self.broadeningReport.main(self.reportPath,True)

    def show_manual_fit(self):
        self.STATUS_REQUESTED.emit()
        self.ManualFitWindow = manual_fit.Window(self.fontList.currentFont().family(),self.fontSizeSlider.value())
        self.ManualFitWindow.FIT_SATISFIED.connect(self.update_results)
        self.ManualFitWindow.set_status(self.status)
        path = os.path.join(self.currentSource,'*.nef')
        startIndex = int(self.startImageIndexEdit.text())
        image_list = []
        for filename in glob.glob(path):
            image_list.append(filename)
        if not image_list == []:
            self.ManualFitWindow.main(image_list[startIndex],self.table.rowCount(),self.BGCheck.checkState())
        else:
            self.raise_error("Please open an image first")

    def set_status(self,status):
        self.status = status

    def raise_error(self,message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setEscapeButton(QtWidgets.QMessageBox.Close)
        msg.exec()

    def raise_attention(self,information):
        info = QtWidgets.QMessageBox()
        info.setIcon(QtWidgets.QMessageBox.Information)
        info.setText(information)
        info.setWindowTitle("Information")
        info.setStandardButtons(QtWidgets.QMessageBox.Ok)
        info.setEscapeButton(QtWidgets.QMessageBox.Close)
        info.exec()

    def progress(self,min,max,val):
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        self.progressBar.setValue(val)

    def progress_reset(self):
        self.progressBar.reset()
        self.progressBar.setVisible(False)
