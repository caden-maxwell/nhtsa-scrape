# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\SummaryTab.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SummaryTab(object):
    def setupUi(self, SummaryTab):
        SummaryTab.setObjectName("SummaryTab")
        SummaryTab.resize(608, 538)
        self.gridLayout = QtWidgets.QGridLayout(SummaryTab)
        self.gridLayout.setObjectName("gridLayout")
        self.paramsBox = QtWidgets.QGroupBox(parent=SummaryTab)
        self.paramsBox.setObjectName("paramsBox")
        self.formLayout = QtWidgets.QFormLayout(self.paramsBox)
        self.formLayout.setObjectName("formLayout")
        self.makeLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.makeLabel.setObjectName("makeLabel")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.makeLabel
        )
        self.makeEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.makeEdit.setReadOnly(True)
        self.makeEdit.setObjectName("makeEdit")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.makeEdit
        )
        self.modelLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.modelLabel.setObjectName("modelLabel")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.modelLabel
        )
        self.modelEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.modelEdit.setReadOnly(True)
        self.modelEdit.setObjectName("modelEdit")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.modelEdit
        )
        self.startYearLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.startYearLabel.setObjectName("startYearLabel")
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.startYearLabel
        )
        self.startYearEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.startYearEdit.setReadOnly(True)
        self.startYearEdit.setObjectName("startYearEdit")
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.startYearEdit
        )
        self.endYearLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.endYearLabel.setObjectName("endYearLabel")
        self.formLayout.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.endYearLabel
        )
        self.endYearEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.endYearEdit.setReadOnly(True)
        self.endYearEdit.setObjectName("endYearEdit")
        self.formLayout.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.endYearEdit
        )
        self.minDVLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.minDVLabel.setObjectName("minDVLabel")
        self.formLayout.setWidget(
            4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.minDVLabel
        )
        self.minDVEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.minDVEdit.setReadOnly(True)
        self.minDVEdit.setObjectName("minDVEdit")
        self.formLayout.setWidget(
            4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.minDVEdit
        )
        self.maxDVLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.maxDVLabel.setObjectName("maxDVLabel")
        self.formLayout.setWidget(
            5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.maxDVLabel
        )
        self.maxDVEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.maxDVEdit.setReadOnly(True)
        self.maxDVEdit.setObjectName("maxDVEdit")
        self.formLayout.setWidget(
            5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.maxDVEdit
        )
        self.pDmgLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.pDmgLabel.setObjectName("pDmgLabel")
        self.formLayout.setWidget(
            6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.pDmgLabel
        )
        self.pDmgEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.pDmgEdit.setReadOnly(True)
        self.pDmgEdit.setObjectName("pDmgEdit")
        self.formLayout.setWidget(
            6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pDmgEdit
        )
        self.sDmgLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.sDmgLabel.setObjectName("sDmgLabel")
        self.formLayout.setWidget(
            7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.sDmgLabel
        )
        self.sDmgEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.sDmgEdit.setReadOnly(True)
        self.sDmgEdit.setObjectName("sDmgEdit")
        self.formLayout.setWidget(
            7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.sDmgEdit
        )
        self.maxCasesLabel = QtWidgets.QLabel(parent=self.paramsBox)
        self.maxCasesLabel.setObjectName("maxCasesLabel")
        self.formLayout.setWidget(
            8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.maxCasesLabel
        )
        self.maxCasesEdit = QtWidgets.QLineEdit(parent=self.paramsBox)
        self.maxCasesEdit.setReadOnly(True)
        self.maxCasesEdit.setObjectName("maxCasesEdit")
        self.formLayout.setWidget(
            8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.maxCasesEdit
        )
        self.gridLayout.addWidget(self.paramsBox, 0, 0, 1, 1)
        self.statsBox = QtWidgets.QGroupBox(parent=SummaryTab)
        self.statsBox.setObjectName("statsBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.statsBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.totalCasesEdit = QtWidgets.QLineEdit(parent=self.statsBox)
        self.totalCasesEdit.setReadOnly(True)
        self.totalCasesEdit.setObjectName("totalCasesEdit")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.totalCasesEdit
        )
        self.totalCasesLabel = QtWidgets.QLabel(parent=self.statsBox)
        self.totalCasesLabel.setObjectName("totalCasesLabel")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.totalCasesLabel
        )
        self.failedParsesLabel = QtWidgets.QLabel(parent=self.statsBox)
        self.failedParsesLabel.setObjectName("failedParsesLabel")
        self.formLayout_2.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.failedParsesLabel
        )
        self.failedParsesEdit = QtWidgets.QLineEdit(parent=self.statsBox)
        self.failedParsesEdit.setReadOnly(True)
        self.failedParsesEdit.setObjectName("failedParsesEdit")
        self.formLayout_2.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.failedParsesEdit
        )
        self.totalTimeLabel = QtWidgets.QLabel(parent=self.statsBox)
        self.totalTimeLabel.setObjectName("totalTimeLabel")
        self.formLayout_2.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.totalTimeLabel
        )
        self.totalTimeEdit = QtWidgets.QLineEdit(parent=self.statsBox)
        self.totalTimeEdit.setReadOnly(True)
        self.totalTimeEdit.setObjectName("totalTimeEdit")
        self.formLayout_2.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.totalTimeEdit
        )
        self.gridLayout.addWidget(self.statsBox, 0, 1, 1, 1)
        self.listView = QtWidgets.QListView(parent=SummaryTab)
        self.listView.setObjectName("listView")
        self.gridLayout.addWidget(self.listView, 8, 0, 1, 2)

        self.retranslateUi(SummaryTab)
        QtCore.QMetaObject.connectSlotsByName(SummaryTab)

    def retranslateUi(self, SummaryTab):
        _translate = QtCore.QCoreApplication.translate
        SummaryTab.setWindowTitle(_translate("SummaryTab", "Form"))
        self.paramsBox.setTitle(_translate("SummaryTab", "Scrape Parameters:"))
        self.makeLabel.setText(_translate("SummaryTab", "Make"))
        self.modelLabel.setText(_translate("SummaryTab", "Model"))
        self.startYearLabel.setText(_translate("SummaryTab", "Start Year"))
        self.endYearLabel.setText(_translate("SummaryTab", "End Year"))
        self.minDVLabel.setText(_translate("SummaryTab", "Min Delta-V"))
        self.maxDVLabel.setText(_translate("SummaryTab", "Max Delta-V"))
        self.pDmgLabel.setText(_translate("SummaryTab", "Primary Damage"))
        self.sDmgLabel.setText(_translate("SummaryTab", "Secondary Damage"))
        self.maxCasesLabel.setText(_translate("SummaryTab", "Max Cases"))
        self.statsBox.setTitle(_translate("SummaryTab", "Scrape Statistics:"))
        self.totalCasesLabel.setText(_translate("SummaryTab", "Total Cases Scraped:"))
        self.failedParsesLabel.setText(_translate("SummaryTab", "Failed to Parse:"))
        self.totalTimeLabel.setText(_translate("SummaryTab", "Total Time:"))