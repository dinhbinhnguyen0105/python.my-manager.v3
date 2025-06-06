# src/views/mainwindow.py
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import QTimer

from src.my_types import (
    SettingProxyType,
    SettingUserDataDirType,
    RealEstateTemplateType,
)

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
from src.controllers.robot_controller import RobotController

from src.views.product.real_estate_product_page import RealEstateProductPage
from src.views.user.user_page import UserPage
from src.views.robot.robot_page import RobotPage
from src.views.settings.dialog_settings import DialogSettings
from src.ui.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(
        self,
        user_controller: UserController,
        robot_controller: RobotController,
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
        self._robot_controller = robot_controller

        self.real_estate_product_page = RealEstateProductPage(
            product_controller=self._real_estate_product_controller,
            template_controller=self._real_estate_template_controller,
            setting_controller=self._setting_user_data_dir_controller,
            parent=self,
        )
        self.user_page = UserPage(
            user_controller=self._user_controller,
            setting_udd_controller=self._setting_user_data_dir_controller,
            setting_proxy_controller=self._setting_proxy_controller,
            parent=self,
        )
        self.robot_page = RobotPage(
            robot_controller=self._robot_controller,
            parent=self,
        )

        self.setup_ui()
        self.setup_events()

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
            self._robot_controller,
        ]:
            controller.success_signal.connect(
                lambda message: self.set_status_bar(
                    message=f"Success: {message}", color="#28a745", time_out=1_000
                )
            )
            controller.error_signal.connect(
                lambda message: self.set_status_bar(
                    message=f"Error: {message}", color="#dc3545", time_out=3_000
                )
            )
            controller.warning_signal.connect(
                lambda message: self.set_status_bar(
                    message=f"Warning: {message}", color="#ffc107", time_out=2_000
                )
            )
            controller.info_signal.connect(
                lambda message: self.set_status_bar(
                    message=f"Info: {message}", color="#2196F3", time_out=1_000
                )
            )

    def setup_ui(self):
        self.content_container.addWidget(self.real_estate_product_page)
        self.content_container.addWidget(self.user_page)
        self.content_container.addWidget(self.robot_page)

        self.content_container.setCurrentWidget(self.robot_page)

    def setup_events(self):
        self.sidebar_re_btn.clicked.connect(
            lambda: self.on_sidebar_btn_clicked("real_estate_product")
        )
        self.sidebar_misc_btn.clicked.connect(
            lambda: self.on_sidebar_btn_clicked("misc_product")
        )
        self.sidebar_user_btn.clicked.connect(
            lambda: self.on_sidebar_btn_clicked("user")
        )
        self.sidebar_robot_btn.clicked.connect(
            lambda: self.on_sidebar_btn_clicked("robot")
        )
        self.sidebar_robot_settings.clicked.connect(self.on_robot_settings_clicked)

    @pyqtSlot(str)
    def on_sidebar_btn_clicked(self, page_name: str):
        if page_name == "real_estate_product":
            self.content_container.setCurrentWidget(self.real_estate_product_page)
        # elif page_name == "misc_product":
        #     self.content_container.setCurrentWidget()
        elif page_name == "user":
            self.content_container.setCurrentWidget(self.user_page)
        elif page_name == "robot":
            self.content_container.setCurrentWidget(self.robot_page)

    @pyqtSlot()
    def on_robot_settings_clicked(self):
        dialog_settings = DialogSettings(
            proxy_setting_model=self._setting_proxy_controller.service.model,
            udd_setting_model=self._setting_user_data_dir_controller.service.model,
            re_template_model=self._real_estate_template_controller.service.model,
            parent=self,
        )
        dialog_settings.new_proxy_data_signal.connect(self.handle_create_new_proxy)
        dialog_settings.new_udd_data_signal.connect(
            self.handle_create_new_user_data_dir
        )
        dialog_settings.new_re_template_signal.connect(
            self.handle_create_new_re_template
        )
        dialog_settings.delete_proxy_signal.connect(self.handle_delete_proxy)
        dialog_settings.delete_udd_signal.connect(self.handle_delete_udd)
        dialog_settings.delete_re_template_signal.connect(
            self.handle_delete_re_template
        )
        dialog_settings.set_udd_selected_signal.connect(self.handle_set_udd_selected)
        dialog_settings.re_template_set_default_signal.connect(
            self.handle_set_to_default
        )

        dialog_settings.exec()

    @pyqtSlot(SettingProxyType)
    def handle_create_new_proxy(self, proxy_data: SettingProxyType):
        self._setting_proxy_controller.create_proxy(proxy_data)

    @pyqtSlot(SettingUserDataDirType)
    def handle_create_new_user_data_dir(self, udd_data: SettingUserDataDirType):
        self._setting_user_data_dir_controller.create_user_data_dir(udd_data)

    @pyqtSlot(RealEstateTemplateType)
    def handle_create_new_re_template(self, re_template_data: RealEstateTemplateType):
        self._real_estate_template_controller.create_template(re_template_data)

    @pyqtSlot(int)
    def handle_delete_proxy(self, record_id: int):
        self._setting_proxy_controller.delete_proxy(record_id)

    @pyqtSlot(int)
    def handle_delete_udd(self, record_id: int):
        self._setting_user_data_dir_controller.delete_user_data_dir(record_id)

    @pyqtSlot(int)
    def handle_delete_re_template(self, record_id: int):
        self._real_estate_template_controller.delete_template(record_id=record_id)

    @pyqtSlot(int)
    def handle_set_udd_selected(self, record_id: int):
        self._setting_user_data_dir_controller.set_selected_user_data_dir(
            record_id=record_id
        )

    @pyqtSlot(int)
    def handle_set_to_default(self, record_id: int):
        self._real_estate_template_controller.set_default_template(record_id)

    @pyqtSlot(str, str, int)
    def set_status_bar(self, message: str, color: str, time_out: int):
        label = QLabel(message)
        label.setStyleSheet(f"color: {color};")
        self.status_bar.addWidget(label)
        QTimer.singleShot(time_out, lambda: self.status_bar.removeWidget(label))
