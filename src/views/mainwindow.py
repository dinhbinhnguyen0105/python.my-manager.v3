# src/views/mainwindow.py
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QMainWindow

from src.controllers.user_controller import UserController, UserListedProductController
from src.controllers.product_controller import (
    RealEstateProductController,
    RealEstateTemplateController,
    MiscProductController,
)
from src.controllers.setting_controller import (
    SettingProxyController,
    SettingUserDataDirController,
)

from src.ui.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(
        self,
        user_controller: UserController,
        user_listed_product_controller: UserListedProductController,
        real_estate_product_controller: RealEstateProductController,
        real_estate_template_controller: RealEstateTemplateController,
        misc_product_controller: MiscProductController,
        setting_proxy_controller: SettingProxyController,
        setting_user_data_dir_controller: SettingUserDataDirController,
        parent=None,
    ):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("My manager")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(960, 540)

        self._user_controller = user_controller
        self._user_listed_product_controller = user_listed_product_controller
        self._real_estate_product_controller = real_estate_product_controller
        self._real_estate_template_controller = real_estate_template_controller
        self._misc_product_controller = misc_product_controller
        self._setting_proxy_controller = setting_proxy_controller
        self._setting_user_data_dir_controller = setting_user_data_dir_controller

        self.set_status_bar_message()

    def set_status_bar_message(self):
        self.status_bar.showMessage("My manager application is running ...", 2000)
        for controller in [
            self._user_controller,
            self._user_listed_product_controller,
            self._real_estate_product_controller,
            self._real_estate_template_controller,
            self._misc_product_controller,
            self._setting_proxy_controller,
            self._setting_user_data_dir_controller,
        ]:
            controller.success_signal.connect(
                lambda message: self.status_bar.showMessage(
                    f"Success: {message}.", 1000
                )
            )
            controller.error_signal.connect(
                lambda message: self.status_bar.showMessage(f"Error: {message}.", 1000)
            )
            controller.warning_signal.connect(
                lambda message: self.status_bar.showMessage(
                    f"Warning: {message}.", 1000
                )
            )
            controller.info_signal.connect(
                lambda message: self.status_bar.showMessage(f"Info: {message}.", 1000)
            )
