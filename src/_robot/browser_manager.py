# src/robot/browser_manager.py
from typing import List, Dict, Optional
from collections import deque
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal, pyqtSlot, QTimer

from src.robot.browser_worker import BrowserWorker
from src.my_types import BrowserType, BrowserWorkerSignals_, BrowserManagerSignals_


class BrowserManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending_browsers: deque[BrowserType] = deque()
        self._pending_raw_proxies: deque[str] = deque()
        self._in_progress_tasks: Dict[str, dict] = {}
        self._total_task_num: int = 0
        self._settings: Dict[str, str] = {}
        self._waiting_proxies: set[str] = set()
        self._proxy_timer = None
        self._no_proxy_timer = None
        self.manager_signals = BrowserManagerSignals_()
        self.worker_signals = BrowserWorkerSignals_()

        self.worker_signals.info_signal.connect(self.on_info)
        self.worker_signals.warning_signal.connect(self.on_warning)
        self.worker_signals.failed_signal.connect(self.on_failed)
        self.worker_signals.error_signal.connect(self.on_error)
        self.worker_signals.progress_signal.connect(self.on_progress)
        self.worker_signals.finished_signal.connect(self.on_finished)
        self.worker_signals.proxy_unavailable_signal.connect(self.on_proxy_unavailable)
        self.worker_signals.proxy_not_ready_signal.connect(self.on_proxy_not_ready)
        self.worker_signals.require_phone_number_signal.connect(
            self.on_require_phone_number
        )
        self.worker_signals.require_otp_code_signal.connect(self.on_require_otp_code)
        self.threadpool = QThreadPool.globalInstance()

    def add_browsers(
        self, list_browsers: List[BrowserType], list_raw_proxies: List[str]
    ):
        for browser in list_browsers:
            self._pending_browsers.append(browser)
            self._total_browser_num += 1

        for proxy in list_raw_proxies:
            if proxy not in self._pending_raw_proxies:
                self._pending_raw_proxies.append(proxy)

        self.try_start_browsers()

    def try_start_browsers(self):
        available_threads = min(
            self.threadpool.maxThreadCount() - self.threadpool.activeThreadCount(),
            self.settings.get("thread_num", 1),
            len(self._pending_raw_proxies),
        )
        while (
            available_threads > 0
            and self._pending_browsers
            and self._pending_raw_proxies
        ):
            browser = self._pending_browsers.popleft()
            raw_proxy = self._pending_raw_proxies.popleft()
            worker = BrowserWorker(
                browser=browser,
                raw_proxy=raw_proxy,
                settings=self._settings,
                signals=self.worker_signals,
            )
            available_threads -= 1
            if browser:
                self._in_progress_tasks[browser.browser_id] = {
                    "browser": browser,
                    "raw_proxy": raw_proxy,
                    "worker": worker,
                }
            self.threadpool.start(worker)
        if not self._pending_browsers and not self._in_progress_tasks:
            self.manager_signals.finished_signal.emit("All task finished!")

    def is_all_task_finished(self) -> bool:
        return not self._pending_browsers and not self._in_progress_tasks

    # --------------------- setter --------------------- #
    def set_settings(self, settings: dict):
        self._settings = settings.copy()

    # --------------------- BrowserWorkerSignals_ slots --------------------- #
    @pyqtSlot(BrowserType, str)
    def on_info(self, browser: BrowserType, message: str):
        msg = f"ℹ️ [INFO][{browser.user_info.uid}]({browser.action_name}): {message}"
        self.manager_signals.info_signal.emit(msg)

    @pyqtSlot(BrowserType, str)
    def on_warning(self, browser: BrowserType, message: str):
        msg = f"⚠️ [WARNING][{browser.user_info.uid}]({browser.action_name}): {message}"
        self.manager_signals.info_signal.emit(msg)

    @pyqtSlot(BrowserType, str, str)
    def on_failed(self, browser: BrowserType, message: str, raw_proxy: str):
        msg = f"❗ [FAILED][{browser.user_info.uid}]({browser.action_name}): {message}"
        self.manager_signals.failed_signal.emit(msg)
        self._pending_raw_proxies.append(raw_proxy)
        if browser.browser_id in self._in_progress.keys():
            del self._in_progress[browser.browser_id]
        self.try_start_browsers()

    @pyqtSlot(BrowserType, str)
    def on_error(self, browser: BrowserType, message: str):
        msg = f"❌ [ERROR][{browser.user_info.uid}]({browser.action_name}): {message}"
        self.manager_signals.error_signal.emit(msg)

    @pyqtSlot(BrowserType, str, list)
    def on_progress(
        self, browser: BrowserType, message: str, progressing: List[int, int]
    ):
        msg = f"✔️ [PROGRESS][{browser.user_info.uid}]({browser.action_name}): {message}"
        self.manager_signals.progress_singal.emit(msg, progressing)

    @pyqtSlot(object, str, str)
    def on_finished(self, browser: Optional[BrowserType], message: str, raw_proxy: str):
        msg = (
            f"✅ [FINISHED][{browser.user_info.uid}]({browser.action_name}): {message}"
        )
        if browser.browser_id in self._in_progress.keys():
            del self._in_progress[browser.browser_id]
        self._pending_raw_proxies.append(raw_proxy)
        self.manager_signals.finished_signal.emit(msg)
        self.try_start_browsers()

    @pyqtSlot(BrowserType, str)
    def on_proxy_unavailable(self):
        # ⚠️
        pass

    @pyqtSlot(BrowserType, str)
    def on_proxy_not_ready(self):
        # ⚠️
        pass

    @pyqtSlot(BrowserType)
    def on_require_phone_number(self):
        # ❓
        pass

    @pyqtSlot(BrowserType)
    def on_require_otp_code(self):
        # ❓
        pass
