# -*- coding: utf-8 -*-
from liquidctl.driver.base_usb import BaseUsbDriver

from PyQt5 import *
from PyQt5.QtCore import pyqtSignal

class DeviceLightingPreset(QtCore.QObject):
    """
    Stores values that can be sent to a device, and provides PyQt5 signals when values change

    Keyword arguments::
    `device` -- must be an instance of `BaseUsbDriver`\n
    `channel` -- the channel that preset will manage, must be either `sync`, `ring`, or `logo` (default: `'sync'`)\n
    `mode` -- lighting mode, must be in `device.get_color_modes()`\n
    `speed` -- the animation speed, must be in `device.get_animation_speeds()`
    """

    changed = pyqtSignal(str)

    def __init__(self, device: BaseUsbDriver, channel = 'sync', mode = 'fixed', colors = [], speed = 'normal'):
        super().__init__()
        self.__channel = channel
        self.__device = device
        self.__modes = device.get_color_modes()
        self.__speeds = device.get_animation_speeds()
        self.values = [channel, mode, colors, speed]

    def write(self):
        """ write to the device specific BaseUsbDriver  """
        # get the maxiumum colors supported by the mode
        maxcolors = self.device.get_color_modes()[self.__mode][4]


        strip_colors = [i.strip("#") for i in self.colors[0:maxcolors]]
        # convert back to bytes
        byte_colors = list(map(bytes.fromhex, strip_colors))

        # write to the device
        self.device.set_color(self.__channel, self.__mode, byte_colors, self.__speed)

    @property
    def device(self):
        return self.__device

    @property
    def values(self):
        return [self.__channel, self.__mode, self.__colors, self.__speed]
    @values.setter
    def values(self, value):
        channel, mode, colors, speed = value

        #if (not hasattr(self, '__channel')):
        #    self.__channel = channel
        self.__mode = 'off'
        self.__colors = []
        self.__speed = 'normal'
        self.mode = mode
        self.colors = colors
        self.speed = speed

    def to_json(self):
        return {
            'mode': self.mode,
            'colors': self.colors,
            'speed': self.speed
        }

    @property
    def channel(self):
        return self.__channel
        
    @property
    def mode(self):
        return self.__mode
    @mode.setter
    def mode(self, value):
        value = value.lower()
        if (value not in self.__modes):
            raise AttributeError("The device does not support the mode value '%s'" % value)
        old_value = self.__mode
        self.__mode = value
        if (value != old_value):
            self.changed.emit('mode')
    @property
    def modes(self):
        return self.__modes

    @property
    def colors(self):
        """the array of hexidecimal colors for the channel"""
        if (self.__channel == 'logo'):
            return [self.__colors[0]]
        return self.__colors
    @colors.setter
    def colors(self, values):
        if (not isinstance(values, list)):
            return
        old_value = self.__colors
        self.__colors = values
        if (values != old_value):
            self.changed.emit('colors')

    @property
    def speed(self):
        return self.__speed
    @speed.setter
    def speed(self, value):
        if (value not in self.__speeds):
            raise AttributeError("The device does not support the speed value '%s'" % value)
        old_value = self.__speed
        self.__speed = value
        if (value != old_value):
            self.changed.emit('speed')
    
    @property
    def speeds(self):
        return self.__speeds

    