# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\SettingsMenu.ui'
#
# Created by: PyQt6 UI code generator 6.7.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SettingsMenu(object):
    def setupUi(self, SettingsMenu):
        SettingsMenu.setObjectName("SettingsMenu")
        SettingsMenu.resize(538, 376)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(SettingsMenu)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.backBtn = QtWidgets.QPushButton(parent=SettingsMenu)
        self.backBtn.setObjectName("backBtn")
        self.horizontalLayout.addWidget(self.backBtn)
        self.mainTitle = QtWidgets.QLabel(parent=SettingsMenu)
        self.mainTitle.setText("Scrape Settings")
        self.mainTitle.setObjectName("mainTitle")
        self.horizontalLayout.addWidget(self.mainTitle)
        spacerItem = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(parent=SettingsMenu)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_4.addWidget(self.line)
        self.gridWidget = QtWidgets.QWidget(parent=SettingsMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gridWidget.sizePolicy().hasHeightForWidth())
        self.gridWidget.setSizePolicy(sizePolicy)
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalWidget_2 = QtWidgets.QWidget(parent=self.gridWidget)
        self.verticalWidget_2.setObjectName("verticalWidget_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalWidget_2)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.verticalWidget_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label.setObjectName("label")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label
        )
        self.minRateSpinBox = QtWidgets.QDoubleSpinBox(parent=self.groupBox_2)
        self.minRateSpinBox.setDecimals(2)
        self.minRateSpinBox.setSingleStep(0.05)
        self.minRateSpinBox.setObjectName("minRateSpinBox")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.minRateSpinBox
        )
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2
        )
        self.maxRateSpinBox = QtWidgets.QDoubleSpinBox(parent=self.groupBox_2)
        self.maxRateSpinBox.setDecimals(2)
        self.maxRateSpinBox.setSingleStep(0.05)
        self.maxRateSpinBox.setObjectName("maxRateSpinBox")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.maxRateSpinBox
        )
        self.timeoutLabel = QtWidgets.QLabel(parent=self.groupBox_2)
        self.timeoutLabel.setObjectName("timeoutLabel")
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.timeoutLabel
        )
        self.timeoutSpinBox = QtWidgets.QDoubleSpinBox(parent=self.groupBox_2)
        self.timeoutSpinBox.setDecimals(2)
        self.timeoutSpinBox.setSingleStep(0.5)
        self.timeoutSpinBox.setObjectName("timeoutSpinBox")
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.timeoutSpinBox
        )
        self.verticalLayout_5.addWidget(self.groupBox_2)
        self.gridLayout.addWidget(
            self.verticalWidget_2, 1, 0, 1, 1, QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.verticalWidget = QtWidgets.QWidget(parent=self.gridWidget)
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(parent=self.verticalWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.debugCheckbox = QtWidgets.QCheckBox(parent=self.groupBox)
        self.debugCheckbox.setChecked(True)
        self.debugCheckbox.setObjectName("debugCheckbox")
        self.verticalLayout_2.addWidget(self.debugCheckbox)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.gridLayout.addWidget(
            self.verticalWidget, 1, 1, 1, 1, QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.verticalLayout_4.addWidget(self.gridWidget)

        self.retranslateUi(SettingsMenu)
        QtCore.QMetaObject.connectSlotsByName(SettingsMenu)

    def retranslateUi(self, SettingsMenu):
        _translate = QtCore.QCoreApplication.translate
        SettingsMenu.setWindowTitle(_translate("SettingsMenu", "Form"))
        self.backBtn.setText(_translate("SettingsMenu", "Back"))
        self.groupBox_2.setTitle(_translate("SettingsMenu", "Request Handler Settings"))
        self.label.setText(_translate("SettingsMenu", "Min Rate Limit"))
        self.minRateSpinBox.setSuffix(_translate("SettingsMenu", "s"))
        self.label_2.setText(_translate("SettingsMenu", "Max Rate Limit"))
        self.maxRateSpinBox.setSuffix(_translate("SettingsMenu", "s"))
        self.timeoutLabel.setText(_translate("SettingsMenu", "Timeout"))
        self.timeoutSpinBox.setSuffix(_translate("SettingsMenu", "s"))
        self.groupBox.setTitle(_translate("SettingsMenu", "Logger Settings"))
        self.debugCheckbox.setText(_translate("SettingsMenu", "Debug Mode"))
