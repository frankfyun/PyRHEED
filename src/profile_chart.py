from process import Image
from PyQt5 import QtCore, QtWidgets, QtGui, QtChart, QtSvg
import numpy as np

class ProfileChart(QtChart.QChartView):

    CHART_MOUSE_MOVEMENT = QtCore.pyqtSignal(QtCore.QPointF,str)
    CHART_MOUSE_LEAVE = QtCore.pyqtSignal()
    CHART_IS_PRESENT = False
    FONTS_CHANGED = QtCore.pyqtSignal(str,int)

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

    def append_to_chart(self,x,y,a,b,angle,weights,colors,type="ellipse"):
        ncomp = len(x)
        series_length = len(self.profileChart.series()) 
        chart_width = self.profileChart.plotArea().width()
        scale = chart_width/14
        if series_length > 2*ncomp:
            while series_length>1:
                last_series = self.profileChart.series()[-1]
                self.profileChart.removeSeries(last_series)
                series_length -= 1
        for n in range(ncomp):
            series = QtChart.QScatterSeries()
            series.setMarkerShape(QtChart.QScatterSeries.MarkerShapeRectangle)
            series.setBorderColor(QtCore.Qt.transparent)
            ea, eb = a[n]*scale,b[n]*scale
            delta_a = ea*(1-np.cos(angle[n]/180*np.pi))-eb*np.sin(angle[n]/180*np.pi)
            delta_b = ea*np.sin(angle[n]/180*np.pi)+eb*(1-np.cos(angle[n]/180*np.pi))
            msize = max(ea, eb)*np.sqrt(2)
            series.setMarkerSize(msize)
            ellipsePath = QtGui.QPainterPath()
            ellipsePath.addEllipse(0,0,ea,eb)
            ellipse = QtGui.QImage(msize,msize,QtGui.QImage.Format_ARGB32)
            ellipse.fill(QtCore.Qt.transparent)
            ellipse_painter = QtGui.QPainter(ellipse)
            ellipse_painter.translate(msize//2-ea//2+delta_a//2,msize//2-eb//2+delta_b//2)
            ellipse_painter.rotate(-angle[n])
            ellipse_painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter_color = QtGui.QColor(colors[n])
            painter_color.setAlphaF(weights[n])
            pen_color = QtGui.QColor(QtCore.Qt.black)
            pen_color.setAlphaF(weights[n])
            ellipse_painter.setPen(pen_color)
            ellipse_painter.setBrush(painter_color)
            ellipse_painter.drawPath(ellipsePath)
            ellipse_painter.end()
            series.setBrush(QtGui.QBrush(ellipse))

            if weights[n] > 0.01:
                label_series = QtChart.QScatterSeries()
                label_series.setMarkerShape(QtChart.QScatterSeries.MarkerShapeRectangle)
                label_series.setMarkerSize(1000)
                label_series.setBorderColor(QtCore.Qt.transparent)
                label = QtGui.QImage(1000,1000,QtGui.QImage.Format_ARGB32)
                label.fill(QtCore.Qt.transparent)
                label_painter = QtGui.QPainter(label)
                label_painter_color = QtGui.QColor(colors[n])
                label_pen_color = QtGui.QColor(colors[n])
                label_painter.setPen(label_pen_color)
                label_painter.setBrush(label_painter_color)
                label_painter.setFont(QtGui.QFont("Times",20))
                region = QtCore.QRect(500,500,1000,1000) 
                label_painter.drawText(region,QtCore.Qt.AlignLeft,"({:.2f},{:.2f})".format(x[n],y[n]))
                label_painter.end()
                label_series.setBrush(QtGui.QBrush(label))
                label_series.append(x[n],y[n])
                self.profileChart.addSeries(label_series)
                label_series.attachAxis(self.axisX)
                label_series.attachAxis(self.axisY)

            series.append(x[n],y[n])
            self.profileChart.addSeries(series)
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)

    def add_chart(self,radius,profile,type="line",slope=0):
        #pen = QtGui.QPen(QtCore.Qt.SolidLine)
        #pen.setColor(QtGui.QColor(QtCore.Qt.blue))
        #pen.setWidth(3)
        if type == 'scatter':
            series = QtChart.QScatterSeries()
            scatter_pen_color = QtGui.QColor(QtCore.Qt.blue)
            scatter_pen_color.setAlphaF(0.7)
            pen = QtGui.QPen(scatter_pen_color)
            series.setPen(pen)
            series.setMarkerSize(10)
            series.setBorderColor(QtCore.Qt.black)
        else:
            series = QtChart.QLineSeries()
            #series.setPen(pen)
        self.currentRadius = []
        self.currentProfile = []
        for x,y in zip(radius,profile):
            series.append(x,y)
            self.currentRadius.append(x)
            self.currentProfile.append(y)
        self.profileChart = QtChart.QChart()
        self.profileChart.removeAllSeries()
        self.profileChart.addSeries(series)
        self.profileChart.setTheme(self.theme)
        self.profileChart.setBackgroundRoundness(0)
        self.profileChart.setMargins(QtCore.QMargins(0,0,0,0))
        if type == "line" or type == "rectangle":
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QValueAxis()
            if slope > 1:
                self.axisX.setTitleText("<b>k</b><sub>||</sub> (\u212B\u207B\u00B9)")
            else:
                self.axisX.setTitleText("<b>k</b><sub>\u27C2</sub> (\u212B\u207B\u00B9)")
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
        elif type == "kikuchi line":
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QValueAxis()
            self.axisX.setTitleText("<b>k</b><sub>x</sub> (\u212B\u207B\u00B9)")
            self.axisY.setTitleText("<b>k</b><sub>y</sub> (\u212B\u207B\u00B9)")
            self.axisY.setTickCount(10)
            self.axisY.setReverse(True)
        elif type == "ELBO change":
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QLogValueAxis()
            self.axisX.setTitleText("Number of Iterations")
            self.axisY.setTitleText("Log of ELBO change")
        elif type == 'scatter':
            self.axisX = QtChart.QValueAxis()
            self.axisX.setTickCount(10)
            self.axisY = QtChart.QValueAxis()
            self.axisX.setTitleText("X")
            self.axisY.setTitleText("Y")
            self.axisX.setRange(-7,7)
            self.axisY.setRange(-7,7)
        if hasattr('self','fontname'):
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

    def set_axes_visible(self,state):
        if state == 2:
            self.profileChart.axisX().setVisible(True)
            self.profileChart.axisY().setVisible(True)
        elif state == 0:
            self.profileChart.axisX().setVisible(False)
            self.profileChart.axisY().setVisible(False)

    def set_grids_visible(self,state):
        if state == 2:
            self.profileChart.axisX().setGridLineVisible(True)
            self.profileChart.axisY().setGridLineVisible(True)
        elif state == 0:
            self.profileChart.axisX().setGridLineVisible(False)
            self.profileChart.axisY().setGridLineVisible(False)

    def set_fonts(self,fontname,fontsize):
        self.fontname = fontname
        self.fontsize = fontsize

    def set_img(self,img):
        self._img = img

    def set_scale_factor(self,s):
        self._scaleFactor = s

    def line_scan(self,start,end):
        x,y = self.image_worker.get_line_scan(start,end,self._img,self._scaleFactor)
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        slope=abs((x0-x1)/(y1-y0)) if y1!=y0 else 0
        self.add_chart(x,y,"line",slope)

    def integral(self,start,end,width):
        x,y = self.image_worker.get_integral(start,end,width,self._img,self._scaleFactor)
        x0,y0,x1,y1 = start.x(),start.y(),end.x(),end.y()
        slope=abs((x0-x1)/(y1-y0)) if y1!=y0 else 0
        self.add_chart(x,y,"rectangle",slope)

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
            self.CHART_MOUSE_LEAVE.emit()
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
