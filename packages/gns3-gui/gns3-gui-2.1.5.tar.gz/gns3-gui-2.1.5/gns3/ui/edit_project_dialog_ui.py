# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/edit_project_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditProjectDialog(object):
    def setupUi(self, EditProjectDialog):
        EditProjectDialog.setObjectName("EditProjectDialog")
        EditProjectDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        EditProjectDialog.resize(955, 387)
        EditProjectDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(EditProjectDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiSceneWidthLabel = QtWidgets.QLabel(EditProjectDialog)
        self.uiSceneWidthLabel.setObjectName("uiSceneWidthLabel")
        self.gridLayout.addWidget(self.uiSceneWidthLabel, 1, 0, 1, 1)
        self.uiSceneHeightLabel = QtWidgets.QLabel(EditProjectDialog)
        self.uiSceneHeightLabel.setObjectName("uiSceneHeightLabel")
        self.gridLayout.addWidget(self.uiSceneHeightLabel, 2, 0, 1, 1)
        self.uiProjectAutoStartCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoStartCheckBox.setObjectName("uiProjectAutoStartCheckBox")
        self.gridLayout.addWidget(self.uiProjectAutoStartCheckBox, 7, 0, 1, 3)
        self.uiProjectAutoCloseCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoCloseCheckBox.setObjectName("uiProjectAutoCloseCheckBox")
        self.gridLayout.addWidget(self.uiProjectAutoCloseCheckBox, 8, 0, 1, 3)
        self.uiProjectNameLineEdit = QtWidgets.QLineEdit(EditProjectDialog)
        self.uiProjectNameLineEdit.setObjectName("uiProjectNameLineEdit")
        self.gridLayout.addWidget(self.uiProjectNameLineEdit, 0, 1, 1, 1)
        self.uiProjectNameLabel = QtWidgets.QLabel(EditProjectDialog)
        self.uiProjectNameLabel.setObjectName("uiProjectNameLabel")
        self.gridLayout.addWidget(self.uiProjectNameLabel, 0, 0, 1, 1)
        self.uiGridSizeLabel = QtWidgets.QLabel(EditProjectDialog)
        self.uiGridSizeLabel.setObjectName("uiGridSizeLabel")
        self.gridLayout.addWidget(self.uiGridSizeLabel, 3, 0, 1, 1)
        self.uiSceneWidthSpinBox = QtWidgets.QSpinBox(EditProjectDialog)
        self.uiSceneWidthSpinBox.setMinimum(500)
        self.uiSceneWidthSpinBox.setMaximum(1000000)
        self.uiSceneWidthSpinBox.setObjectName("uiSceneWidthSpinBox")
        self.gridLayout.addWidget(self.uiSceneWidthSpinBox, 1, 1, 1, 1)
        self.uiSceneHeightSpinBox = QtWidgets.QSpinBox(EditProjectDialog)
        self.uiSceneHeightSpinBox.setMinimum(500)
        self.uiSceneHeightSpinBox.setMaximum(1000000)
        self.uiSceneHeightSpinBox.setObjectName("uiSceneHeightSpinBox")
        self.gridLayout.addWidget(self.uiSceneHeightSpinBox, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 0, 1, 1)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(EditProjectDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridLayout.addWidget(self.uiButtonBox, 9, 0, 1, 3)
        self.uiProjectAutoOpenCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoOpenCheckBox.setObjectName("uiProjectAutoOpenCheckBox")
        self.gridLayout.addWidget(self.uiProjectAutoOpenCheckBox, 6, 0, 1, 3)
        self.uiGridSizeSpinBox = QtWidgets.QSpinBox(EditProjectDialog)
        self.uiGridSizeSpinBox.setObjectName("uiGridSizeSpinBox")
        self.gridLayout.addWidget(self.uiGridSizeSpinBox, 3, 1, 1, 1)

        self.retranslateUi(EditProjectDialog)
        self.uiButtonBox.accepted.connect(EditProjectDialog.accept)
        self.uiButtonBox.rejected.connect(EditProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditProjectDialog)

    def retranslateUi(self, EditProjectDialog):
        _translate = QtCore.QCoreApplication.translate
        EditProjectDialog.setWindowTitle(_translate("EditProjectDialog", "Edit project"))
        self.uiSceneWidthLabel.setText(_translate("EditProjectDialog", "Scene width:"))
        self.uiSceneHeightLabel.setText(_translate("EditProjectDialog", "Scene height:"))
        self.uiProjectAutoStartCheckBox.setText(_translate("EditProjectDialog", "Start all nodes when this project is opened"))
        self.uiProjectAutoCloseCheckBox.setText(_translate("EditProjectDialog", "Leave this project running in the background when closing GNS3"))
        self.uiProjectNameLabel.setText(_translate("EditProjectDialog", "Project Name:"))
        self.uiGridSizeLabel.setText(_translate("EditProjectDialog", "Grid size:"))
        self.uiSceneWidthSpinBox.setSuffix(_translate("EditProjectDialog", " px"))
        self.uiSceneHeightSpinBox.setSuffix(_translate("EditProjectDialog", " px"))
        self.uiProjectAutoOpenCheckBox.setText(_translate("EditProjectDialog", "Open this project in the background when GNS3 server starts"))

