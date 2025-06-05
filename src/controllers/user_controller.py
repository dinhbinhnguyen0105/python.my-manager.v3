# src/controllers/user_controller.py
from typing import Optional, List
from datetime import datetime
import string, secrets, os
from PyQt6.QtCore import pyqtSlot

from src.controllers.base_controller import BaseController
from src.services.user_service import UserService, UserListedProductService

from src.services.check_live import CheckLive
from src.robot.browser_manager import BrowserManager
from src.my_types import (
    UserType,
    UserListedProductType,
    BrowserType,
)


class UserController(BaseController):

    def __init__(
        self,
        user_service: UserService,
        parent=None,
    ):
        super().__init__(service=user_service, parent=parent)
        self._user_service = user_service
        self._current_check_live_process: Optional[CheckLive] = None
        self._current_browser_progress: Optional[BrowserManager] = None

    def create_user(self, user_data: UserType):
        try:
            if not isinstance(user_data, UserType):
                raise TypeError(f"Expected UserType, got {type(user_data)}")
            if self._user_service.find_by_uid(user_data.uid):
                self.warning_signal.emit(
                    f"User with UID '{user_data.uid}' already exists."
                )
                return False
            if not self._user_service.create(user_data):
                self.error_signal.emit(
                    "Failed to create new user. Check logs for details."
                )
                return False
            else:
                self.success_signal.emit(
                    f"Successfully created new user uid '{user_data.uid}'"
                )
                self.data_changed_signal.emit()
                return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.handle_add_user] Error: {e}")
            self.error_signal.emit(
                "Error occurred while create user. Check logs for details."
            )
            return False

    def read_user(self, record_id: int) -> UserType:
        user_data: Optional[UserType] = None
        try:
            user_data = self._user_service.read(record_id)
            if not user_data:
                self.warning_signal.emit(
                    f"Failed to read user (id: {record_id}). Check logs for details."
                )
                return None
            return user_data
        except Exception as e:
            print(f"[{self.__class__.__name__}.handle_read_user] Error: {e}")
            self.error_signal.emit(
                "Error occurred while create user. Check logs for details."
            )
            return user_data

    def update_user(self, record_id: int, user_data: UserType) -> bool:
        try:
            if not isinstance(user_data, UserType):
                raise TypeError(f"Expected UserType, got {type(user_data)}")
            if not self._user_service.update(record_id, user_data):
                self.error_signal.emit(
                    f"Failed to update user {user_data.uid} (id: {record_id}). Check logs for details."
                )
                return False
            else:
                self.success_signal.emit(f"Successfully update user (id: {record_id}) ")
                return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.handle_read_user] Error: {e}")
            self.error_signal.emit(
                "Error occurred while create user. Check logs for details."
            )
            return False

    def delete_user(self, udd_container, record_id) -> bool:
        try:
            if not self._user_service.delete(udd_container, record_id):
                self.warning_signal.emit(
                    f"Failed to delete user (id: {record_id}). Check logs for details."
                )
                return False
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.handle_read_user] Error: {e}")
            self.error_signal.emit(
                "Error occurred while create user. Check logs for details."
            )
            return False

    def handle_new_desktop_ua(self) -> str:
        return self._user_service.handle_new_desktop_ua()

    def handle_new_mobile_ua(self) -> str:
        return self._user_service.handle_new_mobile_ua()

    def handle_new_time(self) -> str:
        return str(datetime.now())

    def handle_new_password(self) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = "".join(secrets.choice(alphabet) for i in range(30))
        return password

    def update_status(self, record_id: int, current_status: int):
        try:
            result = self._user_service.update_status(record_id, 1 ^ current_status)
            if result:
                self.success_signal.emit(f"Toggled status for user ID {record_id}.")
                self.data_changed_signal.emit()
            else:
                self.warning_signal.emit(
                    f"Failed to toggle status for user ID {record_id}."
                )
            return result
        except Exception as e:
            print(f"[{self.__class__.__name__}.update_status] Error: {e}")
            self.error_signal.emit("Error occurred while toggling user status.")
            return False

    def handle_check_users(self, selected_ids: List[int]) -> bool:
        list_uid = self._user_service.get_uids_by_record_ids(selected_ids)
        if not list_uid:
            # TODO emit message
            return True
        tasks = list(zip(selected_ids, list_uid))

        if (
            self._current_check_live_process
            and not self._current_check_live_process._check_if_done()
        ):
            print(
                f"[{self.__class__.__name__}.handleCheckUsersRequest] Check Live process is already running. Adding tasks to the queue."
            )
            self._current_check_live_process.add_tasks(tasks)
        else:
            print(
                f"[{self.__class__.__name__}.handleCheckUsersRequest] Starting new Check Live process."
            )
            self._current_check_live_process = CheckLive(self)

            self._current_check_live_process.task_succeeded.connect(
                self._on_check_live_task_succeeded
            )
            self._current_check_live_process.task_failed.connect(
                self._on_check_live_task_failed
            )
            self._current_check_live_process.all_tasks_finished.connect(
                self.check_live_all_tasks_finished
            )

            self._current_check_live_process.add_tasks(tasks)

    def handle_launch_browser(
        self,
        record_ids: List[int],
        udd_container: str,
        raw_proxies: List[str],
        is_mobile: bool = False,
        url: str = "",
    ) -> bool:
        if not udd_container:
            self.warning_signal.emit("Please select the user data directory (UDD).")
            return False
        if not raw_proxies:
            self.warning_signal.emit("Please enter proxies to run the browser.")
            return False
        browsers: List[BrowserType] = []
        for record_id in record_ids:
            user_info = self._user_service.read(record_id)
            if user_info:
                browser = BrowserType(
                    user_info=user_info,
                    action_name="launch_browser",
                    action_payload={"url": "http://httpbin.org/ip" if not url else url},
                    udd=os.path.join(udd_container, str(user_info.id)),
                    is_mobile=is_mobile,
                    headless=False,
                )
                browsers.append(browser)
        if (
            self._current_browser_progress
            and not self._current_browser_progress.is_all_browser_finished()
        ):
            print(
                f"[{self.__class__.__name__}.handle_launch_browser] Launching browser is already running. Adding browser to the queue."
            )
            self._current_browser_progress.add_browsers(browsers, raw_proxies)
        else:
            print(
                f"[{self.__class__.__name__}.handle_launch_browser] Starting new launch browser tasks."
            )
            self._current_browser_progress = BrowserManager(self)
            self._current_browser_progress.set_max_worker(len(browsers))
            # self._current_browser_progress.succeeded_signal.connect(
            #     self._on_browser_succeed
            # )
            # self._current_browser_progress.failed_signal.connect(
            #     self._on_browser_failed
            # )
            # self._current_browser_progress.finished.connect(self._on_browsers_finished)
            self._current_browser_progress.succeeded_signal.connect(self.success_signal)
            self._current_browser_progress.error_signal.connect(self.error_signal)
            self._current_browser_progress.warning_signal.connect(self.warning_signal)
            self._current_browser_progress.failed_signal.connect(self.warning_signal)
            self._current_browser_progress.progress_signal.connect(
                self.on_launch_progress
            )
            self._current_browser_progress.finished.connect(self.on_finished)
            self._current_browser_progress.add_browsers(browsers, raw_proxies)

    @pyqtSlot(int, str, bool)
    def _on_check_live_task_succeeded(self, record_id: int, uid: str, is_live: bool):
        print(f"{record_id} - {uid} : {is_live}")
        self._user_service.update_status(record_id, 1 if is_live else 0)

    @pyqtSlot(int, str, str)
    def _on_check_live_task_failed(self, record_id: int, uid: str, error_message: str):
        # self.error_signal.emit(
        #     f"Error occurred while check live user {uid} (id: {record_id}). Check logs for details."
        # )
        print(f"'{uid}': {error_message}")

    @pyqtSlot()
    def check_live_all_tasks_finished(self):
        self.success_signal.emit("User active status check completed.")

    @pyqtSlot(str, int, int)
    def on_launch_progress(
        self, message: str, current_progress: int, total_progress: int
    ):
        self.success_signal.emit(f"{message}")

    @pyqtSlot()
    def on_finished(self):
        print("Finished from controller!")


