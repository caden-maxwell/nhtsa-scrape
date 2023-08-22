# Form implementation generated from reading ui file 'c:\Users\Caden\Desktop\nhtsa-scrape\src\app\ui\EventsTab.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_EventsTab(object):
    def setupUi(self, EventsTab):
        EventsTab.setObjectName("EventsTab")
        EventsTab.resize(901, 771)
        self.mainGrid = QtWidgets.QGridLayout(EventsTab)
        self.mainGrid.setObjectName("mainGrid")
        self.line_2 = QtWidgets.QFrame(parent=EventsTab)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.mainGrid.addWidget(self.line_2, 0, 1, 5, 1)
        self.eventsList = QtWidgets.QListView(parent=EventsTab)
        self.eventsList.setMinimumSize(QtCore.QSize(100, 0))
        self.eventsList.setObjectName("eventsList")
        self.mainGrid.addWidget(self.eventsList, 1, 0, 4, 1)
        self.promptLabel = QtWidgets.QLabel(parent=EventsTab)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.promptLabel.sizePolicy().hasHeightForWidth())
        self.promptLabel.setSizePolicy(sizePolicy)
        self.promptLabel.setObjectName("promptLabel")
        self.mainGrid.addWidget(self.promptLabel, 0, 0, 1, 1)
        self.imgWidget = QtWidgets.QWidget(parent=EventsTab)
        self.imgWidget.setObjectName("imgWidget")
        self.imgWidgetGrid = QtWidgets.QGridLayout(self.imgWidget)
        self.imgWidgetGrid.setObjectName("imgWidgetGrid")
        self.scrollArea = QtWidgets.QScrollArea(parent=self.imgWidget)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 200))
        self.scrollArea.setMaximumSize(QtCore.QSize(16777215, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.thumbnailsWidget = QtWidgets.QWidget()
        self.thumbnailsWidget.setGeometry(QtCore.QRect(0, 0, 863, 198))
        self.thumbnailsWidget.setObjectName("thumbnailsWidget")
        self.thumbnailsLayout = QtWidgets.QHBoxLayout(self.thumbnailsWidget)
        self.thumbnailsLayout.setObjectName("thumbnailsLayout")
        self.scrollArea.setWidget(self.thumbnailsWidget)
        self.imgWidgetGrid.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.mainGrid.addWidget(self.imgWidget, 5, 0, 1, 3)
        self.imgScrapeBox = QtWidgets.QGroupBox(parent=EventsTab)
        self.imgScrapeBox.setObjectName("imgScrapeBox")
        self.gridLayout = QtWidgets.QGridLayout(self.imgScrapeBox)
        self.gridLayout.setObjectName("gridLayout")
        self.imgSetCombo = QtWidgets.QComboBox(parent=self.imgScrapeBox)
        self.imgSetCombo.setObjectName("imgSetCombo")
        self.gridLayout.addWidget(self.imgSetCombo, 0, 0, 1, 1)
        self.scrapeBtn = QtWidgets.QPushButton(parent=self.imgScrapeBox)
        self.scrapeBtn.setObjectName("scrapeBtn")
        self.gridLayout.addWidget(self.scrapeBtn, 0, 2, 1, 1)
        self.stopBtn = QtWidgets.QPushButton(parent=self.imgScrapeBox)
        self.stopBtn.setObjectName("stopBtn")
        self.gridLayout.addWidget(self.stopBtn, 0, 3, 1, 1)
        self.mainGrid.addWidget(self.imgScrapeBox, 4, 2, 1, 1)
        self.actionsBox = QtWidgets.QGroupBox(parent=EventsTab)
        self.actionsBox.setObjectName("actionsBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.actionsBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ignoreBtn = QtWidgets.QPushButton(parent=self.actionsBox)
        self.ignoreBtn.setObjectName("ignoreBtn")
        self.horizontalLayout_3.addWidget(self.ignoreBtn)
        self.discardBtn = QtWidgets.QPushButton(parent=self.actionsBox)
        self.discardBtn.setObjectName("discardBtn")
        self.horizontalLayout_3.addWidget(self.discardBtn)
        self.mainGrid.addWidget(self.actionsBox, 2, 2, 1, 1)
        self.dataBox = QtWidgets.QGroupBox(parent=EventsTab)
        self.dataBox.setObjectName("dataBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.dataBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.eventDataLeft = QtWidgets.QWidget(parent=self.dataBox)
        self.eventDataLeft.setObjectName("eventDataLeft")
        self.formLayoutLeft = QtWidgets.QFormLayout(self.eventDataLeft)
        self.formLayoutLeft.setVerticalSpacing(4)
        self.formLayoutLeft.setObjectName("formLayoutLeft")
        self.makeLabel = QtWidgets.QLabel(parent=self.eventDataLeft)
        self.makeLabel.setObjectName("makeLabel")
        self.formLayoutLeft.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.makeLabel
        )
        self.makeLineEdit = QtWidgets.QLineEdit(parent=self.eventDataLeft)
        self.makeLineEdit.setReadOnly(True)
        self.makeLineEdit.setObjectName("makeLineEdit")
        self.formLayoutLeft.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.makeLineEdit
        )
        self.modelLabel = QtWidgets.QLabel(parent=self.eventDataLeft)
        self.modelLabel.setObjectName("modelLabel")
        self.formLayoutLeft.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.modelLabel
        )
        self.modelLineEdit = QtWidgets.QLineEdit(parent=self.eventDataLeft)
        self.modelLineEdit.setReadOnly(True)
        self.modelLineEdit.setObjectName("modelLineEdit")
        self.formLayoutLeft.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.modelLineEdit
        )
        self.yearLabel = QtWidgets.QLabel(parent=self.eventDataLeft)
        self.yearLabel.setObjectName("yearLabel")
        self.formLayoutLeft.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.yearLabel
        )
        self.yearLineEdit = QtWidgets.QLineEdit(parent=self.eventDataLeft)
        self.yearLineEdit.setReadOnly(True)
        self.yearLineEdit.setObjectName("yearLineEdit")
        self.formLayoutLeft.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.yearLineEdit
        )
        self.curbWeightLabel = QtWidgets.QLabel(parent=self.eventDataLeft)
        self.curbWeightLabel.setObjectName("curbWeightLabel")
        self.formLayoutLeft.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.curbWeightLabel
        )
        self.curbWeightLineEdit = QtWidgets.QLineEdit(parent=self.eventDataLeft)
        self.curbWeightLineEdit.setReadOnly(True)
        self.curbWeightLineEdit.setObjectName("curbWeightLineEdit")
        self.formLayoutLeft.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.curbWeightLineEdit
        )
        self.dmgLocLabel = QtWidgets.QLabel(parent=self.eventDataLeft)
        self.dmgLocLabel.setObjectName("dmgLocLabel")
        self.formLayoutLeft.setWidget(
            4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.dmgLocLabel
        )
        self.dmgLocLineEdit = QtWidgets.QLineEdit(parent=self.eventDataLeft)
        self.dmgLocLineEdit.setReadOnly(True)
        self.dmgLocLineEdit.setObjectName("dmgLocLineEdit")
        self.formLayoutLeft.setWidget(
            4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dmgLocLineEdit
        )
        self.underrideLabel = QtWidgets.QLabel(parent=self.eventDataLeft)
        self.underrideLabel.setObjectName("underrideLabel")
        self.formLayoutLeft.setWidget(
            5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.underrideLabel
        )
        self.underrideLineEdit = QtWidgets.QLineEdit(parent=self.eventDataLeft)
        self.underrideLineEdit.setReadOnly(True)
        self.underrideLineEdit.setObjectName("underrideLineEdit")
        self.formLayoutLeft.setWidget(
            5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.underrideLineEdit
        )
        self.gridLayout_2.addWidget(self.eventDataLeft, 0, 0, 1, 1)
        self.eventDataRight = QtWidgets.QWidget(parent=self.dataBox)
        self.eventDataRight.setObjectName("eventDataRight")
        self.formLayoutRight = QtWidgets.QFormLayout(self.eventDataRight)
        self.formLayoutRight.setVerticalSpacing(4)
        self.formLayoutRight.setObjectName("formLayoutRight")
        self.cBarLabel = QtWidgets.QLabel(parent=self.eventDataRight)
        self.cBarLabel.setObjectName("cBarLabel")
        self.formLayoutRight.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.cBarLabel
        )
        self.cBarLineEdit = QtWidgets.QLineEdit(parent=self.eventDataRight)
        self.cBarLineEdit.setReadOnly(True)
        self.cBarLineEdit.setObjectName("cBarLineEdit")
        self.formLayoutRight.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.cBarLineEdit
        )
        self.nassDVLabel = QtWidgets.QLabel(parent=self.eventDataRight)
        self.nassDVLabel.setObjectName("nassDVLabel")
        self.formLayoutRight.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nassDVLabel
        )
        self.nassDVLineEdit = QtWidgets.QLineEdit(parent=self.eventDataRight)
        self.nassDVLineEdit.setReadOnly(True)
        self.nassDVLineEdit.setObjectName("nassDVLineEdit")
        self.formLayoutRight.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.nassDVLineEdit
        )
        self.nassVCLabel = QtWidgets.QLabel(parent=self.eventDataRight)
        self.nassVCLabel.setObjectName("nassVCLabel")
        self.formLayoutRight.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.nassVCLabel
        )
        self.nassVCLineEdit = QtWidgets.QLineEdit(parent=self.eventDataRight)
        self.nassVCLineEdit.setReadOnly(True)
        self.nassVCLineEdit.setObjectName("nassVCLineEdit")
        self.formLayoutRight.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.nassVCLineEdit
        )
        self.totDVLabel = QtWidgets.QLabel(parent=self.eventDataRight)
        self.totDVLabel.setObjectName("totDVLabel")
        self.formLayoutRight.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.totDVLabel
        )
        self.totDVLineEdit = QtWidgets.QLineEdit(parent=self.eventDataRight)
        self.totDVLineEdit.setReadOnly(True)
        self.totDVLineEdit.setObjectName("totDVLineEdit")
        self.formLayoutRight.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.totDVLineEdit
        )
        self.gridLayout_2.addWidget(self.eventDataRight, 0, 2, 1, 1)
        self.line = QtWidgets.QFrame(parent=self.dataBox)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 0, 1, 1, 1)
        self.mainGrid.addWidget(self.dataBox, 0, 2, 2, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.mainGrid.addItem(spacerItem, 3, 2, 1, 1)

        self.retranslateUi(EventsTab)
        QtCore.QMetaObject.connectSlotsByName(EventsTab)

    def retranslateUi(self, EventsTab):
        _translate = QtCore.QCoreApplication.translate
        EventsTab.setWindowTitle(_translate("EventsTab", "Events"))
        self.promptLabel.setText(_translate("EventsTab", "Select an event to view:"))
        self.imgScrapeBox.setTitle(_translate("EventsTab", "Image Scrape:"))
        self.imgSetCombo.setPlaceholderText(_translate("EventsTab", "Image Set"))
        self.scrapeBtn.setText(_translate("EventsTab", "Scrape Images"))
        self.stopBtn.setText(_translate("EventsTab", "Stop Image Scrape"))
        self.actionsBox.setTitle(_translate("EventsTab", "Actions:"))
        self.ignoreBtn.setText(_translate("EventsTab", "Ignore Event"))
        self.discardBtn.setText(_translate("EventsTab", "Discard Event"))
        self.dataBox.setTitle(_translate("EventsTab", "Vehicle Data:"))
        self.makeLabel.setText(_translate("EventsTab", "Make:"))
        self.modelLabel.setText(_translate("EventsTab", "Model:"))
        self.yearLabel.setText(_translate("EventsTab", "Year:"))
        self.curbWeightLabel.setText(_translate("EventsTab", "Curb Weight (lbs):"))
        self.dmgLocLabel.setText(_translate("EventsTab", "Damage Location:"))
        self.underrideLabel.setText(_translate("EventsTab", "Underride:"))
        self.cBarLabel.setText(_translate("EventsTab", "Avg Crush (in):"))
        self.nassDVLabel.setText(_translate("EventsTab", "NASS Delta-V (mph):"))
        self.nassVCLabel.setText(_translate("EventsTab", "NASS VC (mph):"))
        self.totDVLabel.setText(_translate("EventsTab", "TOT Delta-V (mph): "))
