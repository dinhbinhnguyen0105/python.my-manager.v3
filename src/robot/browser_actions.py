# src/robot/browser_actions.py
from playwright.sync_api import Page
from src.my_types import RobotTaskType, BrowserWorkerSignals


def do_launch_browser(page: Page, task: RobotTaskType, signals: BrowserWorkerSignals):
    try:
        signals.progress_signal.emit(task, "Launching ...", 0, 1)
        page.goto(task.action_payload.get("url", ""), wait_until="networkidle")
        page.wait_for_event("close", timeout=0)
        signals.progress_signal.emit(task, "Closed!", 1, 1)
    except Exception as e:
        signals.error_signal.emit(task, str(e))


ACTION_MAP = {
    "launch_browser": do_launch_browser,
}
