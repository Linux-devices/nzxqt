# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtCore, QtChart
from PyQt5.QtCore import pyqtSignal

# default explode distances
RING_HOVER = 0.065
RING_NORMAL = 0.035

# QRingWidget - widget based on QtChart that provides a segmented ring
class QRingWidget(QtCore.QObject):

    slice_clicked = pyqtSignal(QtChart.QPieSlice)
    slice_hovered = pyqtSignal(QtChart.QPieSlice, bool)
    slice_dblclicked = pyqtSignal(QtChart.QPieSlice)

    def __init__(self, chartViewParent: QtChart.QChartView):
        super().__init__()

        self.__chart = QtChart.QChart()
        self.__chart.legend().hide()
        self.__chart.setMinimumHeight(180)
        self.__chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.__series = QtChart.QPieSeries()
        self.__series.setHoleSize(0.58)
        self.__series.setPieSize(0.75)

        for i in range(8):
            ps = QtChart.QPieSlice(str(i), 1)
            ps.setExploded(True)
            ps.setExplodeDistanceFactor(RING_NORMAL)

            ps.clicked.connect(self.__slice_clicked)
            ps.hovered.connect(self.__slice_hovered)
            ps.doubleClicked.connect(self.__slice_dblclicked)

            self.__series.append(ps)

        self.__chart.addSeries(self.__series)

        chartViewParent.setRenderHint(QtGui.QPainter.Antialiasing, True)
        chartViewParent.setChart(self.__chart)

        self.__last_slice = self.__series.slices()[0]

    def __slice_clicked(self):
        self.slice_clicked.emit(self.sender())

    def __slice_hovered(self, state):
        ps = self.sender()

        self.slice_hovered.emit(ps, state)

        if state:
            self.last_color = ps.color()
            ps.setColor(self.last_color.lighter())
        else:
            ps.setColor(self.last_color)

        ps.setExplodeDistanceFactor(RING_HOVER if state else RING_NORMAL)


    def __slice_dblclicked(self):
        self.slice_dblclicked.emit(self.sender())

    def setBackgroundColor(self, color):
        brush = QtGui.QBrush(color)
        self.__chart.setBackgroundBrush(brush)

    def slices(self):
        return self.__series.slices()