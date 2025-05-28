# src/views/settings/dialog_settings.py
from typing import List
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QPoint
from PyQt6.QtWidgets import QDialog, QMenu
from PyQt6.QtGui import QAction

from src.models.setting_model import SettingProxyModel, SettingUserDataDirModel

from src.ui.dialog_settings_ui import Ui_Dialog_Settings
from src.my_types import SettingProxyType, SettingUserDataDirType


class DialogSettings(QDialog, Ui_Dialog_Settings):
    new_proxy_data_signal = pyqtSignal(SettingProxyType)
    new_udd_data_signal = pyqtSignal(SettingUserDataDirType)
    delete_proxy_signal = pyqtSignal(int)
    delete_udd_signal = pyqtSignal(int)
    set_proxy_selected_signal = pyqtSignal(int)

    def __init__(
        self,
        proxy_setting_model: SettingProxyModel,
        udd_setting_model: SettingUserDataDirModel,
        parent=None,
    ):
        super(DialogSettings, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Real estate product")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(False)

        self.buttonBox.button(self.buttonBox.StandardButton.Cancel).clicked.connect(
            self.accept
        )

        self._proxy_setting_model = proxy_setting_model
        self._udd_setting_model = udd_setting_model

        self.current_setting_option = None

        self.udd_container.setHidden(True)
        self.proxy_container.setHidden(True)
        # self.udd_radio
        # self.proxy_radio
        # self.fields_container.setHidden(True)
        # self.udd_is_selected_checkbox
        # self.tableView

        self.init_events()

    def init_ui(self):

        pass

    def init_events(self):
        self.udd_radio.clicked.connect(lambda: self.on_setting_option_clicked("udd"))
        self.proxy_radio.clicked.connect(
            lambda: self.on_setting_option_clicked("proxy")
        )

    def set_table_ui(self):
        self.tableView.setSortingEnabled(True)
        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos: QPoint):
        global_pos = self.products_table.mapToGlobal(pos)
        menu = QMenu(self.products_table)
        selected_action = QAction("Select", self)
        delete_action = QAction("Delete", self)

        selected_action.triggered.connect(self.handle_edit)
        delete_action.triggered.connect(self.handle_delete)

        menu.addAction(selected_action)
        menu.addAction(delete_action)

        menu.popup(global_pos)

    @pyqtSlot(str)
    def on_setting_option_clicked(self, setting_option_name: str):
        self.current_setting_option = setting_option_name
        self.udd_container.setVisible("udd" == setting_option_name)
        self.proxy_container.setVisible("proxy" == setting_option_name)

        if "udd" == setting_option_name:
            self.tableView.setModel(self._udd_setting_model)
        if "proxy" == setting_option_name:
            self.tableView.setModel(self._proxy_setting_model)
        self.tableView.hideColumn(0)

    @pyqtSlot()
    def on_save_clicked(self):
        if "udd" == self.current_setting_option:
            self.new_udd_data_signal.emit(
                SettingUserDataDirType(
                    id=None,
                    value=self.udd_input.text(),
                    is_selected=int(self.udd_is_selected_checkbox.isChecked()),
                    created_at=None,
                    updated_at=None,
                )
            )
        elif "proxy" == self.current_setting_option:
            self.new_proxy_data_signal.emit(
                SettingProxyType(
                    id=None,
                    value=self.proxy_input.text(),
                    created_at=None,
                    updated_at=None,
                )
            )
        else:
            return

    @pyqtSlot(int)
    def on_deleted_clicked(self, record_id: int):
        self.

        if "udd" == self.current_setting_option:
            self.delete_udd_signal.emit(record_id)
        elif "proxy" == self.current_setting_option:
            self.delete_proxy_signal.emit(record_id)
        else:
            return

    @pyqtSlot(int)
    def on_set_selected(self, record_id: int):
        self.set_proxy_selected_signal.emit(record_id)
        pass


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication([])
    dialog = DialogSettings(
        SettingProxyModel(),
        SettingUserDataDirModel(),
    )
    dialog.show()
    sys.exit(app.exec())
