# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\MainMenu.ui'
#
# Created by: PyQt6 UI code generator 6.7.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainMenu(object):
    def setupUi(self, MainMenu):
        MainMenu.setObjectName("MainMenu")
        MainMenu.resize(1080, 720)
        self.gridLayout_2 = QtWidgets.QGridLayout(MainMenu)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 1, 2, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 0, 1, 1, 1)
        self.frame = QtWidgets.QFrame(parent=MainMenu)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("frame")
        self.mainVLayout = QtWidgets.QVBoxLayout(self.frame)
        self.mainVLayout.setContentsMargins(10, 10, 10, 10)
        self.mainVLayout.setObjectName("mainVLayout")
        self.mainTitle = QtWidgets.QLabel(parent=self.frame)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.mainTitle.setFont(font)
        self.mainTitle.setObjectName("mainTitle")
        self.mainVLayout.addWidget(self.mainTitle, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.line = QtWidgets.QFrame(parent=self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.mainVLayout.addWidget(self.line)
        spacerItem4 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.mainVLayout.addItem(spacerItem4)
        self.scrapeBtn = QtWidgets.QPushButton(parent=self.frame)
        self.scrapeBtn.setObjectName("scrapeBtn")
        self.mainVLayout.addWidget(self.scrapeBtn)
        self.openBtn = QtWidgets.QPushButton(parent=self.frame)
        self.openBtn.setObjectName("openBtn")
        self.mainVLayout.addWidget(self.openBtn)
        self.logsBtn = QtWidgets.QPushButton(parent=self.frame)
        self.logsBtn.setObjectName("logsBtn")
        self.mainVLayout.addWidget(self.logsBtn)
        self.settingsBtn = QtWidgets.QPushButton(parent=self.frame)
        self.settingsBtn.setObjectName("settingsBtn")
        self.mainVLayout.addWidget(self.settingsBtn)
        self.gridLayout_2.addWidget(self.frame, 1, 1, 1, 1)

        self.retranslateUi(MainMenu)
        QtCore.QMetaObject.connectSlotsByName(MainMenu)

    def retranslateUi(self, MainMenu):
        _translate = QtCore.QCoreApplication.translate
        MainMenu.setWindowTitle(_translate("MainMenu", "Form"))
        self.mainTitle.setText(_translate("MainMenu", "NHTSA Scrape Tool"))
        self.scrapeBtn.setText(_translate("MainMenu", "New Scrape"))
        self.openBtn.setText(_translate("MainMenu", "Open Existing Profile"))
        self.logsBtn.setText(_translate("MainMenu", "Open Application Logs"))
        self.settingsBtn.setText(_translate("MainMenu", "Settings"))
