# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\ProfileMenu.ui'
#
# Created by: PyQt6 UI code generator 6.7.0
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
        self.topHLayout = QtWidgets.QHBoxLayout()
        self.topHLayout.setObjectName("topHLayout")
        self.backBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.backBtn.setObjectName("backBtn")
        self.topHLayout.addWidget(self.backBtn)
        self.mainTitle = QtWidgets.QLabel(parent=ProfileMenu)
        self.mainTitle.setObjectName("mainTitle")
        self.topHLayout.addWidget(self.mainTitle)
        self.topHLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.topHLayout)
        self.treeView = QtWidgets.QTreeView(parent=ProfileMenu)
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        self.bottomHLayout = QtWidgets.QHBoxLayout()
        self.bottomHLayout.setObjectName("bottomHLayout")
        self.deleteBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.deleteBtn.setEnabled(False)
        self.deleteBtn.setObjectName("deleteBtn")
        self.bottomHLayout.addWidget(self.deleteBtn)
        self.renameBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.renameBtn.setEnabled(False)
        self.renameBtn.setObjectName("renameBtn")
        self.bottomHLayout.addWidget(self.renameBtn)
        self.openBtn = QtWidgets.QPushButton(parent=ProfileMenu)
        self.openBtn.setEnabled(False)
        self.openBtn.setDefault(True)
        self.openBtn.setObjectName("openBtn")
        self.bottomHLayout.addWidget(self.openBtn)
        self.verticalLayout.addLayout(self.bottomHLayout)

        self.retranslateUi(ProfileMenu)
        QtCore.QMetaObject.connectSlotsByName(ProfileMenu)

    def retranslateUi(self, ProfileMenu):
        _translate = QtCore.QCoreApplication.translate
        ProfileMenu.setWindowTitle(_translate("ProfileMenu", "Form"))
        self.backBtn.setText(_translate("ProfileMenu", "Back"))
        self.mainTitle.setText(_translate("ProfileMenu", "Open Existing Scrape Profile..."))
        self.deleteBtn.setText(_translate("ProfileMenu", "Delete"))
        self.renameBtn.setText(_translate("ProfileMenu", "Rename"))
        self.openBtn.setText(_translate("ProfileMenu", "Open"))
