# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\ScrapeMenu.ui'
#
# Created by: PyQt6 UI code generator 6.7.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ScrapeMenu(object):
    def setupUi(self, ScrapeMenu):
        ScrapeMenu.setObjectName("ScrapeMenu")
        ScrapeMenu.resize(586, 391)
        self.verticalLayout = QtWidgets.QVBoxLayout(ScrapeMenu)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.backBtn = QtWidgets.QPushButton(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.backBtn.sizePolicy().hasHeightForWidth())
        self.backBtn.setSizePolicy(sizePolicy)
        self.backBtn.setObjectName("backBtn")
        self.horizontalLayout.addWidget(self.backBtn)
        self.mainTitle = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainTitle.sizePolicy().hasHeightForWidth())
        self.mainTitle.setSizePolicy(sizePolicy)
        self.mainTitle.setObjectName("mainTitle")
        self.horizontalLayout.addWidget(self.mainTitle)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabWidget = QtWidgets.QTabWidget(parent=ScrapeMenu)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.damageBox = QtWidgets.QGroupBox(parent=self.tab)
        self.damageBox.setObjectName("damageBox")
        self.formLayout = QtWidgets.QFormLayout(self.damageBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(parent=self.damageBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.pDmgCombo = QtWidgets.QComboBox(parent=self.damageBox)
        self.pDmgCombo.setEditable(False)
        self.pDmgCombo.setObjectName("pDmgCombo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pDmgCombo)
        self.label_2 = QtWidgets.QLabel(parent=self.damageBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.sDmgCombo = QtWidgets.QComboBox(parent=self.damageBox)
        self.sDmgCombo.setEditable(False)
        self.sDmgCombo.setObjectName("sDmgCombo")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sDmgCombo)
        self.gridLayout_2.addWidget(self.damageBox, 1, 0, 1, 1)
        self.vehicleBox = QtWidgets.QGroupBox(parent=self.tab)
        self.vehicleBox.setObjectName("vehicleBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.vehicleBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.makeLabel = QtWidgets.QLabel(parent=self.vehicleBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.makeLabel.sizePolicy().hasHeightForWidth())
        self.makeLabel.setSizePolicy(sizePolicy)
        self.makeLabel.setObjectName("makeLabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.makeLabel)
        self.makeCombo = QtWidgets.QComboBox(parent=self.vehicleBox)
        self.makeCombo.setMinimumSize(QtCore.QSize(200, 0))
        self.makeCombo.setEditable(True)
        self.makeCombo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.makeCombo.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.makeCombo.setObjectName("makeCombo")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.makeCombo)
        self.modelLabel = QtWidgets.QLabel(parent=self.vehicleBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modelLabel.sizePolicy().hasHeightForWidth())
        self.modelLabel.setSizePolicy(sizePolicy)
        self.modelLabel.setObjectName("modelLabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.modelLabel)
        self.modelCombo = QtWidgets.QComboBox(parent=self.vehicleBox)
        self.modelCombo.setEditable(True)
        self.modelCombo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.modelCombo.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.modelCombo.setObjectName("modelCombo")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.modelCombo)
        self.gridLayout_2.addWidget(self.vehicleBox, 0, 0, 1, 1)
        self.yearsBox = QtWidgets.QGroupBox(parent=self.tab)
        self.yearsBox.setObjectName("yearsBox")
        self.formLayout_3 = QtWidgets.QFormLayout(self.yearsBox)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_6 = QtWidgets.QLabel(parent=self.yearsBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_6)
        self.startYearCombo = QtWidgets.QComboBox(parent=self.yearsBox)
        self.startYearCombo.setEditable(False)
        self.startYearCombo.setObjectName("startYearCombo")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.startYearCombo)
        self.label_7 = QtWidgets.QLabel(parent=self.yearsBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_7)
        self.endYearCombo = QtWidgets.QComboBox(parent=self.yearsBox)
        self.endYearCombo.setEditable(False)
        self.endYearCombo.setObjectName("endYearCombo")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.endYearCombo)
        self.gridLayout_2.addWidget(self.yearsBox, 0, 1, 1, 1)
        self.deltaVBox = QtWidgets.QGroupBox(parent=self.tab)
        self.deltaVBox.setObjectName("deltaVBox")
        self.formLayout_4 = QtWidgets.QFormLayout(self.deltaVBox)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_4 = QtWidgets.QLabel(parent=self.deltaVBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_4)
        self.dvMinSpin = QtWidgets.QSpinBox(parent=self.deltaVBox)
        self.dvMinSpin.setMaximum(999999999)
        self.dvMinSpin.setObjectName("dvMinSpin")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dvMinSpin)
        self.label_8 = QtWidgets.QLabel(parent=self.deltaVBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_8)
        self.dvMaxSpin = QtWidgets.QSpinBox(parent=self.deltaVBox)
        self.dvMaxSpin.setMaximum(999999999)
        self.dvMaxSpin.setObjectName("dvMaxSpin")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dvMaxSpin)
        self.gridLayout_2.addWidget(self.deltaVBox, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.vehicleBox_2 = QtWidgets.QGroupBox(parent=self.tab_2)
        self.vehicleBox_2.setObjectName("vehicleBox_2")
        self.formLayout_8 = QtWidgets.QFormLayout(self.vehicleBox_2)
        self.formLayout_8.setObjectName("formLayout_8")
        self.makeLabel_2 = QtWidgets.QLabel(parent=self.vehicleBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.makeLabel_2.sizePolicy().hasHeightForWidth())
        self.makeLabel_2.setSizePolicy(sizePolicy)
        self.makeLabel_2.setObjectName("makeLabel_2")
        self.formLayout_8.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.makeLabel_2)
        self.makeCombo_2 = QtWidgets.QComboBox(parent=self.vehicleBox_2)
        self.makeCombo_2.setMinimumSize(QtCore.QSize(200, 0))
        self.makeCombo_2.setEditable(True)
        self.makeCombo_2.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.makeCombo_2.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.makeCombo_2.setObjectName("makeCombo_2")
        self.formLayout_8.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.makeCombo_2)
        self.modelLabel_2 = QtWidgets.QLabel(parent=self.vehicleBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modelLabel_2.sizePolicy().hasHeightForWidth())
        self.modelLabel_2.setSizePolicy(sizePolicy)
        self.modelLabel_2.setObjectName("modelLabel_2")
        self.formLayout_8.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.modelLabel_2)
        self.modelCombo_2 = QtWidgets.QComboBox(parent=self.vehicleBox_2)
        self.modelCombo_2.setEditable(True)
        self.modelCombo_2.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.modelCombo_2.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.modelCombo_2.setObjectName("modelCombo_2")
        self.formLayout_8.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.modelCombo_2)
        self.gridLayout_3.addWidget(self.vehicleBox_2, 0, 0, 1, 1)
        self.yearsBox_2 = QtWidgets.QGroupBox(parent=self.tab_2)
        self.yearsBox_2.setObjectName("yearsBox_2")
        self.formLayout_6 = QtWidgets.QFormLayout(self.yearsBox_2)
        self.formLayout_6.setObjectName("formLayout_6")
        self.label_10 = QtWidgets.QLabel(parent=self.yearsBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setObjectName("label_10")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_10)
        self.startYearCombo_2 = QtWidgets.QComboBox(parent=self.yearsBox_2)
        self.startYearCombo_2.setEditable(False)
        self.startYearCombo_2.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.startYearCombo_2.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.startYearCombo_2.setObjectName("startYearCombo_2")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.startYearCombo_2)
        self.label_11 = QtWidgets.QLabel(parent=self.yearsBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setObjectName("label_11")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_11)
        self.endYearCombo_2 = QtWidgets.QComboBox(parent=self.yearsBox_2)
        self.endYearCombo_2.setEditable(False)
        self.endYearCombo_2.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.endYearCombo_2.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.endYearCombo_2.setObjectName("endYearCombo_2")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.endYearCombo_2)
        self.gridLayout_3.addWidget(self.yearsBox_2, 0, 1, 1, 1)
        self.damageBox_2 = QtWidgets.QGroupBox(parent=self.tab_2)
        self.damageBox_2.setObjectName("damageBox_2")
        self.formLayout_5 = QtWidgets.QFormLayout(self.damageBox_2)
        self.formLayout_5.setObjectName("formLayout_5")
        self.label_5 = QtWidgets.QLabel(parent=self.damageBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_5)
        self.pDmgCombo_2 = QtWidgets.QComboBox(parent=self.damageBox_2)
        self.pDmgCombo_2.setEditable(False)
        self.pDmgCombo_2.setObjectName("pDmgCombo_2")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pDmgCombo_2)
        self.label_9 = QtWidgets.QLabel(parent=self.damageBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setObjectName("label_9")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_9)
        self.sDmgCombo_2 = QtWidgets.QComboBox(parent=self.damageBox_2)
        self.sDmgCombo_2.setEditable(False)
        self.sDmgCombo_2.setObjectName("sDmgCombo_2")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sDmgCombo_2)
        self.gridLayout_3.addWidget(self.damageBox_2, 1, 0, 1, 1)
        self.deltaVBox_2 = QtWidgets.QGroupBox(parent=self.tab_2)
        self.deltaVBox_2.setObjectName("deltaVBox_2")
        self.formLayout_7 = QtWidgets.QFormLayout(self.deltaVBox_2)
        self.formLayout_7.setObjectName("formLayout_7")
        self.label_12 = QtWidgets.QLabel(parent=self.deltaVBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setObjectName("label_12")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_12)
        self.dvMinSpin_2 = QtWidgets.QSpinBox(parent=self.deltaVBox_2)
        self.dvMinSpin_2.setMaximum(999999999)
        self.dvMinSpin_2.setObjectName("dvMinSpin_2")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dvMinSpin_2)
        self.label_13 = QtWidgets.QLabel(parent=self.deltaVBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)
        self.label_13.setObjectName("label_13")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_13)
        self.dvMaxSpin_2 = QtWidgets.QSpinBox(parent=self.deltaVBox_2)
        self.dvMaxSpin_2.setMaximum(999999999)
        self.dvMaxSpin_2.setObjectName("dvMaxSpin_2")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dvMaxSpin_2)
        self.gridLayout_3.addWidget(self.deltaVBox_2, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.bottomHLayout = QtWidgets.QWidget(parent=ScrapeMenu)
        self.bottomHLayout.setObjectName("bottomHLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.bottomHLayout)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.multiCheckBox = QtWidgets.QCheckBox(parent=self.bottomHLayout)
        self.multiCheckBox.setObjectName("multiCheckBox")
        self.horizontalLayout_2.addWidget(self.multiCheckBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.label_3 = QtWidgets.QLabel(parent=self.bottomHLayout)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.nassRadioBtn = QtWidgets.QRadioButton(parent=self.bottomHLayout)
        self.nassRadioBtn.setEnabled(False)
        self.nassRadioBtn.setObjectName("nassRadioBtn")
        self.databaseBtnGroup = QtWidgets.QButtonGroup(ScrapeMenu)
        self.databaseBtnGroup.setObjectName("databaseBtnGroup")
        self.databaseBtnGroup.addButton(self.nassRadioBtn)
        self.horizontalLayout_2.addWidget(self.nassRadioBtn)
        self.cissRadioBtn = QtWidgets.QRadioButton(parent=self.bottomHLayout)
        self.cissRadioBtn.setEnabled(False)
        self.cissRadioBtn.setObjectName("cissRadioBtn")
        self.databaseBtnGroup.addButton(self.cissRadioBtn)
        self.horizontalLayout_2.addWidget(self.cissRadioBtn)
        self.stopBtn = QtWidgets.QPushButton(parent=self.bottomHLayout)
        self.stopBtn.setEnabled(True)
        self.stopBtn.setDefault(False)
        self.stopBtn.setObjectName("stopBtn")
        self.horizontalLayout_2.addWidget(self.stopBtn)
        self.submitBtn = QtWidgets.QPushButton(parent=self.bottomHLayout)
        self.submitBtn.setEnabled(False)
        self.submitBtn.setCheckable(False)
        self.submitBtn.setDefault(True)
        self.submitBtn.setObjectName("submitBtn")
        self.horizontalLayout_2.addWidget(self.submitBtn)
        self.verticalLayout.addWidget(self.bottomHLayout)

        self.retranslateUi(ScrapeMenu)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ScrapeMenu)

    def retranslateUi(self, ScrapeMenu):
        _translate = QtCore.QCoreApplication.translate
        ScrapeMenu.setWindowTitle(_translate("ScrapeMenu", "Form"))
        self.backBtn.setText(_translate("ScrapeMenu", "Back"))
        self.mainTitle.setText(_translate("ScrapeMenu", "New Scrape"))
        self.damageBox.setTitle(_translate("ScrapeMenu", "Damage Location"))
        self.label.setText(_translate("ScrapeMenu", "Primary:"))
        self.label_2.setText(_translate("ScrapeMenu", "Secondary:"))
        self.vehicleBox.setTitle(_translate("ScrapeMenu", "Vehicle"))
        self.makeLabel.setText(_translate("ScrapeMenu", "Make:"))
        self.modelLabel.setText(_translate("ScrapeMenu", "Model:"))
        self.yearsBox.setTitle(_translate("ScrapeMenu", "Model Years:"))
        self.label_6.setText(_translate("ScrapeMenu", "From"))
        self.label_7.setText(_translate("ScrapeMenu", "To"))
        self.deltaVBox.setTitle(_translate("ScrapeMenu", "Delta V (mph):"))
        self.label_4.setText(_translate("ScrapeMenu", "From"))
        self.label_8.setText(_translate("ScrapeMenu", "To"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ScrapeMenu", "NASS Params"))
        self.vehicleBox_2.setTitle(_translate("ScrapeMenu", "Vehicle"))
        self.makeLabel_2.setText(_translate("ScrapeMenu", "Make:"))
        self.modelLabel_2.setText(_translate("ScrapeMenu", "Model:"))
        self.yearsBox_2.setTitle(_translate("ScrapeMenu", "Model Years:"))
        self.label_10.setText(_translate("ScrapeMenu", "From"))
        self.label_11.setText(_translate("ScrapeMenu", "To"))
        self.damageBox_2.setTitle(_translate("ScrapeMenu", "Damage Location"))
        self.label_5.setText(_translate("ScrapeMenu", "Primary:"))
        self.label_9.setText(_translate("ScrapeMenu", "Secondary:"))
        self.deltaVBox_2.setTitle(_translate("ScrapeMenu", "Delta V (mph):"))
        self.label_12.setText(_translate("ScrapeMenu", "From"))
        self.label_13.setText(_translate("ScrapeMenu", "To"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ScrapeMenu", "CISS Params"))
        self.multiCheckBox.setText(_translate("ScrapeMenu", "Multi-analysis"))
        self.label_3.setText(_translate("ScrapeMenu", "Scrape from: "))
        self.nassRadioBtn.setText(_translate("ScrapeMenu", "NASS"))
        self.cissRadioBtn.setText(_translate("ScrapeMenu", "CISS"))
        self.stopBtn.setText(_translate("ScrapeMenu", " Stop Scrape "))
        self.submitBtn.setText(_translate("ScrapeMenu", "Scrape"))
