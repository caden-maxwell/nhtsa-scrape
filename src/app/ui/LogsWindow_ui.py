# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\LogsWindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LogsWindow(object):
    def setupUi(self, LogsWindow):
        LogsWindow.setObjectName("LogsWindow")
        LogsWindow.resize(619, 419)
        self.verticalLayout = QtWidgets.QVBoxLayout(LogsWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logsEditText = QtWidgets.QTextEdit(parent=LogsWindow)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.logsEditText.setFont(font)
        self.logsEditText.setReadOnly(True)
        self.logsEditText.setObjectName("logsEditText")
        self.verticalLayout.addWidget(self.logsEditText)
        self.bottomBarHLayout = QtWidgets.QHBoxLayout()
        self.bottomBarHLayout.setObjectName("bottomBarHLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.bottomBarHLayout.addItem(spacerItem)
        self.saveLogsBtn = QtWidgets.QPushButton(parent=LogsWindow)
        self.saveLogsBtn.setObjectName("saveLogsBtn")
        self.bottomBarHLayout.addWidget(self.saveLogsBtn)
        self.bottomBarHLayout.setStretch(0, 1)
        self.bottomBarHLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.bottomBarHLayout)

        self.retranslateUi(LogsWindow)
        QtCore.QMetaObject.connectSlotsByName(LogsWindow)

    def retranslateUi(self, LogsWindow):
        _translate = QtCore.QCoreApplication.translate
        LogsWindow.setWindowTitle(_translate("LogsWindow", "Form"))
        self.saveLogsBtn.setText(_translate("LogsWindow", "Save Logs"))
