# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\DataView.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_DataView(object):
    def setupUi(self, DataView):
        DataView.setObjectName("DataView")
        DataView.resize(800, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(DataView)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=DataView)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(DataView)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(DataView)

    def retranslateUi(self, DataView):
        _translate = QtCore.QCoreApplication.translate
        DataView.setWindowTitle(
            _translate("DataView", "NHTSA Scrape Tool - Data Viewer")
        )
