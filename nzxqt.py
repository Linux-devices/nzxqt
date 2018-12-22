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

_SLICE_BORDER = {
    'enable'  : QtGui.QColor(1,1,1,160),
    'disable' : QtGui.QColor(127,127,127,160),
    'hover'   : QtGui.QPalette().color(QtGui.QPalette.Highlight),
    'picked'  : QtGui.QPalette().color(QtGui.QPalette.HighlightedText)
}

def find_all_supported_devices():
    res = map(lambda driver: driver.find_supported_devices(), DRIVERS)
    return itertools.chain(*res)

class MainWindow(QtWidgets.QMainWindow):

    def device_selection_changed(self):
        """Updates the interface when a device has been selected"""
        for item in self.ui.menu_Select_Device.children():
            if isinstance(item, QtWidgets.QAction):
                item.setChecked((self.device.device.serial_number == item.objectName()))

        self.ui.comboBoxPresetModes.clear()

        for mode in self.device.get_color_modes():
            self.ui.comboBoxPresetModes.addItem(str(mode).title())

        self.ui.labelDevDeviceName.setText("Device: %s" % self.device.description)
        self.ui.labelDevSerialNo.setText("Serial No: %s" % self.device.device.serial_number)

        self.preset_mode_changed()
    def update_menu_device_list(self):
        """Populates device menu with supported devices"""
        last_device = self.device if hasattr(self, 'device') else None

        self.devices = list(enumerate(find_all_supported_devices()))
        if len(self.devices) == 0:
            return

        self.ui.menu_Select_Device.clear()

        for i, dev in self.devices:
            action = QtWidgets.QAction(dev.description, self.ui.menu_Select_Device)
            action.setObjectName(dev.device.serial_number)
            action.setCheckable(True)
            action.triggered.connect(self.select_device_menu_tiggered)

            self.ui.menu_Select_Device.addAction(action)

            if ((last_device == None) or (last_device.device.serial_number == dev.device.serial_number)):
                self.device = dev

        self.device_selection_changed()
    def select_device_menu_tiggered(self):
        """Activates device menu item when clicked"""
        for i, dev in self.devices:
            if (dev.device.serial_number == self.sender().objectName()):
                self.device = dev
                break

        self.device_selection_changed()

    def preset_save_clicked(self):
        """Sends preset values to the currently selected device"""
        if (self.device == None ):
            return

        mode = self.ui.comboBoxPresetModes.currentText().lower()
        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]
        colors = [self.get_slice_color(0) if ringonly else bytes.fromhex(self.get_led_logo_qcolor().name().strip("#"))]
        channel = 'sync'
        speed = 'slowest'

        mode = mode.title()

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

        self.ui.labelBothMode.setText("Mixed-modes")

        if (self.ui.labelLogoMode.text() == self.ui.labelRingMode.text()):
            self.ui.labelBothMode.setText(mode)

        self.device.set_color(channel, mode.lower(), colors, speed)
    def preset_speed_changed(self, value: str):
        """Updates animation speed information"""
        self.ui.labelPresetAniSpeedLabel.setText("Animation Speed: %s" % value)
    def preset_mode_changed(self):
        """Highlights ring segments and radiobuttons that are valid for the preset"""
        mode = self.ui.comboBoxPresetModes.currentText().lower()
        if mode == '':
            return

        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]
        
        if (ringonly):
            self.ui.radioButtonPresetRing.setChecked(True)
        else:
            self.ui.radioButtonPresetRing.setEnabled(not ringonly)

        self.ui.radioButtonPresetBoth.setEnabled(not ringonly)
        self.ui.radioButtonPresetLogo.setEnabled(not ringonly)

        for i, ps in enumerate(self.series.slices()):
            self.set_slice_border_color(ps, _SLICE_BORDER['enable'])

        for i, ps in enumerate(self.series.slices()):
            if i == maxcolors:
                break
            self.set_slice_border_color(ps)
        
        if isinstance(self.picked, QtChart.QPieSlice):
            self.set_slice_border_color(self.picked, _SLICE_BORDER['picked'])
        
        font = self.ui.labelLogo.font()
        font.setUnderline(self.picked == self.ui.labelLogo)
        self.ui.labelLogo.setFont(font)
    def preset_mode_reselect(self, sender: QtWidgets.QRadioButton, target: QtWidgets.QLabel):
        """Reselects the preset based on the target value"""
        if (sender.isChecked()):
            index = self.ui.comboBoxPresetModes.findText(target.text())
            if index < 0:
                index = 0
            self.ui.comboBoxPresetModes.setCurrentIndex(index)

    def get_led_logo_qcolor(self) -> QtGui.QColor:
        """Gets the logo QColor from its Palette"""
        return self.ui.labelLogo.palette().color(0)
    def led_logo_clicked(self, evt: QtGui.QMouseEvent):
        """Set color change target to logo"""
        self.picked = self.ui.labelLogo
        self.colorDialog.setCurrentColor(self.get_led_logo_qcolor())
        
        self.preset_mode_changed()
    def led_mode_both_changed(self):
        """Reselects both preset when radiobutton is activated"""
        self.preset_mode_reselect(self.sender(), self.ui.labelBothMode)
    def led_mode_logo_changed(self):
        """Reselects logo preset when radiobutton is activated"""
        self.preset_mode_reselect(self.sender(), self.ui.labelLogoMode)
    def led_mode_ring_changed(self):
        """Reselects ring preset when radiobutton is activated"""
        self.preset_mode_reselect(self.sender(), self.ui.labelRingMode)

    def ring_init(self):
        """Adds a ring widget as a QChart"""
        self.chart = QtChart.QChart()
        self.chartview = QtChart.QChartView(self.chart)
        self.chartview.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self.chart.legend().hide()
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setDropShadowEnabled(enabled=False)
        self.chart.setMinimumHeight(180)
        self.chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.series = QtChart.QPieSeries()
        self.series.setObjectName('series')
        self.series.setUseOpenGL(enable=True)
        self.series.setHoleSize(0.58)
        self.series.setPieSize(0.75)

        for i in range(8):
            ps = QtChart.QPieSlice(str(i), 1)
            ps.setExploded(True)
            ps.setExplodeDistanceFactor(0.035)

            ps.clicked.connect(self.ring_slice_clicked)
            ps.hovered.connect(self.ring_slice_hovered)
            ps.doubleClicked.connect(self.ring_slice_dblclicked)

            self.series.append(ps)
        self.chart.addSeries(self.series)
        self.ui.frame.setChart(self.chart)
    def ring_slice_clicked(self):
        """Stores slice and sets color dialog color"""
        self.picked = self.sender()
        self.colorDialog.setCurrentColor(self.last_color)

        self.preset_mode_changed()
    def ring_slice_dblclicked(self):
        """Fills all slices with the same color"""
        for i, ps in enumerate(self.series.slices()):
            ps.setColor(self.last_color)
    def ring_slice_hovered(self, state):
        """Event when slice is hovered"""
        if state:
            self.last_color = self.sender().color()
            self.sender().setColor(self.last_color.lighter())
        else:
            self.sender().setColor(self.last_color)

        self.preset_mode_changed()
        self.sender().setExplodeDistanceFactor(0.06 if state else 0.03)

        self.hovered = self.sender() if state else None
    def get_slice_color(self, index: int) -> bytes:
        """Returns bytes the slice at index"""
        color = self.series.slices()[index].color().name().strip("#")
        return bytes.fromhex(color)
    def set_slice_border_color(self, slice: QtChart.QPieSlice, mode: QtGui.QColor = _SLICE_BORDER['disable']):
            """Set the slice border"""
            slice.setBorderColor(mode)
    
    def color_dialog_changed(self, value):
        if self.picked != None:
            if isinstance(self.picked, QtWidgets.QLabel):
                palette = QtGui.QPalette()
                palette.setColor(self.ui.labelLogo.foregroundRole(), value)
                self.ui.labelLogo.setPalette(palette)
            else:
                self.picked.setColor(value)
    def color_dialog_init(self):
        #FIXME: need to find a way to prevent the qdialog from disappearing when the user presses esc key
        self.colorDialog = QtWidgets.QColorDialog()
        self.colorDialog.setOptions(QtWidgets.QColorDialog.NoButtons)
        self.colorDialog.currentColorChanged.connect(self.color_dialog_changed)
        window = self.ui.mdiArea.addSubWindow(self.colorDialog, flags=QtCore.Qt.FramelessWindowHint)
        window.showMaximized()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.picked = self.ui.labelLogo
        self.ring_init()
        self.color_dialog_init()
        self.update_menu_device_list()

        self.ui.comboBoxPresetModes.currentTextChanged.connect(self.preset_mode_changed)
        self.ui.pushButtonSave.clicked.connect(self.preset_save_clicked)
        self.ui.actionReload.triggered.connect(self.update_menu_device_list)
        self.ui.labelLogo.mousePressEvent = self.led_logo_clicked
        self.ui.radioButtonPresetLogo.clicked.connect(self.led_mode_logo_changed)
        self.ui.radioButtonPresetRing.clicked.connect(self.led_mode_ring_changed)
        self.ui.radioButtonPresetBoth.clicked.connect(self.led_mode_both_changed)
        self.ui.horizontalSliderASpeed.valueChanged.connect(self.preset_speed_changed)

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
