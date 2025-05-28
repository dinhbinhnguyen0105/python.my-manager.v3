# src/controllers/setting_controller.py
from typing import List, Optional
from src.controllers.base_controller import BaseController
from src.services.setting_service import SettingProxyService, SettingUserDataDirService
from src.my_types import SettingProxyType, SettingUserDataDirType


class SettingProxyController(BaseController):
    def __init__(self, service: SettingProxyService, parent=None):
        super().__init__(service, parent)

    def create_proxy(self, proxy_data: SettingProxyType):
        try:
            if not isinstance(proxy_data, SettingProxyType):
                raise TypeError(f"Expected SettingProxyType, got {type(proxy_data)}")
            if not self.service.create(proxy_data):
                self.error_signal.emit("Failed to create proxy setting.")
                return False
            self.success_signal.emit("Successfully created proxy setting.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.create_proxy] Error: {e}")
            self.error_signal.emit("Error occurred while creating proxy setting.")
            return False

    def read_proxy(self, record_id: int) -> Optional[SettingProxyType]:
        try:
            proxy = self.service.read(record_id)
            if not proxy:
                self.warning_signal.emit(
                    f"Failed to read proxy setting (id: {record_id})."
                )
                return None
            return proxy
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_proxy] Error: {e}")
            self.error_signal.emit("Error occurred while reading proxy setting.")
            return None

    def read_all_proxies(self) -> List[SettingProxyType]:
        try:
            return self.service.read_all()
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_all_proxies] Error: {e}")
            self.error_signal.emit("Error occurred while reading all proxy settings.")
            return []

    def update_proxy(self, record_id: int, proxy_data: SettingProxyType) -> bool:
        try:
            if not isinstance(proxy_data, SettingProxyType):
                raise TypeError(f"Expected SettingProxyType, got {type(proxy_data)}")
            if not self.service.update(record_id, proxy_data):
                self.error_signal.emit("Failed to update proxy setting.")
                return False
            self.success_signal.emit("Successfully updated proxy setting.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.update_proxy] Error: {e}")
            self.error_signal.emit("Error occurred while updating proxy setting.")
            return False

    def delete_proxy(self, record_id: int) -> bool:
        try:
            if not self.service.delete(record_id):
                self.operation_warning_signal.emit(
                    f"Failed to delete proxy setting (id: {record_id})."
                )
                return False
            self.success_signal.emit(
                f"Successfully deleted proxy setting (id: {record_id})."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_proxy] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting proxy setting."
            )
            return False

    def delete_multiple_proxies(self, record_ids: List[int]) -> bool:
        try:
            self.service.delete_multiple(record_ids)
            self.success_signal.emit("Successfully deleted multiple proxy settings.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_multiple_proxies] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting multiple proxy settings."
            )
            return False

    def import_proxies(self, proxies: List[SettingProxyType]):
        try:
            self.service.import_data(proxies)
            self.success_signal.emit("Successfully imported proxy settings.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.import_proxies] Error: {e}")
            self.error_signal.emit("Error occurred while importing proxy settings.")
            return False


class SettingUserDataDirController(BaseController):
    def __init__(self, service: SettingUserDataDirService, parent=None):
        super().__init__(service, parent)

    def create_user_data_dir(self, data_dir: SettingUserDataDirType):
        try:
            if not isinstance(data_dir, SettingUserDataDirType):
                raise TypeError(
                    f"Expected SettingUserDataDirType, got {type(data_dir)}"
                )
            if not self.service.create(data_dir):
                self.error_signal.emit("Failed to create user data dir setting.")
                return False
            self.success_signal.emit("Successfully created user data dir setting.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.create_user_data_dir] Error: {e}")
            self.error_signal.emit(
                "Error occurred while creating user data dir setting."
            )
            return False

    def read_user_data_dir(self, record_id: int) -> Optional[SettingUserDataDirType]:
        try:
            data_dir = self.service.read(record_id)
            if not data_dir:
                self.warning_signal.emit(
                    f"Failed to read user data dir setting (id: {record_id})."
                )
                return None
            return data_dir
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_user_data_dir] Error: {e}")
            self.error_signal.emit(
                "Error occurred while reading user data dir setting."
            )
            return None

    def read_all_user_data_dirs(self) -> List[SettingUserDataDirType]:
        try:
            return self.service.read_all()
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_all_user_data_dirs] Error: {e}")
            self.error_signal.emit(
                "Error occurred while reading all user data dir settings."
            )
            return []

    def update_user_data_dir(
        self, record_id: int, data_dir: SettingUserDataDirType
    ) -> bool:
        try:
            if not isinstance(data_dir, SettingUserDataDirType):
                raise TypeError(
                    f"Expected SettingUserDataDirType, got {type(data_dir)}"
                )
            if not self.service.update(record_id, data_dir):
                self.error_signal.emit("Failed to update user data dir setting.")
                return False
            self.success_signal.emit("Successfully updated user data dir setting.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.update_user_data_dir] Error: {e}")
            self.error_signal.emit(
                "Error occurred while updating user data dir setting."
            )
            return False

    def delete_user_data_dir(self, record_id: int) -> bool:
        try:
            if not self.service.delete(record_id):
                self.operation_warning_signal.emit(
                    f"Failed to delete user data dir setting (id: {record_id})."
                )
                return False
            self.success_signal.emit(
                f"Successfully deleted user data dir setting (id: {record_id})."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_user_data_dir] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting user data dir setting."
            )
            return False

    def delete_multiple_user_data_dirs(self, record_ids: List[int]) -> bool:
        try:
            self.service.delete_multiple(record_ids)
            self.success_signal.emit(
                "Successfully deleted multiple user data dir settings."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(
                f"[{self.__class__.__name__}.delete_multiple_user_data_dirs] Error: {e}"
            )
            self.operation_error_signal.emit(
                "Error occurred while deleting multiple user data dir settings."
            )
            return False

    def import_user_data_dirs(self, data_dirs: List[SettingUserDataDirType]):
        try:
            self.service.import_data(data_dirs)
            self.success_signal.emit("Successfully imported user data dir settings.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.import_user_data_dirs] Error: {e}")
            self.error_signal.emit(
                "Error occurred while importing user data dir settings."
            )
            return False

    def get_selected_user_data_dir(self):
        try:
            udd = None
            udd = self.service.get_selected()
            self.success_signal.emit(
                "Successfully get selected user data dir settings."
            )
            self.data_changed_signal.emit()
            return udd
        except Exception as e:
            print(f"[{self.__class__.__name__}.get_selected_user_data_dir] Error: {e}")
            self.error_signal.emit("Error occurred while get user data dir setting.")
            return False
