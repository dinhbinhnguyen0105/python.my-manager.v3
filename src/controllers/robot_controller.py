# src/controllers/controller_robot.py
import os
from typing import Optional, List

from PyQt6.QtCore import pyqtSlot

from src.my_types import RobotTaskType
from src.controllers.base_controller import BaseController
from src.services.service_robot import RobotService
from src.services.service_user import (
    UserService,
    UserSettingProxyService,
    UserSettingUDDService,
)


class RobotController(BaseController):
    def __init__(
        self,
        service: UserService,
        proxy_service: UserSettingProxyService,
        udd_service: UserSettingUDDService,
        parent=None,
    ):
        super().__init__(service, parent)
        self.service = service
        self._current_task_progress: Optional[RobotService] = None
        self.proxy_service = proxy_service
        self.udd_service = udd_service

    def handle_launch_browser(
        self, record_ids: List[int], headless: bool, is_mobile: bool
    ):
        udd_container = self._get_udd_container()
        if not udd_container:
            return False
        proxies = self._get_proxies()
        if not proxies:
            return False
        tasks: List[RobotTaskType] = []
        for record_id in record_ids:
            user_info = self.service.read(record_id)
            if user_info:
                task = RobotTaskType(
                    user_info=user_info,
                    udd=os.path.join(
                        udd_container,
                        str(user_info.id),
                    ),
                    headless=headless,
                    is_mobile=is_mobile,
                    action_name="launch_browser",
                    action_payload={"url": "http://httpbin.org/ip"},
                )
                tasks.append(task)
        if (
            self._current_task_progress
            and not self._current_task_progress.check_if_done()
        ):
            print(
                f"[{self.__class__.__name__}.handle_launch_browser] Launching browser is already running. Adding task to the queue."
            )
            self._current_task_progress.add_tasks(tasks, proxies)
        else:
            print(
                f"[{self.__class__.__name__}.handle_launch_browser] Starting new launch browser tasks."
            )
            self._current_task_progress = RobotService(self)
            self._current_task_progress.set_max_worker(len(record_ids))
            self._current_task_progress.task_succeeded_signal.connect(
                self.on_task_succeeded
            )
            self._current_task_progress.task_failed_signal.connect(self.on_task_failed)
            self._current_task_progress.all_task_finished.connect(
                self.on_tasks_finished
            )

            self._current_task_progress.add_tasks(
                tasks,
                proxies,
            )

    @pyqtSlot(RobotTaskType)
    def on_task_succeeded(self, task: RobotTaskType):
        pass

    @pyqtSlot(RobotTaskType)
    def on_task_failed(self, task: RobotTaskType):
        pass

    @pyqtSlot()
    def on_tasks_finished(self):
        self.operation_success_signal.emit("All tasks finished successfully.")

    def _get_udd_container(self):
        udd_selected = self.udd_service.get_selected()
        if not udd_selected:
            self.operation_warning_signal.emit("Please selecte a user data dir.")
            return False
        udd_container = os.path.abspath(udd_selected)
        if not os.path.exists(udd_container):
            self.operation_warning_signal.emit(
                "The path containing the user data dir is not accessible."
            )
            return False
        return udd_container

    def _get_proxies(self):
        proxy_infos = self.proxy_service.read_all()
        if not proxy_infos:
            self.operation_warning_signal.emit("Proxy list is empty.")
            return False
        proxies = []
        for proxy_info in proxy_infos:
            proxies.append(proxy_info.value)
        return proxies
