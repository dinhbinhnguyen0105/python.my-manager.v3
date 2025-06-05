# src/views/robot/robot_page.py
from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
)

from src.controllers.user_controller import UserController
from src.controllers.setting_controller import (
    SettingUserDataDirController,
    SettingProxyController,
)

from src.views.utils.multi_field_model import MultiFieldFilterProxyModel
from src.ui.page_robot_ui import Ui_PageRobot

from src.my_types import UserType


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

        self.robot_actions: List[dict] = []

        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        self.set_user_table()
        self.set_action_tree()
        self.log_message.setHidden(True)

    def setup_events(self):
        self.action_add_btn.clicked.connect(self.on_add_action_clicked)

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

    def set_action_tree(self):
        # TODO set actions_tree
        self.actions_tree.clear()
        pass

    def get_selected_ids(self):
        selected_indexes = self.users_table.selectionModel().selectedRows()
        ids = []
        for proxy_index in selected_indexes:
            source_index = self.proxy_model.mapToSource(proxy_index)
            source_model = self.proxy_model.sourceModel()
            id_col = (
                source_model.fieldIndex("id")
                if hasattr(source_model, "fieldIndex")
                else 0
            )
            id_index = source_model.index(source_index.row(), id_col)
            id_value = source_model.data(id_index, Qt.ItemDataRole.DisplayRole)
            ids.append(id_value)
        return sorted(ids)

    def get_selected_users_data(self) -> List[UserType]:
        """
        Retrieves complete UserType data for all selected rows in the users_table.

        Returns:
            List[UserType]: A list of UserType objects representing the selected users.
                            Returns an empty list if no rows are selected or data is unavailable.
        """
        selected_users_data: List[UserType] = []
        selected_proxy_indexes = self.users_table.selectionModel().selectedRows()

        source_model = self.proxy_model.sourceModel()
        if not hasattr(source_model, "record"):
            print(
                "Error: Source model does not support fetching full records. Cannot retrieve UserType data."
            )
            return []

        for proxy_index in selected_proxy_indexes:
            source_index = self.proxy_model.mapToSource(proxy_index)
            row = source_index.row()
            record = source_model.record(row)

            user_data_dict = {}
            for field_info in UserType.__dataclass_fields__.values():
                field_name = field_info.name
                if record.contains(field_name):
                    value = record.value(field_name)
                    if field_info.type == Optional[int] and isinstance(value, str):
                        try:
                            user_data_dict[field_name] = int(value) if value else None
                        except ValueError:
                            user_data_dict[field_name] = None
                    elif field_info.type == Optional[float] and isinstance(value, str):
                        try:
                            user_data_dict[field_name] = float(value) if value else None
                        except ValueError:
                            user_data_dict[field_name] = None
                    else:
                        user_data_dict[field_name] = value
            try:
                user_type_instance = UserType(**user_data_dict)
                selected_users_data.append(user_type_instance)
            except TypeError as e:
                print(f"Error creating UserType instance for row {row}: {e}")
                print(f"Data tried to assign: {user_data_dict}")

        return selected_users_data

    def set_action_tree(self):
        # TODO set actions_tree
        pass

    @pyqtSlot()
    def on_add_action_clicked(self):
        # TODO add action
        pass
