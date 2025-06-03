# src/robot/browser_worker.py
from time import sleep
from typing import Optional
import io, pycurl, json
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from undetected_playwright import Tarnished

from PyQt6.QtCore import QRunnable

from my_types import RobotTaskType, BrowserWorkerSignals
from src.robot.browser_actions import ACTION_MAP


class BrowserWorker(QRunnable):
    def __init__(
        self,
        task: RobotTaskType,
        raw_proxy: str,
    ):
        super().__init__()
        self._task = task
        self._raw_proxy = raw_proxy
        self._signals = BrowserWorkerSignals()
        self.setAutoDelete(True)

    def run(self):
        proxy = self.handle_get_proxy()
        if proxy and self._task.action_name in ACTION_MAP.keys():
            try:
                action_func = ACTION_MAP[self.task.action_name]
                with sync_playwright() as p:
                    context = p.chromium.launch_persistent_context(
                        user_data_dir=self.task.udd,
                        user_agent=(
                            self.task.user_info.mobile_ua
                            if self.task.is_mobile
                            else self.task.user_info.desktop_ua
                        ),
                        headless=self.task.headless,
                        args=["--disable-blink-features=AutomationControlled"],
                        ignore_default_args=["--enable-automation"],
                        proxy=proxy,
                    )
                    Tarnished.apply_stealth(context)
                    page = context.new_page()
                    if self.task.action_name == "launch_browser":
                        action_func(page, self.task, self._signals)

                self._signals.succeeded_signal.emit(
                    self.task,
                    "Succeeded.",
                    self.raw_proxy,
                )
            except Exception as e:
                self._signals.error_signal.emit(self.task, str(e))

    def handle_get_proxy(self):
        try:
            res = self._get_proxy(self.raw_proxy)
            if int(res.get("status")) == 100:
                proxy = res.get("data")
            elif int(res.get("status")) == 101:
                proxy = None
                print(f"[{self.task.user_info.uid}] Not ready proxy ({self.raw_proxy})")
                sleep(60)
                self._signals.proxy_not_ready_signal.emit(self.task, self.raw_proxy)
            elif int(res.get("status")) == 102:
                proxy = None
                self._signals.proxy_unavailable_signal.emit(self.task, self.raw_proxy)
            return proxy
        except Exception as e:
            self._signals.error_signal.emit(
                self.task,
                f"An error occurred while fetching proxy: {e}",
            )

    def _get_proxy(self, proxy_raw: str) -> dict:
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, proxy_url)
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
            parsed_url = urlparse(proxy_url)
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
