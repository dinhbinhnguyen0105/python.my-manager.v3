# src/robot/browser_actions.py
import random, traceback, sys
from typing import Any, Callable
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.my_types import RobotTaskType, BrowserWorkerSignals
from src.robot import selector_constants as selectors

MIN = 60_000


def do_launch_browser(page: Page, task: RobotTaskType, signals: BrowserWorkerSignals):
    try:
        signals.progress_signal.emit(task, "Launching ...", 0, 1)
        # page.goto(task.action_payload.get("url", ""), timeout=MIN)
        page.wait_for_event("close", timeout=0)
        signals.progress_signal.emit(task, "Closed!", 1, 1)
        return True
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


def do_marketplace(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    try:
        print(settings)
        total_progress = 10
        msg = f"[{task.user_info.username}] Performing {task.action_name}"
        signals.progress_signal.emit(task, msg, 0, total_progress)
        is_listed_on_marketplace = handle_list_on_marketplace(
            page, task, signals, total_progress
        )
        return is_listed_on_marketplace
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


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


def click_button(page: Page, btn_selector: Any, timeout: int) -> bool:
    btn_locator = page.locator(btn_selector)

    def try_click_btn(locator: Locator, current_timeout: int) -> bool:
        try:
            locator.wait_for(state="visible", timeout=current_timeout)
            locator.wait_for(state="attached", timeout=current_timeout)
            sleep(random.uniform(0.2, 1.5))  # Đổi sleep thành time.sleep
            locator.first.click(timeout=current_timeout)
            return {
                "status": True,
                "message": "✔️ Clicked the Next button successfully.",
            }

        except PlaywrightTimeoutError:
            return {
                "status": False,
                "message": f"❌ Could not click the Next button within {current_timeout/1000}s.",
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"❌ Unexpected error when clicking the Next button: {e}",
            }

    clicked_result = try_click_btn(btn_locator, timeout)
    if clicked_result["status"]:
        return clicked_result

    close_dialog(page)
    return try_click_btn(btn_locator, timeout)


def handle_list_on_marketplace(
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
    total_progress: int,
) -> bool:
    def emit_progress(msg: str, current_progress: int):
        msg = f"[{task.user_info.username}] {msg}"
        signals.progress_signal.emit(task, msg, current_progress, total_progress)

    try:
        emit_progress("Start listing on marketplace", 1)
        page.goto(
            "https://www.facebook.com/marketplace/create/item",
            timeout=60_000,
        )
        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            failed_msg = (
                f"Cannot start {task.action_name}. Please switch language to English."
            )
            signals.failed_signal.emit(task, failed_msg)
            return False

        marketplace_forms = page.locator(selectors.S_MARKETPLACE_FORM)
        marketplace_form = None
        for marketplace_form in marketplace_forms.all():
            if marketplace_form.is_visible() and marketplace_form.is_enabled():
                break
        if not marketplace_form:
            failed_msg = f"[{task.user_info.username}] {selectors.S_MARKETPLACE_FORM} is not found or is not interactive."
            signals.failed_signal.emit(task, failed_msg)
            return False

        close_dialog(page)
        expand_btn_locators = marketplace_form.locator(selectors.S_EXPAND_BUTTON)
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.click(timeout=MIN)
        emit_progress("Clicked the more details button", 2)

        description_locators = marketplace_form.locator(selectors.S_TEXTAREA)
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.fill(
            value=task.action_payload.description, timeout=MIN
        )
        emit_progress("Filled data into the description field.", 3)

        input_text_locators = marketplace_form.locator(selectors.S_INPUT_TEXT)
        title_locator = input_text_locators.nth(0)
        price_locator = input_text_locators.nth(1)
        location_locator = input_text_locators.nth(3)

        sleep(random.uniform(0.2, 1.5))
        title_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        title_locator.fill(value=task.action_payload.title, timeout=MIN)
        emit_progress("Filled data into the title field.", 4)

        sleep(random.uniform(0.2, 1.5))
        price_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        price_locator.fill(value="0", timeout=MIN)
        sleep(random.uniform(0.2, 1.5))
        emit_progress("Filled data into the price field.", 5)

        location_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        location_locator.fill("Da Lat")
        location_locator.press(" ")
        location_listbox_locators = page.locator(selectors.S_UL_LISTBOX)
        sleep(random.uniform(0.2, 1.5))
        location_listbox_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        location_listbox_locators.first.wait_for(state="attached", timeout=MIN)
        location_option_locators = location_listbox_locators.first.locator(
            selectors.S_LI_OPTION
        )
        sleep(random.uniform(0.2, 1.5))
        location_option_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        location_option_locators.first.click(timeout=MIN)
        emit_progress("Filled data into the location field.", 6)

        combobox_locators = page.locator(selectors.S_LABEL_COMBOBOX_LISTBOX)
        category_locator = combobox_locators.nth(0)
        condition_locator = combobox_locators.nth(1)

        sleep(random.uniform(0.2, 1.5))
        category_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        category_locator.click(timeout=MIN)

        dialog_locators = page.locator(selectors.S_DIALOG_DROPDOWN)
        dialog_locators.first.wait_for(state="attached", timeout=MIN)
        dialog_button_locators = dialog_locators.first.locator(selectors.S_BUTTON)
        dialog_misc_button_locator = dialog_button_locators.nth(
            dialog_button_locators.count() - 2
        )
        sleep(random.uniform(0.2, 1.5))
        dialog_misc_button_locator.scroll_into_view_if_needed()
        dialog_misc_button_locator.click(timeout=MIN)
        dialog_locators.wait_for(state="detached")
        emit_progress("Filled data into the category field.", 7)

        sleep(random.uniform(0.2, 1.5))
        condition_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        condition_locator.click(timeout=MIN)
        listbox_locators = page.locator(selectors.S_DIV_LISTBOX)
        listbox_locators.first.wait_for(state="attached", timeout=MIN)
        listbox_option_locators = listbox_locators.first.locator(selectors.S_DIV_OPTION)

        sleep(random.uniform(0.2, 1.5))
        listbox_option_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        listbox_option_locators.first.click(timeout=MIN)
        dialog_locators.wait_for(state="detached")
        emit_progress("Filled data into the condition field.", 8)

        image_input_locators = marketplace_form.locator(selectors.S_IMG_INPUT)
        sleep(random.uniform(0.2, 1.5))
        image_input_locators.first.set_input_files(task.action_payload.image_paths)
        emit_progress("Filled data into the images field.", 9)

        clicked_next_result = click_button(page, selectors.S_NEXT_BUTTON, MIN)
        if clicked_next_result["status"]:
            emit_progress(clicked_next_result["message"], 10)
            return True
        else:
            signals.failed_signal.emit(task, clicked_next_result["message"])
            return False
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


def handle_list_on_more_place(
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
    total_progress: int,
):
    try:

        return True
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


ACTION_MAP = {
    "launch_browser": do_launch_browser,
    "marketplace": do_marketplace,
    # "marketplace_and_groups": do_marketplace_and_groups,
    # "discussion": do_discussion,
}
