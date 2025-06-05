# src/views/robot/robot_page.py
import os
from typing import List, Optional, Dict
from PyQt6.QtWidgets import QWidget, QLineEdit, QCompleter, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSlot, QStringListModel
from PyQt6.QtGui import QShortcut, QKeySequence

from src.controllers.product_controller import (
    RealEstateProductController,
    RealEstateTemplateController,
)
from src.controllers.user_controller import UserController
from src.controllers.setting_controller import (
    SettingUserDataDirController,
    SettingProxyController,
)

from src.views.utils.multi_field_model import MultiFieldFilterProxyModel
from src.views.robot.action_payload import ActionPayload
from src.ui.page_robot_ui import Ui_PageRobot

from src.utils.re_template import replace_template

from src.my_types import UserType, BrowserType, RealEstateProductType, MiscProductType
from src.my_constants import RE_TRANSACTION


class RobotPage(QWidget, Ui_PageRobot):
    def __init__(
        self,
        user_controller: UserController,
        re_product_controller: RealEstateProductController,
        re_template_controller: RealEstateTemplateController,
        setting_udd_controller: SettingUserDataDirController,
        setting_proxy_controller: SettingProxyController,
        parent=None,
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("User")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._user_controller = user_controller
        self._re_product_controller = re_product_controller
        self._setting_udd_controller = setting_udd_controller
        self._setting_proxy_controller = setting_proxy_controller
        self._re_template_controller = re_template_controller
        self.base_user_model = user_controller.service.model
        self.proxy_model = MultiFieldFilterProxyModel()
        self.proxy_model.setSourceModel(self.base_user_model)

        self.robot_actions: Dict = {}

        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        self.set_user_table()
        self.set_action_tree()
        self.log_message.setHidden(True)

    def setup_events(self):
        self.action_add_btn.clicked.connect(self.on_add_action_clicked)
        self.action_save_btn.clicked.connect(self.on_save_action_clicked)
        self.action_run_btn.clicked.connect(self.on_run_action_clicked)
        shortcut_new_action = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new_action.activated.connect(self.on_add_action_clicked)
        shortcut_save_action = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save_action.activated.connect(self.on_save_action_clicked)
        shortcut_run_action = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_run_action.activated.connect(self.on_run_action_clicked)

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

    def set_pid_completer(self, line_edit: QLineEdit, parent: QWidget):
        suggestions = self._re_product_controller.get_all_pid()
        completer_model = QStringListModel()
        completer_model.setStringList(suggestions)
        completer = QCompleter(parent)
        completer.setModel(completer_model)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        line_edit.setCompleter(completer)

    def fill_actions_tree(self):
        self.actions_tree.clear()
        for uid, actions in self.robot_actions.items():
            if not actions:
                continue
            user_info: UserType = actions[0].user_info
            user_item = QTreeWidgetItem([f"{user_info.username} | {user_info.uid}"])
            for action in actions:
                action_name = (
                    action.action_name
                    if hasattr(action, "action_name")
                    else str(action.get("action_name", ""))
                )
                action_item = QTreeWidgetItem([str(action_name)])
                user_item.addChild(action_item)
            self.actions_tree.addTopLevelItem(user_item)
        self.actions_tree.expandAll()

    def init_browser_task(self):
        pass

    @pyqtSlot()
    def on_add_action_clicked(self):
        self.action_payload_layout.addWidget(ActionPayload(self.set_pid_completer))

    @pyqtSlot()
    def on_save_action_clicked(self):
        selected_users = self.get_selected_users_data()
        re_product = self._re_product_controller.read_all_products()
        products = [].append(re_product)
        if not selected_users:
            return
        action_widgets = self.findChildren(ActionPayload)
        if not action_widgets:
            for selected_user in selected_users:
                if selected_user.uid in self.robot_actions.keys():
                    del self.robot_actions[selected_user.uid]
            self.fill_actions_tree()
            return

        for selected_user in selected_users:
            user_type = selected_user.type.strip().lower()
            self.robot_actions[selected_user.uid] = []

            for action_widget in action_widgets:
                action_value = action_widget.get_values()
                if "pid" in action_value.keys():
                    pid = action_value["pid"]
                    action_payload = {}
                    product = None
                    if not pid or not any(product.pid == pid for product in products):
                        if user_type == "re.s":
                            product = self._re_product_controller.get_random(
                                RE_TRANSACTION["sell"]
                            )
                        elif user_type == "re.r":
                            product = self._re_product_controller.get_random(
                                RE_TRANSACTION["rent"]
                            )
                        elif user_type == "misc.":
                            # TODO get random misc.
                            continue
                    if type(product) == RealEstateProductType:
                        temp_title = self._re_template_controller.get_random(
                            part="title",
                            transaction_type=product.transaction_type,
                            category=product.category,
                        )
                        temp_desc = self._re_template_controller.get_random(
                            part="description",
                            transaction_type=product.transaction_type,
                            category=product.category,
                        )
                        title = replace_template(
                            product_data=product, template=temp_title
                        ).upper()
                        desc = replace_template(
                            product_data=product, template=temp_desc
                        )
                        image_paths = self._re_product_controller.get_images_by_path(
                            product.image_dir
                        )
                        action_payload["title"] = title
                        action_payload["description"] = desc
                        action_payload["image_paths"] = image_paths
                    elif type(product) == MiscProductType:
                        # TODO template misc
                        continue
                elif "content" in action_value.keys():
                    action_payload = action_value["content"]

                self.robot_actions[selected_user.uid].append(
                    BrowserType(
                        user_info=selected_user,
                        action_name=action_value.get("action_name", None),
                        action_payload=action_payload,
                        is_mobile=False,
                        headless=False,
                        udd=os.path.join(
                            self._setting_udd_controller.get_selected_user_data_dir(),
                            str(selected_user.id),
                        ),
                    )
                )
        self.fill_actions_tree()

    @pyqtSlot()
    def on_run_action_clicked(self):
        tasks: List[Optional[BrowserType]] = []
        sorted_uids = sorted(self.robot_actions.keys())
        num_uids = len(sorted_uids)
        max_len = 0
        if self.robot_actions:
            max_len = max(len(actions) for actions in self.robot_actions.values())
        last_uid_contributed: Optional[str] = None

        for i in range(max_len):
            current_column_items_with_uids: List[tuple[Optional[BrowserType], str]] = []
            for uid in sorted_uids:
                if i < len(self.robot_actions[uid]):
                    current_column_items_with_uids.append(
                        (self.robot_actions[uid][i], uid)
                    )
                else:
                    current_column_items_with_uids.append((None, uid))

            for task_obj, current_uid in current_column_items_with_uids:
                if task_obj is not None:
                    if last_uid_contributed is not None:
                        idx_of_last_uid = sorted_uids.index(last_uid_contributed)
                        idx_of_current_uid = sorted_uids.index(current_uid)
                        has_gap_of_skipped_uids = False
                        check_idx = (idx_of_last_uid + 1) % num_uids
                        while check_idx != idx_of_current_uid:
                            if current_column_items_with_uids[check_idx][0] is None:
                                has_gap_of_skipped_uids = True
                                break
                            check_idx = (check_idx + 1) % num_uids
                        if has_gap_of_skipped_uids:
                            tasks.append(None)
                    tasks.append(task_obj)
                    last_uid_contributed = current_uid

        # --- Phần in kết quả để kiểm tra ---
        for task in tasks:
            if task:
                print(f"Action: {task.action_name}, User UID: {task.user_info.uid}")
            else:
                print("--- Empty Slot (None) ---")
        print("\nFinal tasks list length:", len(tasks))

    def handle_run_robot(self):
        pass
