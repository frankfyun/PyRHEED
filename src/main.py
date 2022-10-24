from PyQt5 import QtGui, QtWidgets, QtCore
import broadening
import gmm
import configparser
import generate_report
import graph_3D_surface
import kikuchi
import manual_fit
import os
import preference
import reciprocal_space_mapping
import simulate_RHEED
import statistical_factor
import scenario
import sys
import window

class Window():
    """The main class"""
    def __init__(self):
        self.dirname = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(os.path.join(self.dirname,'configuration.ini'))  #Read the configuration file
        self.app = QtWidgets.QApplication(sys.argv)
        self.screenScaleFactor = (self.app.primaryScreen().geometry().width()/1200 + self.app.primaryScreen().geometry().height()/675)//2
        icon = QtGui.QIcon(os.path.join(self.dirname,'icons/icon.png'))
        self.app.setWindowIcon(icon)
        self.app.setFont(QtGui.QFont(self.app.font().family(),self.app.font().pointSize()*self.screenScaleFactor))
        self.app.setStyle("fusion")
        self.lightPalette = self.app.palette()
        self.darkPalette = QtGui.QPalette()
        self.darkPalette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        self.darkPalette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        self.darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        self.darkPalette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        self.darkPalette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
        self.darkPalette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        self.darkPalette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.darkPalette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.darkPalette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.darkPalette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.darkPalette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.darkPalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        self.darkPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.window = window.Window(config)    #Initialze the main window using the default values in the configuration
        self.window.showMaximized()
        #self.window.setFixedSize(1600,1000)
        self.window.show()
        #Connect the signals emitted by the window object
        self.window.DEFAULT_PROPERTIES_REQUESTED.connect(self.run_preference)
        self.window.RECIPROCAL_SPACE_MAPPING_REQUESTED.connect(self.run_reciprocal_space_mapping)
        self.window.BROADENING_REQUESTED.connect(self.run_broadening)
        self.window.GMM_REQUESTED.connect(self.run_gmm)
        self.window.MANUAL_FIT_REQUESTED.connect(self.run_manual_fit)
        self.window.GENERATE_REPORT_REQUESTED.connect(self.run_generate_report)
        self.window.STATISTICAL_FACTOR_REQUESTED.connect(self.run_statistical_factor)
        self.window.DIFFRACTION_PATTERN_REQUESTED.connect(self.run_simulate_RHEED)
        self.window.KIKUCHI_PATTERN_REQUESTED.connect(self.run_kikuchi)
        self.window.THREE_DIMENSIONAL_GRAPH_REQUESTED.connect(self.run_3D_graph)
        self.window.SCENARIO_REQUESTED.connect(self.run_scenario)
        self.window.TOGGLE_DARK_MODE.connect(self.toggle_light_dark_mode)
        self.preference = preference.Window()
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.window.refresh)
        self.toggle_light_dark_mode("light")
        sys.exit(self.app.exec_())

    def toggle_light_dark_mode(self, mode):
        if mode == "light":
            self.app.setPalette(self.lightPalette)
            self.window.isDarkmode = False
            for i in range(0,self.window.mainTab.count()):
                self.window.mainTab.widget(i).setBackgroundBrush(QtGui.QBrush(QtGui.QColor('darkGray')))
        elif mode == "dark":
            self.app.setPalette(self.darkPalette)
            self.window.isDarkmode = True
            for i in range(0,self.window.mainTab.count()):
                self.window.mainTab.widget(i).setBackgroundBrush(QtGui.QBrush(QtGui.QColor(20, 20, 20)))
        self.app.setStyle("fusion")
        self.preference.toggle_dark_theme(mode)

    def run_preference(self):
        self.preference.main()

    def run_scenario(self):
        self.scenario_window = scenario.Window()

    def run_reciprocal_space_mapping(self,path):
        self.reciprocal_space_mapping = reciprocal_space_mapping.Window()
        self.reciprocal_space_mapping.STATUS_REQUESTED.connect(self.window.status)
        self.reciprocal_space_mapping.SHOW_3D_GRAPH.connect(self.run_3D_graph)
        self.reciprocal_space_mapping.SHOW_2D_CONTOUR.connect(self.run_2D_contour)
        self.reciprocal_space_mapping.CONNECT_TO_CANVAS.connect(self.connect_mapping_to_canvas)
        self.window.RETURN_STATUS.connect(self.reciprocal_space_mapping.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.reciprocal_space_mapping.refresh)
        self.reciprocal_space_mapping.main(path)

    def run_generate_report(self,path):
        self.generate_report = generate_report.Window()
        self.generate_report.STATUS_REQUESTED.connect(self.window.status)
        self.window.RETURN_STATUS.connect(self.generate_report.set_status)
        self.generate_report.main(path)

    def run_manual_fit(self,path,nop):
        self.manual_fit = manual_fit.Window()
        self.manual_fit.STATUS_REQUESTED.connect(self.window.status)
        self.window.RETURN_STATUS.connect(self.manual_fit.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.manual_fit.refresh)
        self.manual_fit.main(path,nop)

    def run_gmm(self,path):
        self.gmm = gmm.Window()
        self.gmm.STATUS_REQUESTED.connect(self.window.status)
        self.gmm.CONNECT_TO_CANVAS.connect(self.connect_gmm_to_canvas)
        self.window.RETURN_STATUS.connect(self.gmm.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.gmm.refresh)
        self.gmm.main(path)

    def run_broadening(self,path):
        self.broadening = broadening.Window()
        self.broadening.STATUS_REQUESTED.connect(self.window.status)
        self.broadening.CONNECT_TO_CANVAS.connect(self.connect_broadening_to_canvas)
        self.window.RETURN_STATUS.connect(self.broadening.set_status)
        self.preference.DEFAULT_SETTINGS_CHANGED.connect(self.broadening.refresh)
        self.broadening.main(path)

    def run_statistical_factor(self):
        self.statistical_factor = statistical_factor.Window()
        self.statistical_factor.main()

    def run_simulate_RHEED(self):
        self.simulation = simulate_RHEED.Window()
        self.simulation.main()

    def run_kikuchi(self):
        self.kikuchi = kikuchi.Window()
        self.kikuchi.main()

    def run_3D_graph(self,path=''):
        """The window to show a 3D surface

        Args:
            path: str, optional
                The path of the text file that contains the 2D reciprocal space mapping data. Default is ''.
        """
        self.graph = graph_3D_surface.Graph()
        self.graph.run_3D_graph(path)

    def run_2D_contour(self, path=None, insideGraph3D = False, min=0.0, max=1.0, radius_min=0, radius_max=10, number_of_levels=50, colormap='jet'):
        """The window to show a 2D Contour

        Args:
            path: str, optional
                The path of the text file that contains the 2D reciprocal space mapping data. Default is None.
            insideGraph3D: bool, optional
                True if the function is intended to be called from a 3D graph window. Default is False.
            min: float, optional
                Level minimum. Default is 0.0.
            max: float,optional
                Level maximum. Default is 1.0.
            radius_min: float, optional
                The start position on the radial axis. Default is 0.
            radius_max: float, optional
                The end position on the radial axis. Default is 10.
            number_of_levels: int, optional
                The number of contour levels. Default is 50.
            colormap: str, optional
                The name of the colormap. Default is 'jet'.

        """
        self.graph = graph_3D_surface.Graph()
        self.graph.show_2d_contour(path,insideGraph3D = insideGraph3D, min=min, max=max, radius_min=radius_min, radius_max=radius_max,\
                                   number_of_levels=number_of_levels, colormap=colormap)

    def connect_gmm_to_canvas(self):
        """Signal Connection"""
        self.gmm.DRAW_LINE_REQUESTED.connect(self.window.mainTab.currentWidget().draw_line)
        self.gmm.DRAW_RECT_REQUESTED.connect(self.window.mainTab.currentWidget().draw_rect)

    def connect_broadening_to_canvas(self):
        """Signal Connection"""
        self.broadening.DRAW_LINE_REQUESTED.connect(self.window.mainTab.currentWidget().draw_line)
        self.broadening.DRAW_RECT_REQUESTED.connect(self.window.mainTab.currentWidget().draw_rect)

    def connect_mapping_to_canvas(self):
        """Signal Connection"""
        self.reciprocal_space_mapping.DRAW_LINE_REQUESTED.connect(self.window.mainTab.currentWidget().draw_line)
        self.reciprocal_space_mapping.DRAW_RECT_REQUESTED.connect(self.window.mainTab.currentWidget().draw_rect)
        self.reciprocal_space_mapping.REFRESH_CANVAS.connect(self.window.refresh_image)

if __name__ == '__main__':
    Window()
