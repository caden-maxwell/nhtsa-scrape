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
        self.verticalLayout = QtWidgets.QVBoxLayout(ScrapeMenu)
        self.verticalLayout.setObjectName("verticalLayout")
        self.topHLayout = QtWidgets.QHBoxLayout()
        self.topHLayout.setObjectName("topHLayout")
        self.backBtn = QtWidgets.QPushButton(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.backBtn.sizePolicy().hasHeightForWidth())
        self.backBtn.setSizePolicy(sizePolicy)
        self.backBtn.setObjectName("backBtn")
        self.topHLayout.addWidget(self.backBtn)
        self.mainTitle = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainTitle.sizePolicy().hasHeightForWidth())
        self.mainTitle.setSizePolicy(sizePolicy)
        self.mainTitle.setObjectName("mainTitle")
        self.topHLayout.addWidget(self.mainTitle)
        self.topHLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.topHLayout)
        self.line_2 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.body = QtWidgets.QGridLayout()
        self.body.setObjectName("body")
        self.imageSetLayout = QtWidgets.QVBoxLayout()
        self.imageSetLayout.setObjectName("imageSetLayout")
        self.label_10 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setObjectName("label_10")
        self.imageSetLayout.addWidget(self.label_10)
        self.imageSetCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.imageSetCombo.setObjectName("imageSetCombo")
        self.imageSetLayout.addWidget(self.imageSetCombo)
        self.body.addLayout(self.imageSetLayout, 4, 2, 1, 1)
        self.vehicleLayout = QtWidgets.QVBoxLayout()
        self.vehicleLayout.setObjectName("vehicleLayout")
        self.makeLabel = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.makeLabel.sizePolicy().hasHeightForWidth())
        self.makeLabel.setSizePolicy(sizePolicy)
        self.makeLabel.setObjectName("makeLabel")
        self.vehicleLayout.addWidget(self.makeLabel)
        self.makeCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.makeCombo.setEditable(False)
        self.makeCombo.setObjectName("makeCombo")
        self.vehicleLayout.addWidget(self.makeCombo)
        self.modelLabel = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modelLabel.sizePolicy().hasHeightForWidth())
        self.modelLabel.setSizePolicy(sizePolicy)
        self.modelLabel.setObjectName("modelLabel")
        self.vehicleLayout.addWidget(self.modelLabel)
        self.modelCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.modelCombo.setEditable(False)
        self.modelCombo.setObjectName("modelCombo")
        self.vehicleLayout.addWidget(self.modelCombo)
        self.body.addLayout(self.vehicleLayout, 0, 0, 3, 1)
        self.line_7 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_7.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_7.setObjectName("line_7")
        self.body.addWidget(self.line_7, 1, 2, 1, 1)
        self.line_3 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.body.addWidget(self.line_3, 3, 0, 1, 1)
        self.damageLayout = QtWidgets.QVBoxLayout()
        self.damageLayout.setObjectName("damageLayout")
        self.label = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.damageLayout.addWidget(self.label)
        self.pDmgCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.pDmgCombo.setEditable(False)
        self.pDmgCombo.setObjectName("pDmgCombo")
        self.damageLayout.addWidget(self.pDmgCombo)
        self.label_2 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.damageLayout.addWidget(self.label_2)
        self.sDmgCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.sDmgCombo.setEditable(False)
        self.sDmgCombo.setObjectName("sDmgCombo")
        self.damageLayout.addWidget(self.sDmgCombo)
        self.body.addLayout(self.damageLayout, 4, 0, 3, 1)
        self.line_5 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_5.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_5.setObjectName("line_5")
        self.body.addWidget(self.line_5, 3, 2, 1, 1)
        self.numCasesLayout = QtWidgets.QVBoxLayout()
        self.numCasesLayout.setObjectName("numCasesLayout")
        self.label_9 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setObjectName("label_9")
        self.numCasesLayout.addWidget(self.label_9)
        self.casesSpin = QtWidgets.QSpinBox(parent=ScrapeMenu)
        self.casesSpin.setMinimum(1)
        self.casesSpin.setMaximum(999999999)
        self.casesSpin.setObjectName("casesSpin")
        self.numCasesLayout.addWidget(self.casesSpin)
        self.body.addLayout(self.numCasesLayout, 6, 2, 1, 1)
        self.yearsLayout = QtWidgets.QGridLayout()
        self.yearsLayout.setObjectName("yearsLayout")
        self.label_7 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.yearsLayout.addWidget(self.label_7, 1, 2, 1, 1)
        self.startYearCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.startYearCombo.setEditable(False)
        self.startYearCombo.setObjectName("startYearCombo")
        self.yearsLayout.addWidget(self.startYearCombo, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.yearsLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.endYearCombo = QtWidgets.QComboBox(parent=ScrapeMenu)
        self.endYearCombo.setEditable(False)
        self.endYearCombo.setObjectName("endYearCombo")
        self.yearsLayout.addWidget(self.endYearCombo, 1, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.yearsLayout.addWidget(self.label_5, 0, 0, 1, 4)
        self.body.addLayout(self.yearsLayout, 0, 2, 1, 1)
        self.deltaLayout = QtWidgets.QGridLayout()
        self.deltaLayout.setObjectName("deltaLayout")
        self.label_8 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.deltaLayout.addWidget(self.label_8, 1, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.deltaLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.dvMaxSpin = QtWidgets.QSpinBox(parent=ScrapeMenu)
        self.dvMaxSpin.setMaximum(999999999)
        self.dvMaxSpin.setObjectName("dvMaxSpin")
        self.deltaLayout.addWidget(self.dvMaxSpin, 1, 3, 1, 1)
        self.dvMinSpin = QtWidgets.QSpinBox(parent=ScrapeMenu)
        self.dvMinSpin.setMaximum(999999999)
        self.dvMinSpin.setObjectName("dvMinSpin")
        self.deltaLayout.addWidget(self.dvMinSpin, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(parent=ScrapeMenu)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.deltaLayout.addWidget(self.label_3, 0, 0, 1, 4)
        self.body.addLayout(self.deltaLayout, 2, 2, 1, 1)
        self.line_8 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_8.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_8.setObjectName("line_8")
        self.body.addWidget(self.line_8, 5, 2, 1, 1)
        self.line_4 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.body.addWidget(self.line_4, 4, 1, 3, 1)
        self.line_6 = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line_6.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_6.setObjectName("line_6")
        self.body.addWidget(self.line_6, 0, 1, 3, 1)
        self.verticalLayout.addLayout(self.body)
        self.line = QtWidgets.QFrame(parent=ScrapeMenu)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.bottomHLayout = QtWidgets.QHBoxLayout()
        self.bottomHLayout.setObjectName("bottomHLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.bottomHLayout.addItem(spacerItem)
        self.submitBtn = QtWidgets.QPushButton(parent=ScrapeMenu)
        self.submitBtn.setEnabled(False)
        self.submitBtn.setMinimumSize(QtCore.QSize(100, 0))
        self.submitBtn.setObjectName("submitBtn")
        self.bottomHLayout.addWidget(self.submitBtn)
        self.verticalLayout.addLayout(self.bottomHLayout)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(ScrapeMenu)
        QtCore.QMetaObject.connectSlotsByName(ScrapeMenu)

    def retranslateUi(self, ScrapeMenu):
        _translate = QtCore.QCoreApplication.translate
        ScrapeMenu.setWindowTitle(_translate("ScrapeMenu", "Form"))
        self.backBtn.setText(_translate("ScrapeMenu", "Back"))
        self.mainTitle.setText(_translate("ScrapeMenu", "New Scrape"))
        self.label_10.setText(_translate("ScrapeMenu", "Image Set:"))
        self.makeLabel.setText(_translate("ScrapeMenu", "Make:"))
        self.modelLabel.setText(_translate("ScrapeMenu", "Model:"))
        self.label.setText(_translate("ScrapeMenu", "Primary Damage Location:"))
        self.label_2.setText(_translate("ScrapeMenu", "Secondary Damage Location:"))
        self.label_9.setText(_translate("ScrapeMenu", "Max Number of Cases:"))
        self.label_7.setText(_translate("ScrapeMenu", "to"))
        self.label_6.setText(_translate("ScrapeMenu", "From"))
        self.label_5.setText(_translate("ScrapeMenu", "Model Years:"))
        self.label_8.setText(_translate("ScrapeMenu", "to"))
        self.label_4.setText(_translate("ScrapeMenu", "From"))
        self.label_3.setText(_translate("ScrapeMenu", "Delta V:"))
        self.submitBtn.setText(_translate("ScrapeMenu", "Scrape"))
