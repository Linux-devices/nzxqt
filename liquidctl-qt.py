# -*- coding: utf-8 -*-
import sys, os
import mainwindow as mainwindow
import usb.core

from PyQt5 import *
import argparse
import itertools

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
    
    def reload_device_list(self):
        last_device = self.device

        self.devices = list(enumerate(find_all_supported_devices()))
        #self.device = last_device if (last_device in self.devices) else self.devices[0]
        self.device = self.devices[0][1]

        self.ui.menu_Select_Device.clear()

        for i, dev in self.devices:
 
            action = QtWidgets.QAction(self.ui.menu_Select_Device)
            action.setObjectName(dev.device.serial_number)
            action.setText(dev.description)
            action.setCheckable(True)
            action.triggered.connect(self.select_device)
            self.ui.menu_Select_Device.addAction(action)

            if ((last_device == None) or
                (last_device.device.serial_number == dev.device.serial_number) 
                ):
                self.device = dev
                action.setChecked(True)

        self.ui.comboBoxPresetModes.clear()
        self.ui.comboBoxPresetModes.addItems(self.device.get_color_modes())
    def select_device(self, arg):
        self.sender()

    def save_clicked(self, value):

        if (self.device == None ):
            return

        mode = self.ui.comboBoxPresetModes.currentText()
        channel = 'sync'
        colors = []
        speed = 'slowest'
        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]

        for key, value in self.device.get_animation_speeds().items():
            if (value == self.ui.horizontalSliderASpeed.value()):
                speed = key
                break

        if (maxcolors > 0):
            for i, ps in enumerate(self.series.slices()):
                color = ps.color().name().replace("#", "")
                if (i >= maxcolors):
                    break

                colors.append(bytes.fromhex(color))

        if (self.ui.checkBoxLogoLed.isChecked()):
            channel = 'logo'

        if (self.ui.checkBoxRingLed.isChecked()):
            channel = 'ring'

        if (self.ui.checkBoxRingLed.isChecked() and self.ui.checkBoxLogoLed.isChecked()):
            channel = 'sync'

        self.device.set_color(channel, mode, colors, speed)


    def mode_changed(self):
        pass
    def slice_clicked(self):
        sender = self.sender()
        self.picked = sender
        #sender.setBorderColor(QtGui.QColor(128,1,1, 255))
        self.colorDialog.setCurrentColor(self.picked.color())
        #print(sender.label())
    def logo_clicked(self):
        self.picked = self.ui.pushButtonLogo
        self.colorDialog.setCurrentColor(self.picked.textColor())

    def color_changed(self, value):
        #print(value.name())
        if self.picked != None:
            self.picked.setColor(value)

    def add_chart(self):
        self.chart = QtChart.QChart()
        self.chart.legend().hide()
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setDropShadowEnabled(enabled=False)
        self.chart.setMinimumHeight(180)
        #self.chart.setAnimationOptions(QtChart.QChart.SeriesAnimations)
        self.chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.series = QtChart.QPieSeries()
        self.series.setObjectName('series')
        self.series.setUseOpenGL(enable=True)
        self.series.setHoleSize(0.55)

        for i in range(8):
            ps = QtChart.QPieSlice(str(i), 1)
            ps.setBorderColor(QtGui.QColor(1,1,1, 255))
            ps.setColor(QtGui.QColor(i * 32,0,0))
            ps.clicked.connect(self.slice_clicked)
            #ps.hovered.connect(self.sliceHovered)
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
        self.add_chart()
        self.add_color_dialog()
        self.reload_device_list()
        
        self.ui.comboBoxPresetModes.currentTextChanged.connect(self.mode_changed)
        self.ui.pushButtonSave.clicked.connect(self.save_clicked)
        self.ui.actionReload.triggered.connect(self.reload_device_list)
        self.ui.pushButtonLogo.clicked.connect(self.logo_clicked)


app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
