# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\ScatterTab.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ScatterTab(object):
    def setupUi(self, ScatterTab):
        ScatterTab.setObjectName("ScatterTab")
        ScatterTab.resize(504, 358)
        self.gridLayout = QtWidgets.QGridLayout(ScatterTab)
        self.gridLayout.setObjectName("gridLayout")
        self.nassDataBtn = QtWidgets.QPushButton(parent=ScatterTab)
        self.nassDataBtn.setCheckable(True)
        self.nassDataBtn.setChecked(True)
        self.nassDataBtn.setObjectName("nassDataBtn")
        self.gridLayout.addWidget(self.nassDataBtn, 1, 1, 1, 1)
        self.nassLabelBtn = QtWidgets.QPushButton(parent=ScatterTab)
        self.nassLabelBtn.setCheckable(True)
        self.nassLabelBtn.setChecked(True)
        self.nassLabelBtn.setObjectName("nassLabelBtn")
        self.gridLayout.addWidget(self.nassLabelBtn, 1, 2, 1, 1)
        self.totalDataBtn = QtWidgets.QPushButton(parent=ScatterTab)
        self.totalDataBtn.setCheckable(True)
        self.totalDataBtn.setObjectName("totalDataBtn")
        self.gridLayout.addWidget(self.totalDataBtn, 1, 3, 1, 1)
        self.totalLabelBtn = QtWidgets.QPushButton(parent=ScatterTab)
        self.totalLabelBtn.setEnabled(False)
        self.totalLabelBtn.setCheckable(True)
        self.totalLabelBtn.setChecked(True)
        self.totalLabelBtn.setObjectName("totalLabelBtn")
        self.gridLayout.addWidget(self.totalLabelBtn, 1, 4, 1, 1)
        self.scatterLayout = QtWidgets.QVBoxLayout()
        self.scatterLayout.setObjectName("scatterLayout")
        self.gridLayout.addLayout(self.scatterLayout, 0, 1, 1, 4)

        self.retranslateUi(ScatterTab)
        QtCore.QMetaObject.connectSlotsByName(ScatterTab)

    def retranslateUi(self, ScatterTab):
        _translate = QtCore.QCoreApplication.translate
        ScatterTab.setWindowTitle(_translate("ScatterTab", "Scatterplot"))
        self.nassDataBtn.setText(_translate("ScatterTab", "NASS_dv"))
        self.nassLabelBtn.setText(_translate("ScatterTab", "NASS_dv Case Labels"))
        self.totalDataBtn.setText(_translate("ScatterTab", "TOT_dv"))
        self.totalLabelBtn.setText(_translate("ScatterTab", "TOT_dv Case Labels"))
