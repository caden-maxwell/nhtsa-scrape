# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\ProfileMenu.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ProfileMenu(object):
    def setupUi(self, ProfileMenu):
        ProfileMenu.setObjectName("ProfileMenu")
        ProfileMenu.resize(735, 521)
        self.verticalLayout = QtWidgets.QVBoxLayout(ProfileMenu)
        self.verticalLayout.setObjectName("verticalLayout")
        self.topBarHLayout = QtWidgets.QHBoxLayout()
        self.topBarHLayout.setObjectName("topBarHLayout")
        self.backBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.backBtn.setObjectName("backBtn")
        self.topBarHLayout.addWidget(self.backBtn)
        self.menuTitle = QtWidgets.QLabel(parent=ProfileMenu)
        self.menuTitle.setObjectName("menuTitle")
        self.topBarHLayout.addWidget(self.menuTitle)
        self.verticalLayout.addLayout(self.topBarHLayout)
        self.listView = QtWidgets.QListView(parent=ProfileMenu)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.bottomBarHLayout = QtWidgets.QHBoxLayout()
        self.bottomBarHLayout.setObjectName("bottomBarHLayout")
        self.reScrapeBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.reScrapeBtn.setObjectName("reScrapeBtn")
        self.bottomBarHLayout.addWidget(self.reScrapeBtn)
        self.openCaseBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.openCaseBtn.setObjectName("openCaseBtn")
        self.bottomBarHLayout.addWidget(self.openCaseBtn)
        self.verticalLayout.addLayout(self.bottomBarHLayout)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(ProfileMenu)
        QtCore.QMetaObject.connectSlotsByName(ProfileMenu)

    def retranslateUi(self, ProfileMenu):
        _translate = QtCore.QCoreApplication.translate
        ProfileMenu.setWindowTitle(_translate("ProfileMenu", "Form"))
        self.backBtn.setText(_translate("ProfileMenu", "Back"))
        self.menuTitle.setText(_translate("ProfileMenu", "Open Existing Case Profile..."))
        self.reScrapeBtn.setText(_translate("ProfileMenu", "Re-Scrape"))
        self.openCaseBtn.setText(_translate("ProfileMenu", "Open Case Profile"))
