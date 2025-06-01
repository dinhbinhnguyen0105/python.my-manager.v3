# src/views/user/page_user.py
from typing import List, Any, Optional
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QPoint,
    QSortFilterProxyModel,
    QModelIndex,
    QVariant,
    pyqtSlot,
)
from PyQt6.QtGui import QAction

from src.my_types import UserType
from src.controllers.user_controller import UserController
from src.ui.page_user_ui import Ui_PageUser
from src.views.user.dialog_create_user import DialogCreateUser


class MultiFieldFilterProxyModel(QSortFilterProxyModel):
    SERIAL_NUMBER_COLUMN_INDEX = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filters = {}

    def set_filter(self, column, text):
        self.filters[column] = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        for column, text in self.filters.items():
            if text:
                index = model.index(source_row, column, source_parent)
                data = str(model.data(index, Qt.ItemDataRole.DisplayRole)).lower()
                if text not in data:
                    return False
        return True


class UserPage(QWidget, Ui_PageUser):
    def __init__(
        self,
        user_controller: UserController,
        parent=None,
    ):
        super(UserPage, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("User")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._user_controller = user_controller
        self.base_user_model = user_controller.service.model
        self.proxy_model = MultiFieldFilterProxyModel()
        self.proxy_model.setSourceModel(self.base_user_model)

        self.init_ui()
        self.init_events()

    def init_ui(self):
        self.set_user_table()

    def init_events(self):
        self.action_create_btn.clicked.connect(self.on_create_user)
        self.set_filters()
        pass

    def set_user_table(self):
        self.users_table.setModel(self.proxy_model)
        self.users_table.setSortingEnabled(True)
        self.users_table.setSelectionBehavior(
            self.users_table.SelectionBehavior.SelectRows
        )
        self.users_table.setSelectionMode(
            self.users_table.SelectionMode.SingleSelection
        )
        self.users_table.setEditTriggers(self.users_table.EditTrigger.NoEditTriggers)

        # self.users_table.selectionModel().selectionChanged.connect(
        #     self.on_selection_changed
        # )
        for i in range(self.base_user_model.columnCount()):
            column_name = self.base_user_model.headerData(
                i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            )
            if column_name in [
                "id",
                # "status",
                "mobile_ua",
                "desktop_ua",
            ]:
                self.users_table.setColumnHidden(i, True)
        self.users_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.users_table.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos: QPoint):
        proxy_index = self.users_table.indexAt(pos)
        if not proxy_index.isValid():
            return

        # Chuyển sang index của source model
        source_index = self.proxy_model.mapToSource(proxy_index)
        source_model = self.proxy_model.sourceModel()

        # Tìm cột status
        status_col = (
            source_model.fieldIndex("status")
            if hasattr(source_model, "fieldIndex")
            else 0
        )
        status_index = source_model.index(source_index.row(), status_col)
        status_value: int = source_model.data(status_index, Qt.ItemDataRole.DisplayRole)

        id_col = (
            source_model.fieldIndex("id") if hasattr(source_model, "fieldIndex") else 0
        )
        id_index = source_model.index(source_index.row(), id_col)
        id_value = source_model.data(id_index, Qt.ItemDataRole.DisplayRole)

        global_pos = self.users_table.mapToGlobal(pos)
        menu = QMenu(self.users_table)

        set_status_action: Optional[QAction] = None
        if status_value == 1:
            set_status_action = QAction("Change to dead", self)
            set_status_action.triggered.connect(
                lambda _, record_id=id_value, current_status=status_value: self.handle_change_status(
                    record_id,
                    current_status,
                )
            )
        else:
            set_status_action = QAction("Change to live", self)
            set_status_action.triggered.connect(
                lambda _, record_id=id_value, current_status=status_value: self.handle_change_status(
                    record_id,
                    current_status,
                )
            )

        update_action = QAction("Update", self)
        delete_action = QAction("Delete", self)
        launch_as_desktop_action = QAction("Launch as desktop", self)
        launch_as_mobile_action = QAction("Launch as mobile", self)
        check_action = QAction("Check live", self)
        update_action.triggered.connect(
            lambda _, record_id=id_value: self.on_update_product(record_id)
        )
        delete_action.triggered.connect(
            lambda _, record_id=id_value: self.handle_delete_product(record_id)
        )
        menu.addAction(launch_as_desktop_action)
        menu.addAction(launch_as_mobile_action)
        menu.addAction(check_action)
        if set_status_action:
            menu.addAction(set_status_action)
        menu.addAction(update_action)
        menu.addAction(delete_action)
        menu.popup(global_pos)

    def set_filters(self):
        filter_widgets = [
            (self.uid_input, self.base_user_model.fieldIndex("uid")),
            (self.note_input, self.base_user_model.fieldIndex("note")),
            (self.type_input, self.base_user_model.fieldIndex("type")),
            (self.email_input, self.base_user_model.fieldIndex("email")),
            (
                self.email_password_input,
                self.base_user_model.fieldIndex("email_password"),
            ),
            (self.group_input, self.base_user_model.fieldIndex("group")),
            (self.two_fa_input, self.base_user_model.fieldIndex("two_fa")),
            (self.username_input, self.base_user_model.fieldIndex("username")),
            (self.password_input, self.base_user_model.fieldIndex("password")),
            (self.phone_number_input, self.base_user_model.fieldIndex("phone_number")),
        ]

        for widget, column in filter_widgets:
            widget.textChanged.connect(
                lambda text, col=column: self.proxy_model.set_filter(col, text)
            )

    @pyqtSlot()
    def on_create_user(self):
        current_time = self._user_controller.handle_new_time()
        self.create_user_dialog = DialogCreateUser(
            {
                "password": self._user_controller.handle_new_password(),
                "created_at": current_time,
                "updated_at": current_time,
                "user_group": "-1",
                "mobile_ua": self._user_controller.handle_new_mobile_ua(),
                "desktop_ua": self._user_controller.handle_new_desktop_ua(),
            }
        )
        self.create_user_dialog.user_data_signal.connect(self.handle_create_user)
        self.create_user_dialog.show()

    @pyqtSlot(UserType)
    def handle_create_user(self, user_data: UserType):
        self._user_controller.create_user(user_data)

    @pyqtSlot(int, int)
    def handle_change_status(self, record_id: int, current_status: int):
        self._user_controller.update_status(
            record_id=record_id, current_status=current_status
        )

    @pyqtSlot(int)
    def on_update_product(self, record_id: int):
        pass

    @pyqtSlot(int)
    def handle_delete_product(self, record_id: int):
        pass
