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

class Preset(QtCore.QObject):
    from PyQt5.QtCore import pyqtSignal

    def __init__(self, device: liquidctl.driver.base_usb, channel = 'sync', mode = 'Off', colors = [], speed = 'slowest'):
        super().__init__()
        self._device = device
        self._modes = device.get_color_modes()
        self._speeds = device.get_animation_speeds()
        self.values = [channel, mode, colors, speed]

    changed = pyqtSignal(str)

    def write(self):
        self.device.set_color(self._channel, self._mode, self._colors, self._speed)

    @property
    def device(self):
        return self._device

    @property
    def values(self):
        return [self._channel, self._mode, self._colors, self._speed]
    @values.setter
    def values(self, value):
        channel, mode, colors, speed = value

        if hasattr(self, '_channel'):
            pass
        self._channel = channel
        self._mode = 'Off'
        self._colors = []
        self._speed = 'slowest'
        self.mode = mode
        self.colors = colors
        self.speed = speed
        pass

    @property
    def channel(self):
        return self._channel
        
    @property
    def mode(self):
        return self._mode
    @mode.setter
    def mode(self, value):
        value = value.lower()
        if (value not in self._modes):
            raise AttributeError("The device does not support the mode value '%s'" % value)
        old_value = self._mode
        self._mode = value
        if (value != old_value):
            self.changed.emit('mode')
    @property
    def colors(self):
        return self._colors
    @colors.setter
    def colors(self, values):
        old_value = self._colors
        self._colors = values
        if (values != old_value):
            self.changed.emit('colors')

    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, value):
        if (value not in self._speeds):
            raise AttributeError("The device does not support the speed value '%s'" % value)
        old_value = self._speed
        self._speed = value
        if (value != old_value):
            self.changed.emit('speed')
    
def find_all_supported_devices():
    res = map(lambda driver: driver.find_supported_devices(), DRIVERS)
    return itertools.chain(*res)

