# Form implementation generated from reading ui file '/Volumes/KINGSTON/Dev/python/python.my-manager.v3/ui/action_payload.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ActionPayloadContainer(object):
    def setupUi(self, ActionPayloadContainer):
        ActionPayloadContainer.setObjectName("ActionPayloadContainer")
        ActionPayloadContainer.resize(489, 292)
        ActionPayloadContainer.setStyleSheet("#ActionPayloadContainer{\n"
"  font-family: \"Courier New\";\n"
"  background-color: #FFFFFF;\n"
"  font-size: 13px;\n"
"border: 1px solid #cccccc;\n"
"border-radius: 8px;\n"
"}\n"
"QPushButton{\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"}\n"
"QCheckBox {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"}\n"
"QGroupBox {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  background-color: rgba(248, 249, 250, 1);\n"
"}\n"
"QLineEdit {\n"
"  padding: 4px 0;\n"
"  border: 1px solid #ced4da;\n"
"  border-radius: 8px;\n"
"  background-color: #FFFFFF;\n"
"  color:#212529;\n"
"}\n"
"QPlainTextEdit {\n"
"    background-color: #FFFFFF;\n"
"  color:#212529;\n"
"}\n"
"QLabel {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: rgb(90, 93, 97);\n"
"}\n"
"QRadioButton {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: #212529;\n"
"}\n"
"QComboBox {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: #212529;\n"
"}\n"
"QPushButton {\n"
"  color: #212529;\n"
"}\n"
"\n"
"QCheckBox{\n"
"  color: #212529;\n"
"}")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ActionPayloadContainer)
        self.verticalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.names_combobox = QtWidgets.QComboBox(parent=ActionPayloadContainer)
        self.names_combobox.setObjectName("names_combobox")
        self.horizontalLayout.addWidget(self.names_combobox)
        self.options_combobox = QtWidgets.QComboBox(parent=ActionPayloadContainer)
        self.options_combobox.setObjectName("options_combobox")
        self.horizontalLayout.addWidget(self.options_combobox)
        self.pid_input = QtWidgets.QLineEdit(parent=ActionPayloadContainer)
        self.pid_input.setMinimumSize(QtCore.QSize(120, 0))
        self.pid_input.setStyleSheet("margin: 0 4px;")
        self.pid_input.setObjectName("pid_input")
        self.horizontalLayout.addWidget(self.pid_input)
        self.delete_btn = QtWidgets.QPushButton(parent=ActionPayloadContainer)
        self.delete_btn.setStyleSheet("")
        self.delete_btn.setObjectName("delete_btn")
        self.horizontalLayout.addWidget(self.delete_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.content_container = QtWidgets.QWidget(parent=ActionPayloadContainer)
        self.content_container.setObjectName("content_container")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.content_container)
        self.horizontalLayout_2.setContentsMargins(8, 0, 8, 0)
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.open_images_btn = QtWidgets.QPushButton(parent=self.content_container)
        self.open_images_btn.setObjectName("open_images_btn")
        self.verticalLayout_3.addWidget(self.open_images_btn)
        self.list_images = QtWidgets.QListWidget(parent=self.content_container)
        self.list_images.setObjectName("list_images")
        self.verticalLayout_3.addWidget(self.list_images)
        self.title_line_edit = QtWidgets.QLineEdit(parent=self.content_container)
        self.title_line_edit.setObjectName("title_line_edit")
        self.verticalLayout_3.addWidget(self.title_line_edit)
        self.description_text_edit = QtWidgets.QPlainTextEdit(parent=self.content_container)
        self.description_text_edit.setObjectName("description_text_edit")
        self.verticalLayout_3.addWidget(self.description_text_edit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout.addWidget(self.content_container)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(parent=ActionPayloadContainer)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)

        self.retranslateUi(ActionPayloadContainer)
        QtCore.QMetaObject.connectSlotsByName(ActionPayloadContainer)

    def retranslateUi(self, ActionPayloadContainer):
        _translate = QtCore.QCoreApplication.translate
        ActionPayloadContainer.setWindowTitle(_translate("ActionPayloadContainer", "Form"))
        self.delete_btn.setText(_translate("ActionPayloadContainer", "Delete"))
        self.open_images_btn.setText(_translate("ActionPayloadContainer", "Open images"))