class UserListedProductController(BaseController):
    def __init__(self, service: UserListedProductService, parent=None):
        super().__init__(service, parent)

    def create_listed_product(self, product_data: UserListedProductType):
        try:
            if not isinstance(product_data, UserListedProductType):
                raise TypeError(
                    f"Expected UserListedProductType, got {type(product_data)}"
                )
            if not self._user_service.create(product_data):
                self.error_signal.emit(
                    "Failed to create listed product. Check logs for details."
                )
                return False
            self.success_signal.emit("Successfully created listed product.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.create_listed_product] Error: {e}")
            self.error_signal.emit(
                "Error occurred while creating listed product. Check logs for details."
            )
            return False

    def read_listed_product(self, record_id: int) -> UserListedProductType:
        try:
            product = self._user_service.read(record_id)
            if not product:
                self.warning_signal.emit(
                    f"Failed to read listed product (id: {record_id})."
                )
                return None
            return product
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_listed_product] Error: {e}")
            self.error_signal.emit(
                "Error occurred while reading listed product. Check logs for details."
            )
            return None

    def read_all_listed_products(self) -> list:
        try:
            return self._user_service.read_all()
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_all_listed_products] Error: {e}")
            self.error_signal.emit("Error occurred while reading all listed products.")
            return []

    def delete_listed_product(self, record_id: int) -> bool:
        try:
            if not self._user_service.delete(record_id):
                self.warning_signal.emit(
                    f"Failed to delete listed product (id: {record_id})."
                )
                return False
            self.success_signal.emit(
                f"Successfully deleted listed product (id: {record_id})."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_listed_product] Error: {e}")
            self.error_signal.emit("Error occurred while deleting listed product.")
            return False

    def delete_multiple_listed_products(self, record_ids: list) -> bool:
        try:
            self._user_service.delete_multiple(record_ids)
            self.success_signal.emit("Successfully deleted multiple listed products.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(
                f"[{self.__class__.__name__}.delete_multiple_listed_products] Error: {e}"
            )
            self.error_signal.emit(
                "Error occurred while deleting multiple listed products."
            )
            return False

    def read_by_user_id(self, user_id: int) -> list:
        try:
            products = self._user_service.read_by_user_id(user_id)
            if products is None:
                self.warning_signal.emit(
                    f"No listed products found for user id {user_id}."
                )
                return []
            return products
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_by_user_id] Error: {e}")
            self.error_signal.emit(
                "Error occurred while reading listed products by user id."
            )
            return []

    def shift_record_by_user_id(self, user_id: int) -> UserListedProductType:
        try:
            product = self._user_service.shift_record_by_user_id(user_id)
            if not product:
                self.warning_signal.emit(
                    f"No listed product to shift for user id {user_id}."
                )
                return None
            self.success_signal.emit(
                f"Successfully shifted listed product for user id {user_id}."
            )
            self.data_changed_signal.emit()
            return product
        except Exception as e:
            print(f"[{self.__class__.__name__}.shift_record_by_user_id] Error: {e}")
            self.error_signal.emit(
                "Error occurred while shifting listed product by user id."
            )
            return None
