# src/robot/browser_worker.py
from time import sleep
from typing import Optional
import io, pycurl, json
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from undetected_playwright import Tarnished

from PyQt6.QtCore import QRunnable

from src.my_types import BrowserWorkerSignals, BrowserType
from src.robot.action_mapping import ACTION_MAP
from src.my_constants import ROBOT_ACTION_NAMES


class BrowserWorker(QRunnable):
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
        self._settings = settings
        self._settings["raw_proxy"] = self._raw_proxy

        self.setAutoDelete(True)

    def run(self):
        proxy = self.handle_get_proxy()
        if proxy and self._browser.action_name in ACTION_MAP.keys():
            try:
                action_func = ACTION_MAP[self._browser.action_name]
                if self._browser.action_name == "share_latest_product":
                    self._browser.is_mobile = True
                is_succeeded = False
                with sync_playwright() as p:
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
                    context = p.chromium.launch_persistent_context(**context_kwargs)
                    Tarnished.apply_stealth(context)
                    pages = context.pages
                    if pages:
                        current_page = pages[0]
                    else:
                        current_page = context.new_page()
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

                    page = context.new_page()
                    print(
                        f"[Info] Opened Chromium for user: {self._browser.user_info.username}"
                    )
                    if self._browser.action_name == "launch_browser":
                        is_succeeded = action_func(
                            page, self._browser, self._settings, self._signals
                        )
                    elif self._browser.action_name in ROBOT_ACTION_NAMES.keys():
                        is_succeeded = action_func(
                            page, self._browser, self._settings, self._signals
                        )
                sleep(self._settings.get("delay_time", 0))

                if not is_succeeded:
                    self._signals.failed_signal.emit(
                        self._browser,
                        "Failed",
                        self._raw_proxy,
                    )
                else:
                    self._signals.succeeded_signal.emit(
                        self._browser,
                        "Succeeded",
                        self._raw_proxy,
                    )

            except Exception as e:
                self._signals.error_signal.emit(self._browser, str(e))

    def handle_get_proxy(self):
        try:
            res = self._get_proxy(self._raw_proxy)
            if int(res.get("status")) == 100:
                proxy = res.get("data")
            elif int(res.get("status")) == 101:
                proxy = None
                msg = f"[{self._browser.user_info.uid}] Not ready proxy ({self._raw_proxy})"
                # sleep(60)
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

    def _get_proxy(self, proxy_raw: str) -> dict:
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, proxy_raw)
        curl.setopt(pycurl.CONNECTTIMEOUT, 60)
        curl.setopt(pycurl.TIMEOUT, 60)
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept: application/json, text/plain, */*",
            "Accept-Language: en-US,en;q=0.9",
            "Referer: https://proxyxoay.shop/",
            "Connection: keep-alive",
        ]
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.perform()
        try:
            code = curl.getinfo(pycurl.RESPONSE_CODE)
            if code != 200:
                return {"status": code, "message": "Error fetching proxy"}
            body = buffer.getvalue().decode("utf-8")
            res = json.loads(body)
            data = None
            parsed_url = urlparse(proxy_raw)
            domain = parsed_url.netloc
            if domain == "proxyxoay.shop":
                if res.get("status") == 100 and "proxyhttp" in res:
                    raw = res["proxyhttp"]
                    ip, port, user, pwd = raw.split(":", 3)
                    data = {
                        "username": user,
                        "password": pwd,
                        "server": f"{ip}:{port}",
                    }
            else:
                raise Exception(f"Invalid domain ({domain})")

            return {
                "data": data,
                "status": res.get("status"),
                "message": res.get("message"),
            }
        except Exception as e:
            raise Exception(e)
