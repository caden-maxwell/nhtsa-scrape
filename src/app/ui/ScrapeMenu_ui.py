# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\ScrapeMenu.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ScrapeMenu(object):
    def setupUi(self, ScrapeMenu):
        ScrapeMenu.setObjectName("ScrapeMenu")
        ScrapeMenu.resize(932, 593)
        self.gridLayout = QtWidgets.QGridLayout(ScrapeMenu)
        self.gridLayout.setObjectName("gridLayout")
        self.submitBtn = QtWidgets.QPushButton(parent=ScrapeMenu)
        self.submitBtn.setEnabled(False)
        self.submitBtn.setObjectName("submitBtn")
        self.gridLayout.addWidget(self.submitBtn, 3, 3, 1, 1)
        self.mainTitle = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainTitle.sizePolicy().hasHeightForWidth())
        self.mainTitle.setSizePolicy(sizePolicy)
        self.mainTitle.setObjectName("mainTitle")
        self.gridLayout.addWidget(self.mainTitle, 0, 1, 1, 1)
        self.backBtn = QtWidgets.QPushButton(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.backBtn.sizePolicy().hasHeightForWidth())
        self.backBtn.setSizePolicy(sizePolicy)
        self.backBtn.setObjectName("backBtn")
        self.gridLayout.addWidget(self.backBtn, 0, 0, 1, 1)
        self.body = QtWidgets.QGridLayout()
        self.body.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.body.setObjectName("body")
        self.deltaVBox = QtWidgets.QGroupBox(parent=ScrapeMenu)
        self.deltaVBox.setObjectName("deltaVBox")
        self.formLayout_4 = QtWidgets.QFormLayout(self.deltaVBox)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_4 = QtWidgets.QLabel(parent=self.deltaVBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.formLayout_4.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_4
        )
        self.dvMinSpin = QtWidgets.QSpinBox(parent=self.deltaVBox)
        self.dvMinSpin.setMaximum(999999999)
        self.dvMinSpin.setObjectName("dvMinSpin")
        self.formLayout_4.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dvMinSpin
        )
        self.label_8 = QtWidgets.QLabel(parent=self.deltaVBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.formLayout_4.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_8
        )
        self.dvMaxSpin = QtWidgets.QSpinBox(parent=self.deltaVBox)
        self.dvMaxSpin.setMaximum(999999999)
        self.dvMaxSpin.setObjectName("dvMaxSpin")
        self.formLayout_4.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dvMaxSpin
        )
        self.body.addWidget(self.deltaVBox, 2, 3, 1, 1)
        self.damageBox = QtWidgets.QGroupBox(parent=ScrapeMenu)
        self.damageBox.setObjectName("damageBox")
        self.formLayout = QtWidgets.QFormLayout(self.damageBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(parent=self.damageBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label
        )
        self.pDmgCombo = QtWidgets.QComboBox(parent=self.damageBox)
        self.pDmgCombo.setEditable(False)
        self.pDmgCombo.setObjectName("pDmgCombo")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pDmgCombo
        )
        self.label_2 = QtWidgets.QLabel(parent=self.damageBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2
        )
        self.sDmgCombo = QtWidgets.QComboBox(parent=self.damageBox)
        self.sDmgCombo.setEditable(False)
        self.sDmgCombo.setObjectName("sDmgCombo")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sDmgCombo
        )
        self.body.addWidget(self.damageBox, 2, 1, 1, 1)
        self.vehicleBox = QtWidgets.QGroupBox(parent=ScrapeMenu)
        self.vehicleBox.setObjectName("vehicleBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.vehicleBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.makeLabel = QtWidgets.QLabel(parent=self.vehicleBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.makeLabel.sizePolicy().hasHeightForWidth())
        self.makeLabel.setSizePolicy(sizePolicy)
        self.makeLabel.setObjectName("makeLabel")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.makeLabel
        )
        self.makeCombo = QtWidgets.QComboBox(parent=self.vehicleBox)
        self.makeCombo.setMinimumSize(QtCore.QSize(200, 0))
        self.makeCombo.setEditable(False)
        self.makeCombo.setObjectName("makeCombo")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.makeCombo
        )
        self.modelLabel = QtWidgets.QLabel(parent=self.vehicleBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modelLabel.sizePolicy().hasHeightForWidth())
        self.modelLabel.setSizePolicy(sizePolicy)
        self.modelLabel.setObjectName("modelLabel")
        self.formLayout_2.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.modelLabel
        )
        self.modelCombo = QtWidgets.QComboBox(parent=self.vehicleBox)
        self.modelCombo.setEditable(False)
        self.modelCombo.setObjectName("modelCombo")
        self.formLayout_2.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.modelCombo
        )
        self.body.addWidget(self.vehicleBox, 1, 1, 1, 1)
        self.yearsBox = QtWidgets.QGroupBox(parent=ScrapeMenu)
        self.yearsBox.setObjectName("yearsBox")
        self.formLayout_3 = QtWidgets.QFormLayout(self.yearsBox)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_6 = QtWidgets.QLabel(parent=self.yearsBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.formLayout_3.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_6
        )
        self.startYearCombo = QtWidgets.QComboBox(parent=self.yearsBox)
        self.startYearCombo.setEditable(False)
        self.startYearCombo.setObjectName("startYearCombo")
        self.formLayout_3.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.startYearCombo
        )
        self.label_7 = QtWidgets.QLabel(parent=self.yearsBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.formLayout_3.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_7
        )
        self.endYearCombo = QtWidgets.QComboBox(parent=self.yearsBox)
        self.endYearCombo.setEditable(False)
        self.endYearCombo.setObjectName("endYearCombo")
        self.formLayout_3.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.endYearCombo
        )
        self.body.addWidget(self.yearsBox, 1, 3, 1, 1)
        self.databasesBox = QtWidgets.QGroupBox(parent=ScrapeMenu)
        self.databasesBox.setObjectName("databasesBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.databasesBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nassCheckbox = QtWidgets.QCheckBox(parent=self.databasesBox)
        self.nassCheckbox.setChecked(True)
        self.nassCheckbox.setObjectName("nassCheckbox")
        self.horizontalLayout.addWidget(self.nassCheckbox)
        self.cissCheckbox = QtWidgets.QCheckBox(parent=self.databasesBox)
        self.cissCheckbox.setChecked(True)
        self.cissCheckbox.setObjectName("cissCheckbox")
        self.horizontalLayout.addWidget(self.cissCheckbox)
        self.body.addWidget(self.databasesBox, 3, 3, 1, 1)
        self.maxCasesBox = QtWidgets.QGroupBox(parent=ScrapeMenu)
        self.maxCasesBox.setObjectName("maxCasesBox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.maxCasesBox)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.casesSpin = QtWidgets.QSpinBox(parent=self.maxCasesBox)
        self.casesSpin.setMinimum(1)
        self.casesSpin.setMaximum(999999999)
        self.casesSpin.setObjectName("casesSpin")
        self.horizontalLayout_4.addWidget(self.casesSpin)
        self.body.addWidget(self.maxCasesBox, 3, 1, 1, 1)
        self.gridLayout.addLayout(self.body, 2, 0, 1, 4)

        self.retranslateUi(ScrapeMenu)
        QtCore.QMetaObject.connectSlotsByName(ScrapeMenu)

    def retranslateUi(self, ScrapeMenu):
        _translate = QtCore.QCoreApplication.translate
        ScrapeMenu.setWindowTitle(_translate("ScrapeMenu", "Form"))
        self.submitBtn.setText(_translate("ScrapeMenu", "Scrape"))
        self.mainTitle.setText(_translate("ScrapeMenu", "New Scrape"))
        self.backBtn.setText(_translate("ScrapeMenu", "Back"))
        self.deltaVBox.setTitle(_translate("ScrapeMenu", "Delta V (mph):"))
        self.label_4.setText(_translate("ScrapeMenu", "From"))
        self.label_8.setText(_translate("ScrapeMenu", "To"))
        self.damageBox.setTitle(_translate("ScrapeMenu", "Damage Location"))
        self.label.setText(_translate("ScrapeMenu", "Primary:"))
        self.label_2.setText(_translate("ScrapeMenu", "Secondary:"))
        self.vehicleBox.setTitle(_translate("ScrapeMenu", "Vehicle"))
        self.makeLabel.setText(_translate("ScrapeMenu", "Make:"))
        self.modelLabel.setText(_translate("ScrapeMenu", "Model:"))
        self.yearsBox.setTitle(_translate("ScrapeMenu", "Model Years:"))
        self.label_6.setText(_translate("ScrapeMenu", "From"))
        self.label_7.setText(_translate("ScrapeMenu", "To"))
        self.databasesBox.setTitle(_translate("ScrapeMenu", "NHTSA Databases:"))
        self.nassCheckbox.setText(_translate("ScrapeMenu", "NASS/CDS"))
        self.cissCheckbox.setText(_translate("ScrapeMenu", "CISS"))
        self.maxCasesBox.setTitle(_translate("ScrapeMenu", "Max Number of Cases:"))
