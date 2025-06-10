# src/views/robot/dialog_run_bot.py
from typing import Dict
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QIntValidator

from src.ui.dialog_robot_run_ui import Ui_Dialog_RobotRun


class DialogRobotRun(QDialog, Ui_Dialog_RobotRun):
    setting_data_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(f"Run settings")

        self.thread_num_input.setValidator(QIntValidator())
        self.group_num_input.setValidator(QIntValidator())
        self.delay_time_input.setValidator(QIntValidator())

        self.buttonBox.accepted.disconnect()
        self.buttonBox.accepted.connect(self.handle_run)

    def handle_run(self):
        self.setting_data_signal.emit(
            {
                "is_mobile": self.is_mobile_checkbox.isChecked(),
                "headless": self.is_headless_checkbox.isChecked(),
                "thread_num": self.thread_num_input.text(),
                "group_num": self.group_num_input.text(),
                "delay_num": self.delay_time_input.text(),
            }
        )
        self.accept()
