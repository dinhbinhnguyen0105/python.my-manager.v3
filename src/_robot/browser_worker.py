# src/robot/browser_worker_2.py
import threading
from time import sleep
from typing import Optional, Dict
import io, pycurl, json
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from undetected_playwright import Tarnished

from PyQt6.QtCore import QRunnable

from src.my_types import BrowserWorkerSignals, BrowserType
from src.robot.action_mapping import ACTION_MAP
from src.my_constants import ROBOT_ACTION_NAMES
from src.utils.get_proxy import get_proxy

UDD_LOCKS = {}


class BrowserWorker_2(QRunnable):
    def __init__(
        self,
        browser: BrowserType,
        raw_proxy: str,
        signals: BrowserWorkerSignals,
        settings: Optional[dict] = {},
    ):
        super().__init__()
        self._browser = browser
        self._raw_proxy = raw_proxy
        self._signals = signals
        self._settings = settings.copy()
        self._settings["raw_proxy"] = self._raw_proxy
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.setAutoDelete(True)

    def run(self):
        udd = self.browser_obj.udd
        if udd not in UDD_LOCKS:
            UDD_LOCKS[udd] = threading.Lock()

        with UDD_LOCKS[udd]:
            proxy = self.BrowserWorker_2__handle_get_proxy()
            self.playwright = sync_playwright().start()
            context_kwargs = dict(
                user_data_dir=self._browser.udd,
                user_agent=(
                    self._browser.user_info.mobile_ua
                    if self._browser.is_mobile
                    else self._browser.user_info.desktop_ua
                ),
                headless=self._browser.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    f'--app-name=Chromium - {self._browser.user_info.username or "Unknown User"}',
                ],
                ignore_default_args=["--enable-automation"],
                proxy=proxy,
            )
            if self._browser.is_mobile:
                context_kwargs["viewport"] = {"width": 390, "height": 844}
                context_kwargs["screen"] = {"width": 390, "height": 844}
                context_kwargs["is_mobile"] = True
                context_kwargs["device_scale_factor"] = 3
                context_kwargs["has_touch"] = False
            else:
                context_kwargs["viewport"] = {"width": 960, "height": 844}
                context_kwargs["screen"] = {"width": 960, "height": 844}
                context_kwargs["is_mobile"] = False
                context_kwargs["device_scale_factor"] = 3
                context_kwargs["has_touch"] = True

            if proxy and self._browser.action_name in ACTION_MAP:
                if self._browser.action_name == "share_latest_product":
                    self._browser.is_mobile = True
                # TODO config for specific action_name

                self.context = self.playwright.chromium.launch_persistent_context(
                    **context_kwargs
                )
                Tarnished.apply_stealth(self.context)
                pages = self.context.pages()
                if pages:
                    current_page = pages[0]
                else:
                    current_page = self.context.new_page()
                info_html = f"""
                <html>
                    <head><title>{self._browser.user_info.username}</title></head>
                    <body>
                        <h2>username: {self._browser.user_info.username}</h2>
                        <p>id: {self._browser.user_info.id}</p>
                        <p>uid: {self._browser.user_info.uid}</p>
                        <p>user_data_dir: {self._browser.udd}</p>
                    </body>
                </html>
                """
                current_page.set_content(info_html)
                self.page = self.context.new_page()
                print(
                    f"[Info] Opened Chromium for user: {self._browser.user_info.username}"
                )

                self.run_next_step()

    def BrowserWorker_2__handle_get_proxy(self):
        try:
            res = get_proxy(self._raw_proxy)
            if int(res.get("status")) == 100:
                proxy = res.get("data")
            elif int(res.get("status")) == 101:
                proxy = None
                msg = f"[{self._browser.user_info.uid}] Not ready proxy ({self._raw_proxy})"
                self._signals.proxy_not_ready_signal.emit(
                    self._browser, self._raw_proxy
                )
            elif int(res.get("status")) == 102:
                proxy = None
                self._signals.proxy_unavailable_signal.emit(
                    self._browser, self._raw_proxy
                )
            return proxy
        except Exception as e:
            self._signals.error_signal.emit(
                self._browser,
                f"An error occurred while fetching proxy: {e}",
            )