class MainWindow(QtWidgets.QMainWindow):

    def menu_file_save(self):
        pass

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
    def preset_save(self, outputToFile = False):
        """saves values to preset based on currenly selected channel"""
        if (self.device == None ):
            return

        # useful for saving when BOTH channel is selected
        mode = self.ui.comboBoxPresetModes.currentText().lower()
        both = self.ui.radioButtonPresetBoth.isChecked()

        if (self.ui.radioButtonPresetLogo.isChecked() or both):
            self.update_preset_from_ui(self.logo_preset, mode)

        if (self.ui.radioButtonPresetRing.isChecked() or both):
            self.update_preset_from_ui(self.ring_preset, mode)
        
        if (both):
            self.update_preset_from_ui(self.both_preset, mode)

        if (not outputToFile):
            self.logo_preset.write()
            self.ring_preset.write()
    
    def get_logo_qcolor(self) -> QtGui.QColor:
        """Gets the logo QColor from its Palette"""
        return self.ui.labelLogo.palette().color(0)
    def light_logo_clicked(self, evt: QtGui.QMouseEvent):
        """Set color change target to logo"""
        self.ui.radioButtonPresetLogo.click()
    def both_selected(self):
        """Reselects both preset when radiobutton is activated"""
        self.update_ui_from_preset(self.both_preset)
        self.light_preset_highlight_valid_slices()
    def logo_selected(self, data):
        """Reselects logo preset when radiobutton is activated"""
        self.picked = self.ui.labelLogo

        self.colorDialog.setCurrentColor(self.get_logo_qcolor())
        self.update_ui_from_preset(self.logo_preset)
        self.light_preset_highlight_valid_slices()
    def ring_selected(self):
        """Reselects ring preset when radiobutton is activated"""
        if (not isinstance(self.picked, QtChart.QPieSlice)):
            self.picked = self.series.slices()[0]
        
        if (not hasattr(self, 'last_color')):
            self.last_color = self.picked.color()
        self.colorDialog.setCurrentColor(self.last_color)
        self.update_ui_from_preset(self.ring_preset)
        self.light_preset_highlight_valid_slices()

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
    
    def update_preset_from_ui(self, preset: Preset, mode):
        """stores light settings based on current ui values and returns a preset"""
        preset.mode = mode
        colors = [bytes.fromhex(self.get_logo_qcolor().name().strip("#"))]

        for i, ps in enumerate(self.series.slices()):
            colors.append(self.get_slice_color(i))

        preset.colors = colors
        preset.speed = self.get_animation_speed_name(self.ui.horizontalSliderASpeed.value())

        if (preset.channel == 'sync'):
            self.update_preset_from_ui(self.logo_preset, mode)
            self.update_preset_from_ui(self.ring_preset, mode)
    def update_ui_from_preset(self, data: Preset):
        """ updates ui values for the given preset data """
        if (data == None):
            raise AttributeError("Cannot update from None Preset")

        if (data.channel == 'logo'):
            preset = self.logo_preset
            label = self.ui.labelLogoMode
        elif (data.channel == 'ring'):
            preset = self.ring_preset
            label = self.ui.labelRingMode
        else:
            preset = self.both_preset
            label = self.ui.labelBothMode

        modes = [self.ui.comboBoxPresetModes.itemText(i) for i in range(self.ui.comboBoxPresetModes.count())]
        speeds = preset.device.get_animation_speeds()
        mode = preset.mode.title()

        if ((preset.channel not in ['logo', 'ring', 'sync']) 
        or (mode not in modes)
        or (preset.speed not in speeds)):
            return

        for i, ps in enumerate(self.series.slices()):
            if (i >= (len(preset.colors) - 1)):
                break
            ps.setColor(QtGui.QColor("#" + preset.colors[i + 1].hex()))

        self.ui.horizontalSliderASpeed.setValue(speeds[preset.speed])
        self.ui.comboBoxPresetModes.setCurrentText(mode)

        if (preset.channel in ['logo', 'ring', 'sync']):
            label.setText(mode)
            
        if (self.ui.labelLogoMode.text() != self.ui.labelRingMode.text()):
            self.ui.labelBothMode.setText("Mixed-modes")

        self.light_preset_highlight_valid_slices()

    def settings_load(self, file = 'config.json'):
        self.logo_preset = Preset(self.device, 'logo')
        self.ring_preset = Preset(self.device, 'ring')
        self.both_preset = Preset(self.device)
        
        self.logo_preset.changed.connect(self.logo_changed)
        self.ring_preset.changed.connect(self.ring_changed)
        self.both_preset.changed.connect(self.both_changed)

        self.logo_preset.values = ['logo', 'Fixed', [b'\xef\xf0\xf1'], 'slower']
        self.ring_preset.values = ['ring', 'super-fixed', [b'\xef\xf0\xf1', b'\xff\x00\x00', b'\xffU\x00', b'\xff\xff\x00', b'\x00\xff\x00', b'\x00\x80\xff', b'\x00\x00\xff', b'\xff\x00\x7f', b'\xff\x00\xff'], 'normal']
        
        self.logo_preset.write()
        self.ring_preset.write()

        self.update_ui_from_preset(self.both_preset)

    def ring_changed(self, param):
        #print("ring %s changed" % param)
        self.update_ui_from_preset(self.ring_preset)

    def logo_changed(self, param):
        #print("logo %s changed" % param)
        self.update_ui_from_preset(self.logo_preset)
    
    def both_changed(self, param):
        #print("both %s changed" % param)
        self.update_ui_from_preset(self.both_preset)


    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.picked = self.ui.labelLogo
        self.light_chart_init()
        self.color_dialog_init()
        self.menu_device_reload()

        self.ui.comboBoxPresetModes.currentTextChanged.connect(self.light_preset_highlight_valid_slices)
        self.ui.pushButtonSave.clicked.connect(self.preset_save)
        self.ui.labelLogo.mousePressEvent = self.logo_selected #self.light_logo_clicked
        self.ui.radioButtonPresetLogo.clicked.connect(self.logo_selected)
        self.ui.radioButtonPresetRing.clicked.connect(self.ring_selected)
        self.ui.radioButtonPresetBoth.clicked.connect(self.both_selected)
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
