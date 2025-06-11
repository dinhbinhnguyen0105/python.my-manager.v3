import random
from typing import Any
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.robot import selector_constants as selectors

MIN = 60_000


def close_dialog(page: Page):
    try:
        dialog_locators = page.locator(selectors.S_DIALOG)
        for dialog_locator in dialog_locators.all():
            if dialog_locator.is_visible() and dialog_locator.is_enabled():
                close_button_locators = dialog_locator.locator(selectors.S_CLOSE_BUTTON)
                sleep(random.uniform(0.2, 1.5))
                close_button_locators.last.click(timeout=MIN)
                dialog_locator.wait_for(state="detached", timeout=MIN)
        return True
    except PlaywrightTimeoutError:
        return False
    except Exception as e:
        print(
            f"ERROR: An unexpected error occurred while closing dialog: {e}",
            file=sys.stderr,
        )
        return False


def click_button(
    page: Page, btn_selector: Any, timeout: int
) -> dict:  # Changed return type hint to dict for clarity
    btn_locator = page.locator(btn_selector)

    def try_click_btn(locator: Locator, current_timeout: int) -> dict:
        try:
            locator.wait_for(state="visible", timeout=current_timeout)
            locator.wait_for(state="attached", timeout=current_timeout)
            sleep(random.uniform(0.2, 1.5))
            locator.first.click(timeout=current_timeout)
            return {
                "status": True,
                "message": "Clicked button successfully.",
            }

        except PlaywrightTimeoutError:
            return {
                "status": False,
                "message": f"Could not click button within {current_timeout/1000}s.",
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Unexpected error when clicking button: {e}",
            }

    clicked_result = try_click_btn(btn_locator, timeout)
    if clicked_result["status"]:
        return clicked_result

    close_dialog(page)
    return try_click_btn(btn_locator, timeout)
