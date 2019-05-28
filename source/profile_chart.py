from process import Image
from PyQt5 import QtCore, QtWidgets, QtGui, QtChart, QtSvg
import numpy as np

class ProfileChart(QtChart.QChartView):

    CHART_MOUSE_MOVEMENT = QtCore.pyqtSignal(QtCore.QPointF,str)
    CHART_IS_PRESENT = False

    def __init__(self,config):
        super(ProfileChart,self).__init__()
        chartDefault = dict(config['chartDefault'].items())
        if int(chartDefault['theme']) == 0:
            self.theme = QtChart.QChart.ChartThemeLight
        if int(chartDefault['theme']) == 1:
            self.theme = QtChart.QChart.ChartThemeBlueCerulean
        if int(chartDefault['theme']) == 2:
            self.theme = QtChart.QChart.ChartThemeDark
        if int(chartDefault['theme']) == 3:
            self.theme = QtChart.QChart.ChartThemeBrownSand
        if int(chartDefault['theme']) == 4:
            self.theme = QtChart.QChart.ChartThemeBlueNcs
        if int(chartDefault['theme']) == 5:
            self.theme = QtChart.QChart.ChartThemeHighContrast
        if int(chartDefault['theme']) == 6:
            self.theme = QtChart.QChart.ChartThemeBlueIcy
        if int(chartDefault['theme']) == 7:
            self.theme = QtChart.QChart.ChartThemeQt

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self._scaleFactor = 1
        self.setContentsMargins(0,0,0,0)
        self.profileChart = QtChart.QChart()
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.profileChart.setTheme(self.theme)
        self.setChart(self.profileChart)
        self.image_worker = Image()

    def refresh(self,config):
        chartDefault = dict(config['chartDefault'].items())
        if int(chartDefault['theme']) == 0:
            self.theme = QtChart.QChart.ChartThemeLight
        elif int(chartDefault['theme']) == 1:
            self.theme = QtChart.QChart.ChartThemeBlueCerulean
        elif int(chartDefault['theme']) == 2:
            self.theme = QtChart.QChart.ChartThemeDark
        elif int(chartDefault['theme']) == 3:
            self.theme = QtChart.QChart.ChartThemeBrownSand
        elif int(chartDefault['theme']) == 4:
            self.theme = QtChart.QChart.ChartThemeBlueNcs
        elif int(chartDefault['theme']) == 5:
            self.theme = QtChart.QChart.ChartThemeHighContrast
        elif int(chartDefault['theme']) == 6:
            self.theme = QtChart.QChart.ChartThemeBlueIcy
        elif int(chartDefault['theme']) == 7:
            self.theme = QtChart.QChart.ChartThemeQt
        else:
            self.raise_error("Wrong theme")
        self.profileChart.setTheme(self.theme)

    def add_chart(self,radius,profile,type="line"):
        #pen = QtGui.QPen(QtCore.Qt.SolidLine)
        #pen.setColor(QtGui.QColor(QtCore.Qt.blue))
        #pen.setWidth(3)
        series = QtChart.QLineSeries()
        #series.setPen(pen)
        self.currentRadius = []
        self.currentProfile = []
        for x,y in zip(radius,profile):
            series.append(x,y)
            self.currentRadius.append(x)
            self.currentProfile.append(y)
        self.profileChart = QtChart.QChart()
        self.profileChart.setTheme(self.theme)
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        self.profileChart.removeAllSeries()
        self.profileChart.addSeries(series)
        if type == "line" or type == "rectangle":
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QValueAxis()
            self.axisX.setTitleText("K_para (\u212B\u207B\u00B9)")
            self.axisY.setTitleText("Intensity (arb. units)")
            self.axisY.setTickCount(10)
        elif type == "arc":
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QValueAxis()
            self.axisX.setTitleText("\u03A7 (\u00BA)")
            self.axisY.setTitleText("Intensity (arb. units)")
            self.axisY.setTickCount(10)
        elif type == "cost_function":
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QLogValueAxis()
            self.axisX.setTitleText("Number of Iterations")
            self.axisY.setTitleText("Cost Function")
        self.axisX.setLabelsFont(QtGui.QFont(self.fontname,self.fontsize,57))
        self.axisX.setTitleFont(QtGui.QFont(self.fontname,self.fontsize,57))
        self.axisY.setLabelsFont(QtGui.QFont(self.fontname,self.fontsize,57))
        self.axisY.setTitleFont(QtGui.QFont(self.fontname,self.fontsize,57))
        self.profileChart.addAxis(self.axisX, QtCore.Qt.AlignBottom)
        self.profileChart.addAxis(self.axisY, QtCore.Qt.AlignLeft)
        series.attachAxis(self.axisX)
        series.attachAxis(self.axisY)
        self.profileChart.legend().setVisible(False)
        self.setChart(self.profileChart)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.CHART_IS_PRESENT = True

    def adjust_fonts(self,fontname,fontsize):
        self.set_fonts(fontname,fontsize)
        try:
            self.axisX.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisX.setTitleFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setLabelsFont(QtGui.QFont(fontname,fontsize,57))
            self.axisY.setTitleFont(QtGui.QFont(fontname,fontsize,57))
        except:
            pass

    def set_fonts(self,fontname,fontsize):
        self.fontname = fontname
        self.fontsize = fontsize

    def set_img(self,img):
        self._img = img

    def set_scale_factor(self,s):
        self._scaleFactor = s

    def line_scan(self,start,end):
        x,y = self.image_worker.get_line_scan(start,end,self._img,self._scaleFactor)
        self.add_chart(x,y,"line")

    def integral(self,start,end,width):
        x,y = self.image_worker.get_integral(start,end,width,self._img,self._scaleFactor)
        self.add_chart(x,y,"rectangle")

    def chi_scan(self,center,radius,width,chiRange,tilt,chiStep=1):
        x,y = self.image_worker.get_chi_scan(center,radius,width,chiRange,tilt,self._img,chiStep)
        self.add_chart(x,y,"arc")

    def mouseMoveEvent(self, event):
        """This is an overload function"""
        if self.chart().plotArea().contains(event.pos()) and self.CHART_IS_PRESENT:
            self.setCursor(QtCore.Qt.CrossCursor)
            position = self.chart().mapToValue(event.pos())
            self.CHART_MOUSE_MOVEMENT.emit(position,"chart")
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(ProfileChart, self).mouseMoveEvent(event)

    def contextMenuEvent(self,event):
        """This is an overload function"""
        self.menu = QtWidgets.QMenu()
        self.saveAsText = QtWidgets.QAction('Save as text...')
        self.saveAsText.triggered.connect(self.save_profile_as_text)
        self.saveAsImage = QtWidgets.QAction('Save as an image...')
        self.saveAsImage.triggered.connect(self.save_profile_as_image)
        self.saveAsSVG = QtWidgets.QAction('Export as SVG...')
        self.saveAsSVG.triggered.connect(self.save_profile_as_SVG)
        self.menu.addAction(self.saveAsText)
        self.menu.addAction(self.saveAsImage)
        self.menu.addAction(self.saveAsSVG)
        self.menu.popup(event.globalPos())

    def save_profile_as_text(self):
        if self.CHART_IS_PRESENT:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./profile.txt","Text (*.txt)")
            if not self.filename[0] == "":
                np.savetxt(self.filename[0],np.vstack((self.currentRadius,self.currentProfile)).transpose(),fmt='%5.3f')
            else:
                return
        else:
            self.raise_error("No line profile is available")

    def save_profile_as_image(self):
        if self.CHART_IS_PRESENT:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./profile.png","PNG (*.png);;JPEG (*.jpeg);;GIF (*.gif);;BMP (*.bmp)")
            if not self.filename[0] == "":
                output_size = QtCore.QSize(800,600)
                output_rect = QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(output_size))
                image = QtGui.QImage(output_size,QtGui.QImage.Format_ARGB32)
                image.fill(QtCore.Qt.transparent)
                original_size = self.profileChart.size()
                self.profileChart.resize(QtCore.QSizeF(output_size))
                painter = QtGui.QPainter()
                painter.begin(image)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                self.profileChart.scene().render(painter, source=output_rect,target=output_rect,mode=QtCore.Qt.IgnoreAspectRatio)
                painter.end()
                self.profileChart.resize(original_size)
                image.save(self.filename[0])
            else:
                return
        else:
            self.raise_error("No line profile is available")

    def save_profile_as_SVG(self):
        if self.CHART_IS_PRESENT:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(None,"choose save file name","./profile.svg","SVG (*.svg)")
            if not self.filename[0] == "":
                output_size = QtCore.QSize(800,600)
                output_rect = QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(output_size))

                svg = QtSvg.QSvgGenerator()
                svg.setFileName(self.filename[0])
                svg.setSize(output_size)
                svg.setViewBox(output_rect)

                original_size = self.profileChart.size()
                self.profileChart.resize(QtCore.QSizeF(output_size))
                painter = QtGui.QPainter()
                painter.begin(svg)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                self.profileChart.scene().render(painter, source=output_rect,target=output_rect,mode=QtCore.Qt.IgnoreAspectRatio)
                painter.end()
                self.profileChart.resize(original_size)
            else:
                return
        else:
            self.raise_error("No line profile is available")

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
