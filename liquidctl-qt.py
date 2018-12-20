# -*- coding: utf-8 -*-
import sys, os
import mainwindow as mainwindow
import usb.core

from PyQt5 import *
import itertools
import json

import liquidctl.util
from liquidctl.driver.kraken_two import KrakenTwoDriver
from liquidctl.driver.nzxt_smart_device import NzxtSmartDeviceDriver

DRIVERS = [
    KrakenTwoDriver,
    NzxtSmartDeviceDriver,
]

def find_all_supported_devices():
    res = map(lambda driver: driver.find_supported_devices(), DRIVERS)
    return itertools.chain(*res)

class MainWindow(QtWidgets.QMainWindow):

    def get_logo_qcolor(self):
        return QtGui.QColor(self.ui.labelLogo.palette().color(self.ui.labelLogo.foregroundRole()).name())

    def get_logo_color(self):
        color = self.get_logo_qcolor().name().replace("#", "")
        return bytes.fromhex(color)
        #q = self.get_logo_qcolor()
        #return (q.red(), q.green(), q.blue())

    def get_slice_color(self, index):
        color = self.series.slices()[index].color().name().replace("#", "")
        return bytes.fromhex(color)

    def selected_device_changed(self):
        for item in self.ui.menu_Select_Device.children():
            item.setChecked((self.device.device.serial_number == item.objectName()))

        self.ui.comboBoxPresetModes.clear()
        self.ui.comboBoxPresetModes.addItems(self.device.get_color_modes())

        self.ui.labelDevDeviceName.setText("Device: %s" % self.device.description)
        self.ui.labelDevSerialNo.setText("Serial No: %s" % self.device.device.serial_number)

    def reload_device_list(self):
        last_device = self.device

        self.devices = list(enumerate(find_all_supported_devices()))
        self.device = self.devices[0][1]

        self.ui.menu_Select_Device.clear()
        for i, dev in self.devices:
            action = QtWidgets.QAction(self.ui.menu_Select_Device)
            action.setObjectName(dev.device.serial_number)
            action.setText(dev.description)
            action.setCheckable(True)
            action.triggered.connect(self.select_device_menu_tiggered)
            self.ui.menu_Select_Device.addAction(action)

            if ((last_device == None) or (last_device.device.serial_number == dev.device.serial_number)):
                self.device = dev

        self.selected_device_changed()

    def select_device_menu_tiggered(self, arg):
        for i, dev in self.devices:
            if (dev.device.serial_number == self.sender().objectName()):
                self.device = dev
                break

        self.selected_device_changed()

    def save_clicked(self, value):

        if (self.device == None ):
            return

        mode = self.ui.comboBoxPresetModes.currentText()
        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]
        colors = [self.get_slice_color(0) if ringonly else self.get_logo_color()]
        channel = 'sync'
        speed = 'slowest'

        for key, value in self.device.get_animation_speeds().items():
            if (value == self.ui.horizontalSliderASpeed.value()):
                speed = key
                break

        if (maxcolors > 0):
            for i, ps in enumerate(self.series.slices()):
                if (ringonly and i==0):
                    continue
                if (len(colors) == maxcolors):
                    break
                colors.append(self.get_slice_color(i))

        self.ui.labelBothMode.setText('mixed')

        if (self.ui.radioButtonPresetLogo.isChecked()):
            self.ui.labelLogoMode.setText(mode)
            channel = 'logo'

        if (self.ui.radioButtonPresetRing.isChecked()):
            self.ui.labelRingMode.setText(mode)
            channel = 'ring'

        if (self.ui.radioButtonPresetBoth.isChecked()):
            self.ui.labelLogoMode.setText(mode)
            self.ui.labelRingMode.setText(mode)
            self.ui.labelBothMode.setText(mode)
            channel = 'sync'

        if (self.ui.labelLogoMode.text() == self.ui.labelRingMode.text()):
            self.ui.labelBothMode.setText(mode)

        self.device.set_color(channel, mode, colors, speed)

    def mode_changed(self):
        mode = self.ui.comboBoxPresetModes.currentText()
        if mode == '':
            return

        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]
        self.ui.labelPresetModeInfo.setText("Min Colors: %s\nMax Colors: %s\n" % (mincolors, maxcolors))

        enabled = ringonly

        if (ringonly):
            self.ui.radioButtonPresetRing.setChecked(True)
        else:
            #enabled = (maxcolors <= 2)
            self.ui.radioButtonPresetRing.setEnabled(not enabled)
            #self.ui.radioButtonPresetBoth.setChecked(not enabled)

        self.ui.radioButtonPresetBoth.setEnabled(not enabled)
        self.ui.radioButtonPresetLogo.setEnabled(not enabled)

        for i, ps in enumerate(self.series.slices()):
            ps.setBorderColor(QtGui.QColor(255,255,255, 255) if i < maxcolors else QtGui.QColor(1,1,1, 255))

    def slice_hovered(self):
        print(self.sender())
    def slice_clicked(self):
        self.picked = self.sender()
        self.colorDialog.setCurrentColor(self.picked.color())
    def logo_clicked(self, evt):
        self.picked = self.ui.labelLogo
        self.colorDialog.setCurrentColor(self.get_logo_qcolor())

    def color_changed(self, value):
        #print(value.name())
        if self.picked != None:
            if isinstance(self.picked, QtWidgets.QLabel):
                palette = QtGui.QPalette()
                palette.setColor(self.ui.labelLogo.foregroundRole(), value)
                self.ui.labelLogo.setPalette(palette)
            else:
                self.picked.setColor(value)

    def switch_mode_selection(self, sender, target):
        if (sender.isChecked()):
             index = self.ui.comboBoxPresetModes.findText(target.text())
             if index > 0:
                 self.ui.comboBoxPresetModes.setCurrentIndex(index)

    def preset_logo_changed(self):
        self.switch_mode_selection(self.sender(), self.ui.labelLogoMode)
    def preset_ring_changed(self):
        self.switch_mode_selection(self.sender(), self.ui.labelRingMode)
    def preset_both_changed(self):
        self.switch_mode_selection(self.sender(), self.ui.labelBothMode)

    def add_chart(self):
        self.chart = QtChart.QChart()
        self.chartview = QtChart.QChartView(self.chart)
        self.chartview.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self.chart.legend().hide()
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setDropShadowEnabled(enabled=False)
        self.chart.setMinimumHeight(180)
        #self.chart.setRenderHint(QPainter.Antialiasing, True)


       # self.chart.setAnimationOptions(QtChart.QChart.SeriesAnimations)
        self.chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.series = QtChart.QPieSeries()
        self.series.setObjectName('series')
        self.series.setUseOpenGL(enable=True)
        self.series.setHoleSize(0.58)
        
        for i in range(8):
            ps = QtChart.QPieSlice(str(i), 1)
            ps.setBorderColor(QtGui.QColor(1,1,1, 255))
            ps.setColor(QtGui.QColor(i * 32,0,0))
            ps.clicked.connect(self.slice_clicked)
            ps.setExploded(True)
            ps.setExplodeDistanceFactor(0.001)
            # pen = ps.pen()
            # pen.setWidth(2)
            # ps.setPen(pen)
            ps.hovered.connect(self.slice_hovered)
            self.series.append(ps)
        self.chart.addSeries(self.series)
        self.ui.frame.setChart(self.chart)
    def add_color_dialog(self):
        #FIXME: need to find a way to prevent the qdialog from disappearing when the user presses esc key

        self.colorDialog = QtWidgets.QColorDialog()
        self.colorDialog.setOptions(QtWidgets.QColorDialog.NoButtons | QtWidgets.QColorDialog.DontUseNativeDialog)
        self.colorDialog.currentColorChanged.connect(self.color_changed)

        window = self.ui.mdiArea.addSubWindow(self.colorDialog, flags=QtCore.Qt.FramelessWindowHint)
        window.showMaximized()
        
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.device = None
        self.picked = self.ui.labelLogo
        self.add_chart()
        self.add_color_dialog()
        self.reload_device_list()
        
        self.ui.comboBoxPresetModes.currentTextChanged.connect(self.mode_changed)
        self.ui.pushButtonSave.clicked.connect(self.save_clicked)
        self.ui.actionReload.triggered.connect(self.reload_device_list)
        self.ui.labelLogo.mousePressEvent = self.logo_clicked
        self.ui.radioButtonPresetLogo.clicked.connect(self.preset_logo_changed)
        self.ui.radioButtonPresetRing.clicked.connect(self.preset_ring_changed)
        self.ui.radioButtonPresetBoth.clicked.connect(self.preset_both_changed)
        #QtCore.QObject.connect(self.ui.labelLogo, QtCore.SIGNAL("clicked()"), self.logo_clicked)


app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
