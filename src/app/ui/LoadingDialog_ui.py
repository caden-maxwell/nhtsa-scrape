# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\LoadingDialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LoadingDialog(object):
    def setupUi(self, LoadingDialog):
        LoadingDialog.setObjectName("LoadingDialog")
        LoadingDialog.resize(353, 157)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoadingDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainTitle = QtWidgets.QLabel(parent=LoadingDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainTitle.sizePolicy().hasHeightForWidth())
        self.mainTitle.setSizePolicy(sizePolicy)
        self.mainTitle.setObjectName("mainTitle")
        self.verticalLayout.addWidget(self.mainTitle)
        self.progressBar = QtWidgets.QProgressBar(parent=LoadingDialog)
        self.progressBar.setProperty("value", 78)
        self.progressBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.lineEdit = QtWidgets.QLineEdit(parent=LoadingDialog)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=LoadingDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LoadingDialog)
        self.buttonBox.accepted.connect(LoadingDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(LoadingDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(LoadingDialog)

    def retranslateUi(self, LoadingDialog):
        _translate = QtCore.QCoreApplication.translate
        LoadingDialog.setWindowTitle(_translate("LoadingDialog", "Dialog"))
        self.mainTitle.setText(_translate("LoadingDialog", "Scraping NASS/CDS Database..."))
        self.lineEdit.setText(_translate("LoadingDialog", "Logging here"))
