# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\ExitDataViewDialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ExitDataViewDialog(object):
    def setupUi(self, ExitDataViewDialog):
        ExitDataViewDialog.setObjectName("ExitDataViewDialog")
        ExitDataViewDialog.resize(398, 184)
        self.verticalLayout = QtWidgets.QVBoxLayout(ExitDataViewDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.promptLabel = QtWidgets.QLabel(parent=ExitDataViewDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.promptLabel.sizePolicy().hasHeightForWidth())
        self.promptLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        self.promptLabel.setFont(font)
        self.promptLabel.setObjectName("promptLabel")
        self.verticalLayout.addWidget(self.promptLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(parent=ExitDataViewDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.profileNameEdit = QtWidgets.QLineEdit(parent=ExitDataViewDialog)
        self.profileNameEdit.setObjectName("profileNameEdit")
        self.verticalLayout.addWidget(self.profileNameEdit)
        self.bottomHLayout = QtWidgets.QHBoxLayout()
        self.bottomHLayout.setObjectName("bottomHLayout")
        self.discardBtn = QtWidgets.QPushButton(parent=ExitDataViewDialog)
        self.discardBtn.setObjectName("discardBtn")
        self.bottomHLayout.addWidget(self.discardBtn)
        self.saveBtn = QtWidgets.QPushButton(parent=ExitDataViewDialog)
        self.saveBtn.setObjectName("saveBtn")
        self.bottomHLayout.addWidget(self.saveBtn)
        self.verticalLayout.addLayout(self.bottomHLayout)

        self.retranslateUi(ExitDataViewDialog)
        QtCore.QMetaObject.connectSlotsByName(ExitDataViewDialog)

    def retranslateUi(self, ExitDataViewDialog):
        _translate = QtCore.QCoreApplication.translate
        ExitDataViewDialog.setWindowTitle(_translate("ExitDataViewDialog", "Form"))
        self.promptLabel.setText(_translate("ExitDataViewDialog", "Save as New Profile?"))
        self.label.setText(_translate("ExitDataViewDialog", "Enter Profile Name:"))
        self.discardBtn.setText(_translate("ExitDataViewDialog", "Exit without Saving"))
        self.saveBtn.setText(_translate("ExitDataViewDialog", "Save and Exit"))