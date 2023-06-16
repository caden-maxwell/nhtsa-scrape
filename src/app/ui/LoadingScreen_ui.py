# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\LoadingScreen.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LoadingScreen(object):
    def setupUi(self, LoadingScreen):
        LoadingScreen.setObjectName("LoadingScreen")
        LoadingScreen.resize(949, 594)
        self.gridLayout = QtWidgets.QGridLayout(LoadingScreen)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 1, 1, 1)
        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.setObjectName("mainVLayout")
        self.mainTitle = QtWidgets.QLabel(parent=LoadingScreen)
        self.mainTitle.setObjectName("mainTitle")
        self.mainVLayout.addWidget(self.mainTitle)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.mainVLayout.addItem(spacerItem2)
        self.progressBar = QtWidgets.QProgressBar(parent=LoadingScreen)
        self.progressBar.setProperty("value", 78)
        self.progressBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.mainVLayout.addWidget(self.progressBar)
        self.bottomHLayout = QtWidgets.QHBoxLayout()
        self.bottomHLayout.setObjectName("bottomHLayout")
        self.cancelBtn = QtWidgets.QPushButton(parent=LoadingScreen)
        self.cancelBtn.setObjectName("cancelBtn")
        self.bottomHLayout.addWidget(self.cancelBtn)
        self.stopBtn = QtWidgets.QPushButton(parent=LoadingScreen)
        self.stopBtn.setObjectName("stopBtn")
        self.bottomHLayout.addWidget(self.stopBtn)
        self.mainVLayout.addLayout(self.bottomHLayout)
        self.gridLayout.addLayout(self.mainVLayout, 1, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem4, 1, 2, 1, 1)

        self.retranslateUi(LoadingScreen)
        QtCore.QMetaObject.connectSlotsByName(LoadingScreen)

    def retranslateUi(self, LoadingScreen):
        _translate = QtCore.QCoreApplication.translate
        LoadingScreen.setWindowTitle(_translate("LoadingScreen", "Form"))
        self.mainTitle.setText(_translate("LoadingScreen", "Scraping NASS/CDS Database..."))
        self.cancelBtn.setText(_translate("LoadingScreen", "Cancel"))
        self.stopBtn.setText(_translate("LoadingScreen", "Stop and View Data"))