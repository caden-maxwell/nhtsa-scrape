# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\EventsTab.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_EventsTab(object):
    def setupUi(self, EventsTab):
        EventsTab.setObjectName("EventsTab")
        EventsTab.resize(548, 377)
        self.gridLayout = QtWidgets.QGridLayout(EventsTab)
        self.gridLayout.setObjectName("gridLayout")
        self.promptLabel = QtWidgets.QLabel(parent=EventsTab)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.promptLabel.sizePolicy().hasHeightForWidth())
        self.promptLabel.setSizePolicy(sizePolicy)
        self.promptLabel.setObjectName("promptLabel")
        self.gridLayout.addWidget(self.promptLabel, 0, 0, 1, 1)
        self.eventLayout = QtWidgets.QGridLayout()
        self.eventLayout.setObjectName("eventLayout")
        self.gridLayout.addLayout(self.eventLayout, 1, 1, 1, 1)
        self.eventsList = QtWidgets.QListView(parent=EventsTab)
        self.eventsList.setMinimumSize(QtCore.QSize(100, 0))
        self.eventsList.setObjectName("eventsList")
        self.gridLayout.addWidget(self.eventsList, 1, 0, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(EventsTab)
        QtCore.QMetaObject.connectSlotsByName(EventsTab)

    def retranslateUi(self, EventsTab):
        _translate = QtCore.QCoreApplication.translate
        EventsTab.setWindowTitle(_translate("EventsTab", "Events"))
        self.promptLabel.setText(_translate("EventsTab", "Select an event to view:"))
