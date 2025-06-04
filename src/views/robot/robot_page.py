# src/views/robot/robot_page.py
from typing import Optional
from PyQt6.QtWidgets import QWidget, QMenu, QMessageBox
from PyQt6.QtCore import (
    Qt,
    QPoint,
    QSortFilterProxyModel,
    pyqtSlot,
)

from src.controllers.user_controller import UserController
from src.controllers.setting_controller import (
    SettingUserDataDirController,
    SettingProxyController,
)

from src.views.utils.multi_field_model import MultiFieldFilterProxyModel
from src.ui.page_robot_ui import Ui_PageRobot


class RobotPage(QWidget, Ui_PageRobot):
    def __init__(
        self,
        user_controller: UserController,
        setting_udd_controller: SettingUserDataDirController,
        setting_proxy_controller: SettingProxyController,
        parent=None,
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("User")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._user_controller = user_controller
        self._setting_udd_controller = setting_udd_controller
        self._setting_proxy_controller = setting_proxy_controller
        self.base_user_model = user_controller.service.model
        self.proxy_model = MultiFieldFilterProxyModel()
        self.proxy_model.setSourceModel(self.base_user_model)

        self.setup_ui()

    def setup_ui(self):
        self.set_user_table()
        self.log_message.setHidden(True)

    def set_user_table(self):
        self.users_table.setModel(self.proxy_model)
        self.users_table.setSortingEnabled(True)
        self.users_table.setSelectionBehavior(
            self.users_table.SelectionBehavior.SelectRows
        )
        self.users_table.setEditTriggers(self.users_table.EditTrigger.NoEditTriggers)
        for i in range(self.base_user_model.columnCount()):
            column_name = self.base_user_model.headerData(
                i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            )
            if column_name not in ["uid", "username", "note", "type", "user_group"]:
                self.users_table.setColumnHidden(i, True)
