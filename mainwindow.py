# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/wepiha/Documents/liquidctl-qt/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(822, 782)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabCooling = QtWidgets.QWidget()
        self.tabCooling.setObjectName("tabCooling")
        self.widget = QtWidgets.QWidget(self.tabCooling)
        self.widget.setGeometry(QtCore.QRect(153, 13, 466, 241))
        self.widget.setStyleSheet("background-color: black")
        self.widget.setObjectName("widget")
        self.widget_2 = QtWidgets.QWidget(self.tabCooling)
        self.widget_2.setGeometry(QtCore.QRect(155, 279, 463, 247))
        self.widget_2.setStyleSheet("background-color: black")
        self.widget_2.setObjectName("widget_2")
        self.tabWidget.addTab(self.tabCooling, "")
        self.tabLighting = QtWidgets.QWidget()
        self.tabLighting.setObjectName("tabLighting")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tabLighting)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.frame = QtChart.QChartView(self.tabLighting)
        self.frame.setMinimumSize(QtCore.QSize(180, 180))
        self.frame.setMaximumSize(QtCore.QSize(180, 180))
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet("background-color: #1e1e1e")
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.labelLogo = QtWidgets.QLabel(self.frame)
        self.labelLogo.setGeometry(QtCore.QRect(54, 74, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.labelLogo.setFont(font)
        self.labelLogo.setAlignment(QtCore.Qt.AlignCenter)
        self.labelLogo.setObjectName("labelLogo")
        self.gridLayout_4.addWidget(self.frame, 0, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.tabLighting)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBoxLogoLed = QtWidgets.QCheckBox(self.tabLighting)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkBoxLogoLed.setFont(font)
        self.checkBoxLogoLed.setObjectName("checkBoxLogoLed")
        self.gridLayout_2.addWidget(self.checkBoxLogoLed, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tabLighting)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 1, 1, 1)
        self.checkBoxRingLed = QtWidgets.QCheckBox(self.tabLighting)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkBoxRingLed.setFont(font)
        self.checkBoxRingLed.setObjectName("checkBoxRingLed")
        self.gridLayout_2.addWidget(self.checkBoxRingLed, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.tabLighting)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)
        self.pushButtonSave = QtWidgets.QPushButton(self.tabLighting)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.gridLayout_4.addWidget(self.pushButtonSave, 2, 0, 1, 1)
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tabLighting)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_2_1 = QtWidgets.QWidget()
        self.tab_2_1.setObjectName("tab_2_1")
        self.mdiArea = QtWidgets.QMdiArea(self.tab_2_1)
        self.mdiArea.setGeometry(QtCore.QRect(193, 6, 582, 397))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mdiArea.sizePolicy().hasHeightForWidth())
        self.mdiArea.setSizePolicy(sizePolicy)
        self.mdiArea.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.mdiArea.setObjectName("mdiArea")
        self.layoutWidget = QtWidgets.QWidget(self.tab_2_1)
        self.layoutWidget.setGeometry(QtCore.QRect(6, 6, 182, 178))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.comboBoxPresetModes = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBoxPresetModes.setObjectName("comboBoxPresetModes")
        self.verticalLayout_2.addWidget(self.comboBoxPresetModes)
        self.labelPresetModeInfo = QtWidgets.QLabel(self.layoutWidget)
        self.labelPresetModeInfo.setObjectName("labelPresetModeInfo")
        self.verticalLayout_2.addWidget(self.labelPresetModeInfo)
        self.labelPresetAniSpeedLabel = QtWidgets.QLabel(self.layoutWidget)
        self.labelPresetAniSpeedLabel.setMinimumSize(QtCore.QSize(180, 0))
        self.labelPresetAniSpeedLabel.setObjectName("labelPresetAniSpeedLabel")
        self.verticalLayout_2.addWidget(self.labelPresetAniSpeedLabel)
        self.horizontalSliderASpeed = QtWidgets.QSlider(self.layoutWidget)
        self.horizontalSliderASpeed.setMinimum(0)
        self.horizontalSliderASpeed.setMaximum(4)
        self.horizontalSliderASpeed.setPageStep(1)
        self.horizontalSliderASpeed.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSliderASpeed.setObjectName("horizontalSliderASpeed")
        self.verticalLayout_2.addWidget(self.horizontalSliderASpeed)
        self.labelPresetAniSpeedInfo = QtWidgets.QLabel(self.layoutWidget)
        self.labelPresetAniSpeedInfo.setObjectName("labelPresetAniSpeedInfo")
        self.verticalLayout_2.addWidget(self.labelPresetAniSpeedInfo)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.tabWidget_2.addTab(self.tab_2_1, "")
        self.tab_2_2 = QtWidgets.QWidget()
        self.tab_2_2.setObjectName("tab_2_2")
        self.tabWidget_2.addTab(self.tab_2_2, "")
        self.gridLayout_4.addWidget(self.tabWidget_2, 1, 0, 1, 2)
        self.tabWidget.addTab(self.tabLighting, "")
        self.tabOverclock = QtWidgets.QWidget()
        self.tabOverclock.setObjectName("tabOverclock")
        self.tabWidget.addTab(self.tabOverclock, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 822, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuDevice = QtWidgets.QMenu(self.menubar)
        self.menuDevice.setObjectName("menuDevice")
        self.menu_Select_Device = QtWidgets.QMenu(self.menuDevice)
        self.menu_Select_Device.setObjectName("menu_Select_Device")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionReload = QtWidgets.QAction(MainWindow)
        self.actionReload.setObjectName("actionReload")
        self.actiondummy = QtWidgets.QAction(MainWindow)
        self.actiondummy.setObjectName("actiondummy")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionReset = QtWidgets.QAction(MainWindow)
        self.actionReset.setObjectName("actionReset")
        self.actionExit_2 = QtWidgets.QAction(MainWindow)
        self.actionExit_2.setObjectName("actionExit_2")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionReset)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit_2)
        self.menu_Select_Device.addAction(self.actiondummy)
        self.menuDevice.addAction(self.menu_Select_Device.menuAction())
        self.menuDevice.addAction(self.actionReload)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevice.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCooling), _translate("MainWindow", "Cooling"))
        self.labelLogo.setText(_translate("MainWindow", "NZXT"))
        self.label.setText(_translate("MainWindow", "Select the LED you want to edit:"))
        self.checkBoxLogoLed.setText(_translate("MainWindow", "LOGO LED"))
        self.label_2.setText(_translate("MainWindow", "FIXED - Default"))
        self.checkBoxRingLed.setText(_translate("MainWindow", "RING LED"))
        self.label_3.setText(_translate("MainWindow", "FIXED - Default"))
        self.pushButtonSave.setText(_translate("MainWindow", "SAVE CHANGES"))
        self.labelPresetModeInfo.setText(_translate("MainWindow", "TextLabel"))
        self.labelPresetAniSpeedLabel.setText(_translate("MainWindow", "Animation Speed:"))
        self.labelPresetAniSpeedInfo.setText(_translate("MainWindow", "TextLabel"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2_1), _translate("MainWindow", "Preset"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2_2), _translate("MainWindow", "Smart"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLighting), _translate("MainWindow", "Lighting"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabOverclock), _translate("MainWindow", "Overclocking"))
        self.menuFile.setTitle(_translate("MainWindow", "Fi&le"))
        self.menuDevice.setTitle(_translate("MainWindow", "&Device"))
        self.menu_Select_Device.setTitle(_translate("MainWindow", "&Select Device:"))
        self.actionExit.setText(_translate("MainWindow", "&Exit"))
        self.actionReload.setText(_translate("MainWindow", "&Refresh Devices"))
        self.actiondummy.setText(_translate("MainWindow", "&dummy"))
        self.actionSave.setText(_translate("MainWindow", "&Save"))
        self.actionSave_As.setText(_translate("MainWindow", "Sa&ve As..."))
        self.actionOpen.setText(_translate("MainWindow", "&Open..."))
        self.actionNew.setText(_translate("MainWindow", "&New Profile"))
        self.actionReset.setText(_translate("MainWindow", "&Reset"))
        self.actionExit_2.setText(_translate("MainWindow", "&Exit"))

from PyQt5 import QtChart
