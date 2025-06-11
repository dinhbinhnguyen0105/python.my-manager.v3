import random
from typing import Any, List
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.my_types import RobotTaskType, BrowserWorkerSignals
from src.robot import selector_constants as selectors
import sys, traceback

MIN = 60_000


def share_lasted_product(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    test_url = "https://www.facebook.com/marketplace/selling/?listing_id"

    log_prefix = f"[Task {task.user_info.username} - do_launch_browser]"
    progress: List[int] = [0, 4]  # current, total

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    try:
        emit_progress_update("Launching browser...")
        try:
            page.goto(test_url, timeout=MIN)
            emit_progress_update("Successfully navigated to URL.")
        except PlaywrightTimeoutError as e:
            emit_progress_update(f"ERROR: Timeout while navigating to URL.")
            print(
                f"{log_prefix} ERROR: Timeout when navigating to URL: {e}",
                file=sys.stderr,
            )
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False
        except Exception as e:
            if "ERR_ABORTED" in str(e):
                pass  # This is often an expected error when closing the browser.
            else:
                emit_progress_update(
                    f"ERROR: An unexpected error occurred during navigation."
                )
                print(
                    f"{log_prefix} ERROR: An unexpected error occurred during navigation: {e}",
                    file=sys.stderr,
                )

        emit_progress_update("Waiting for browser to close event (if applicable).")
        page.wait_for_event("close", timeout=0)
        emit_progress_update("Browser launched and ready. Waiting for task completion.")
        return True
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        full_traceback = traceback.format_exc()

        print(
            f"{log_prefix} UNEXPECTED ERROR: A general error occurred during task execution:",
            file=sys.stderr,
        )
        print(f"  Error Type: {error_type}", file=sys.stderr)
        print(f"  Message: {error_message}", file=sys.stderr)
        print(f"  Traceback Details:\n{full_traceback}", file=sys.stderr)

        signals.error_signal.emit(
            task,
            f"Unexpected error: {error_message}\nDetails: See console log for full traceback.",
        )
        return False
