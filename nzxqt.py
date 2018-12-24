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
    'picked'  : QtGui.QPalette().color(QtGui.QPalette.HighlightedText)
}

def find_all_supported_devices():
    res = map(lambda driver: driver.find_supported_devices(), DRIVERS)
    return itertools.chain(*res)

class MainWindow(QtWidgets.QMainWindow):

    def menu_file_save(self):
        self.light_device_store(True)

    def menu_device_reload(self):
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
            action.triggered.connect(self.menu_device_selected)

            self.ui.menu_Select_Device.addAction(action)

            if ((last_device == None) or (last_device.device.serial_number == dev.device.serial_number)):
                self.device = dev

        self.light_device_selected()
    def menu_device_selected(self):
        """Activates device menu item when clicked"""
        for i, dev in self.devices:
            if (dev.device.serial_number == self.sender().objectName()):
                self.device = dev
                break

        self.light_device_selected()

    def light_preset_validate_all(self):
        pass
    def light_preset_highlight_valid_slices(self):
        """Highlights ring segments and radiobuttons that are valid for the preset"""
        mode = self.ui.comboBoxPresetModes.currentText().lower()
        if mode == '':
            mode = self.ui.labelRingMode.text().lower()
            if mode == '':
                return

        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]
        
        if (ringonly):
            self.ui.radioButtonPresetRing.setChecked(True)
            if (self.picked == self.ui.labelLogo):
                self.picked = self.series.slices()[0]
            
        for i, ps in enumerate(self.series.slices()):
            ps.setBorderColor(_SLICE_BORDER['enable'])

        for i, ps in enumerate(self.series.slices()):
            if i == maxcolors:
                break
            ps.setBorderColor(_SLICE_BORDER['disable'])
        
        if isinstance(self.picked, QtChart.QPieSlice):
            self.picked.setBorderColor(_SLICE_BORDER['picked'])
        
        font = self.ui.labelLogo.font()
        font.setUnderline(self.picked == self.ui.labelLogo)
        self.ui.labelLogo.setFont(font)

    def update_animation_speed_label(self, value: str):
        """Updates animation speed information"""
        speed = self.get_animation_speed_name(value)
        self.ui.labelPresetAniSpeedLabel.setText("Animation Speed: %s" % speed.title())
    def get_animation_speed_name(self, value):
        for key, i in self.device.get_animation_speeds().items():
            if (value == i):
                return key

    def light_device_selected(self):
        """Updates the interface when a device has been selected"""
        for item in self.ui.menu_Select_Device.children():
            if isinstance(item, QtWidgets.QAction):
                item.setChecked((self.device.device.serial_number == item.objectName()))

        self.ui.comboBoxPresetModes.clear()

        for mode in self.device.get_color_modes():
            self.ui.comboBoxPresetModes.addItem(str(mode).title())

        self.ui.labelDevDeviceName.setText("Device: %s" % self.device.description)
        self.ui.labelDevSerialNo.setText("Serial No: %s" % self.device.device.serial_number)

        self.light_preset_highlight_valid_slices()          
    def get_logo_qcolor(self) -> QtGui.QColor:
        """Gets the logo QColor from its Palette"""
        return self.ui.labelLogo.palette().color(0)
    def light_logo_clicked(self, evt: QtGui.QMouseEvent):
        """Set color change target to logo"""
        self.ui.radioButtonPresetLogo.click()
    def light_both_mode_restore(self):
        """Reselects both preset when radiobutton is activated"""
        self.set_light_values(self.logo_settings)
        self.set_light_values(self.ring_settings)
    def light_logo_mode_restore(self):
        """Reselects logo preset when radiobutton is activated"""
        self.set_light_values(self.logo_settings)
    def light_ring_mode_restore(self):
        """Reselects ring preset when radiobutton is activated"""
        self.set_light_values(self.ring_settings)

    def set_light_picked(self, widget):
        self.picked = widget
    def get_last_color(self):
        if (not hasattr(self, 'last_color')):
            if (not hasattr(self, 'picked')):
                self.picked = self.series.slices()[0]
            self.last_color = self.picked.color()
        
        return self.last_color

    def light_chart_init(self):
        """Adds a ring widget as a QChart"""
        self.chart = QtChart.QChart()
        self.chart.setBackgroundRoundness(5)
        self.chart.legend().hide()
        self.chart.setBackgroundVisible(visible=True)
        self.chart.setDropShadowEnabled(enabled=False)
        self.chart.setMinimumHeight(180)
        self.chart.setMargins(QtCore.QMargins(0,0,0,0))
        self.series = QtChart.QPieSeries()
        self.series.setObjectName('series')
        self.series.setUseOpenGL(enable=True)
        self.series.setHoleSize(0.58)
        self.series.setPieSize(0.75)

        test = self.ui.tab_2_1.palette().color(4)
        brush = QtGui.QBrush(test)
        self.chart.setBackgroundBrush(brush)

        for i in range(8):
            ps = QtChart.QPieSlice(str(i), 1)
            ps.setExploded(True)
            ps.setExplodeDistanceFactor(0.035)

            ps.clicked.connect(self.light_chart_slice_clicked)
            ps.hovered.connect(self.light_chart_slice_hovered)
            ps.doubleClicked.connect(self.light_chart_slice_dblclicked)

            self.series.append(ps)
        self.chart.addSeries(self.series)
        self.ui.frame.setChart(self.chart)
        self.ui.frame.setRenderHint(QtGui.QPainter.Antialiasing, True)
    def light_chart_slice_clicked(self):
        """Stores slice and sets color dialog color"""
        self.picked = self.sender()
        self.ui.radioButtonPresetRing.click()
        self.light_preset_highlight_valid_slices()
    def light_chart_slice_dblclicked(self):
        """Fills all slices with the same color"""
        for i, ps in enumerate(self.series.slices()):
            ps.setColor(self.last_color)
    def light_chart_slice_hovered(self, state):
        """Event when slice is hovered"""
        if state:
            self.last_color = self.sender().color()
            self.sender().setColor(self.last_color.lighter())
        else:
            self.sender().setColor(self.last_color)

        self.light_preset_highlight_valid_slices()
        self.sender().setExplodeDistanceFactor(0.06 if state else 0.03)

        self.hovered = self.sender() if state else None
    def get_slice_color(self, index: int) -> bytes:
        """Returns bytes the slice at index"""
        color = self.series.slices()[index].color().name().strip("#")
        return bytes.fromhex(color)
    
    def color_dialog_changed(self, value):
        """Updates color on selected element"""
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
    
    def set_light_values(self, values, outputToDevice = False):
        """ sets preset to the values after performing sanity checks, may also write to the device"""
        if (len(values) != 4) or (self.device == None):
            return

        channel, mode, colors, speed = values
        speeds = self.device.get_animation_speeds()
        modes = [self.ui.comboBoxPresetModes.itemText(i) for i in range(self.ui.comboBoxPresetModes.count())]
        mode = mode.title()

        if ((channel not in ['logo', 'ring']) 
        or (mode not in modes) 
        or (speed not in speeds)):
            return
        
        if (outputToDevice):
            for i, ps in enumerate(self.series.slices()):
                if (i >= (len(colors) - 1)):
                    break
                #try:
                ps.setColor(QtGui.QColor("#" + colors[i + 1].hex()))
                #except:
                #    pass

        if channel == 'logo':
            self.logo_settings = values
            self.ui.labelLogoMode.setText(mode)
            self.picked = self.ui.labelLogo
            self.colorDialog.setCurrentColor(self.get_logo_qcolor())
        elif channel == 'ring':
            self.ring_settings = values
            self.ui.labelRingMode.setText(mode)
            if (not isinstance(self.picked, QtChart.QPieSlice)):
                self.picked = self.series.slices()[0]
            self.colorDialog.setCurrentColor(self.get_last_color())
        else:
            # 'sync' mode should not occur here as the mode is set from radio buttons 
            pass

        self.ui.horizontalSliderASpeed.setValue(speeds[speed])
        index = self.ui.comboBoxPresetModes.findText(mode)

        if (index < 0) and ((mode == 'default')):
            index = 0

        self.ui.comboBoxPresetModes.setCurrentIndex(index)

        self.ui.labelBothMode.setText("Mixed-modes")

        if (self.ui.labelLogoMode.text() == self.ui.labelRingMode.text()):
            self.ui.labelBothMode.setText(mode)

        if channel == 'logo' or channel == 'sync':
            self.logo_settings = [channel, mode, colors, speed]
        elif channel == 'ring' or channel == 'sync':
            self.ring_settings = [channel, mode, colors, speed]

        if (outputToDevice):
            print("mode = %s" % values)
            self.device.set_color(channel, mode.lower(), colors, speed)

        self.light_preset_highlight_valid_slices()

    def update_light_preset(self, preset):
        """update local preset values"""
        new_mode = self.ui.comboBoxPresetModes.currentText().lower()

        if (preset == self.logo_settings):
            mode = self.ui.labelLogoMode.text().lower()
            channel = 'logo'
        else:
            mode = self.ui.labelRingMode.text().lower()
            channel = 'ring'

        if (mode != new_mode):
            mode = new_mode

        mval, mod2, mod4, mincolors, maxcolors, ringonly = self.device.get_color_modes()[mode]
        colors = [self.get_slice_color(0) if ringonly else bytes.fromhex(self.get_logo_qcolor().name().strip("#"))]
        speed = self.get_animation_speed_name(self.ui.horizontalSliderASpeed.value())

        if (maxcolors > 0):
            for i, ps in enumerate(self.series.slices()):
                if (ringonly and i==0):
                    continue
                if (len(colors) == maxcolors):
                    break
                colors.append(self.get_slice_color(i))
        else:
            colors = []

        preset = [channel, mode, colors, speed]
        self.set_light_values(preset, True)

    def light_preset_save_button_clicked(self):
        """update local preset values and write to the device"""
        if (self.ui.radioButtonPresetLogo.isChecked() or self.ui.radioButtonPresetBoth.isChecked()):
            self.update_light_preset(self.logo_settings)

        if (self.ui.radioButtonPresetRing.isChecked() or self.ui.radioButtonPresetBoth.isChecked()):
            self.update_light_preset(self.ring_settings)

    def settings_load(self, file = 'config.json'):
        #PLACEHOLDER: will load last stored values here
        self.logo_settings = ['logo', 'Fixed', [b'\xef\xf0\xf1'], 'slowest']
        self.ring_settings = ['ring', 'Spectrum-Wave', [], 'normal']
        self.ring_settings = ['ring', 'super-fixed', [b'\xef\xf0\xf1', b'\xff\x00\x00', b'\xffU\x00', b'\xff\xff\x00', b'\x00\xff\x00', b'\x00\x80\xff', b'\x00\x00\xff', b'\xff\x00\x7f', b'\xff\x00\xff'], 'normal']

        self.set_light_values(self.logo_settings, True)
        self.set_light_values(self.ring_settings, True)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.picked = self.ui.labelLogo
        self.light_chart_init()
        self.color_dialog_init()
        self.menu_device_reload()

        self.ui.comboBoxPresetModes.currentTextChanged.connect(self.light_preset_highlight_valid_slices)
        self.ui.pushButtonSave.clicked.connect(self.light_preset_save_button_clicked)
        self.ui.labelLogo.mousePressEvent = self.light_logo_clicked
        self.ui.radioButtonPresetLogo.clicked.connect(self.light_logo_mode_restore)
        self.ui.radioButtonPresetRing.clicked.connect(self.light_ring_mode_restore)
        self.ui.radioButtonPresetBoth.clicked.connect(self.light_both_mode_restore)
        self.ui.horizontalSliderASpeed.valueChanged.connect(self.update_animation_speed_label)

        self.ui.actionSave.triggered.connect(self.menu_file_save)
        self.ui.actionReload.triggered.connect(self.menu_device_reload)
        #self.ui.actionNew.triggered.connect(self.menu_action_new)
        self.ui.actionExit.triggered.connect(quit)

        self.settings_load()

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
