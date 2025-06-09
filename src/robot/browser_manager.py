# src/robot/task_manager.py
from typing import List, Dict
from collections import deque
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal, pyqtSlot, QTimer

from src.robot.browser_worker import BrowserWorker
from src.my_types import BrowserType, BrowserWorkerSignals


class BrowserManager(QObject):
    succeeded_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    warning_signal = pyqtSignal(str)
    failed_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str, int, int)
    task_progress_signal = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._max_worker_num: int = 0
        self._pending_browsers: deque[BrowserType] = deque()
        self._pending_raw_proxies: deque[str] = deque()
        self._in_progress: Dict[str, dict] = {}
        self._total_browser_num: int = 0
        self.signals = BrowserWorkerSignals()
        self.settings = {}
        self._waiting_proxies: set[str] = set()
        self._proxy_timer = None
        self._no_proxy_timer = None
        self.signals.progress_signal.connect(self._on_progress)
        self.signals.task_progress_signal.connect(self.task_progress_signal)
        self.signals.failed_signal.connect(self._on_failed)
        self.signals.error_signal.connect(self._on_error)
        self.signals.succeeded_signal.connect(self._on_succeeded)
        self.signals.proxy_unavailable_signal.connect(self._on_proxy_unavailable)
        self.signals.proxy_not_ready_signal.connect(self._on_proxy_not_ready)

        self.threadpool = QThreadPool.globalInstance()

    def set_max_worker(self, max_worker: int):
        self._max_worker_num = max_worker

    def set_settings(self, settings: dict):
        self.settings = settings

    def add_browsers(self, list_browser: List[BrowserType], list_raw_proxy: List[str]):
        existing_uid = set(
            browser.user_info.uid for browser in self._pending_browsers
        ) | set(key for key in self._in_progress.keys())
        add_uid_in_current_call = set()
        for browser in list_browser:
            if (
                browser.user_info.uid not in existing_uid
                and browser.user_info.uid not in add_uid_in_current_call
            ):
                self._pending_browsers.append(browser)
                self._total_browser_num += 1
                add_uid_in_current_call.add(browser.user_info.uid)

        for proxy in list_raw_proxy:
            if proxy not in self._pending_raw_proxies:
                self._pending_raw_proxies.append(proxy)

        self._try_start_browsers()

    def _try_start_browsers(self):
        available_threads = min(
            self.threadpool.maxThreadCount() - self.threadpool.activeThreadCount(),
            self._max_worker_num,
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
                browser,
                raw_proxy,
                self.signals,
                self.settings,
            )
            available_threads -= 1
            self._in_progress[browser.user_info.uid] = {
                "browser": browser,
                "raw_proxy": raw_proxy,
                "worker": worker,
            }
            self.threadpool.start(worker)

        if not self._pending_browsers and not self._in_progress:
            self.handle_all_browser_finished()

    def handle_all_browser_finished(self):
        print("All browser finished!")
        self.finished.emit()

    def is_all_browser_finished(self) -> bool:
        return not self._pending_browsers and not self._in_progress

    @pyqtSlot(BrowserType, str, int, int)
    def _on_progress(
        self,
        browser: BrowserType,
        message: str,
        current_progress: int,
        total_progress: int,
    ):
        msg = f"[Info][{browser.user_info.uid}]({browser.action_name}): {message} ({current_progress}/{total_progress})"
        print(msg)
        self.progress_signal.emit(msg, current_progress, total_progress)

    @pyqtSlot(BrowserType, str, str)
    def _on_failed(self, browser: BrowserType, message: str, raw_proxy):
        msg = (
            f"⚠️ ⚠️ ⚠️ [Failed][{browser.user_info.uid}]({browser.action_name}): {message}"
        )
        print(msg)
        self.failed_signal.emit(msg)
        self._pending_raw_proxies.append(raw_proxy)
        if browser.user_info.uid in self._in_progress.keys():
            del self._in_progress[browser.user_info.uid]
        self._try_start_browsers()

    @pyqtSlot(BrowserType, str)
    def _on_error(
        self,
        browser: BrowserType,
        message: str,
    ):
        msg = f"❌ ❌ ❌ [Error][{browser.user_info.uid}]({browser.action_name}): {message}"
        print(msg)
        self.error_signal.emit(msg)

    @pyqtSlot(BrowserType, str, str)
    def _on_succeeded(
        self,
        browser: BrowserType,
        message: str,
        raw_proxy: str,
    ):
        msg = (
            f"✅ [Succeeded][{browser.user_info.uid}]({browser.action_name}): {message}"
        )
        print(msg)
        self.succeeded_signal.emit(msg)
        self._pending_raw_proxies.append(raw_proxy)
        if browser.user_info.uid in self._in_progress.keys():
            del self._in_progress[browser.user_info.uid]
        self._try_start_browsers()

    @pyqtSlot(BrowserType, str)
    def _on_proxy_unavailable(
        self,
        browser: BrowserType,
        raw_proxy: str,
    ):
        msg = f"[{browser.user_info.uid}] Unavailable proxy ({raw_proxy})"
        print(msg)
        self.warning_signal.emit(msg)
        self._pending_browsers.append(browser)
        self._try_start_browsers()

    @pyqtSlot(BrowserType, str)
    def _on_proxy_not_ready(
        self,
        browser: BrowserType,
        raw_proxy: str,
    ):
        msg = f"[{browser.user_info.uid}] Could not use proxy ({raw_proxy})"
        self.warning_signal.emit(msg)
        print(msg)
        # Loại proxy khỏi deque nếu còn
        try:
            self._pending_raw_proxies.remove(raw_proxy)
        except ValueError:
            pass
        self._waiting_proxies.add(raw_proxy)
        self._pending_browsers.append(browser)
        msg = f"[{browser.user_info.uid}] Attempting to use another proxy."
        self.warning_signal.emit(msg)
        # Nếu không còn proxy nào, đợi 60s rồi thử lại
        if not self._pending_raw_proxies:
            if self._no_proxy_timer is None:
                self._no_proxy_timer = QTimer(self)
                self._no_proxy_timer.setSingleShot(True)
                self._no_proxy_timer.timeout.connect(self._try_start_browsers)
            self._no_proxy_timer.start(10_000)
            msg = f"[{browser.user_info.uid}] No available proxies left. Waiting for 10 seconds."
            self.warning_signal.emit(msg)
        else:
            self._try_start_browsers()

        # Sau 60s, thêm lại proxy vào deque
        timer = QTimer(self)
        timer.setSingleShot(True)

        def readd_proxy():
            self._pending_raw_proxies.append(raw_proxy)
            self._waiting_proxies.discard(raw_proxy)
            self._try_start_browsers()
            timer.deleteLater()

        timer.timeout.connect(readd_proxy)
        timer.start(10_000)
