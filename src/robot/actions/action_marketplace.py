import random
from typing import Any, List
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.my_types import RobotTaskType, BrowserWorkerSignals
from src.robot import selector_constants as selectors
import sys, traceback
from src.robot.actions.action_funcs import click_button, close_dialog

MIN = 60_000


def marketplace(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    log_prefix = f"[Task {task.user_info.username} - marketplace]"
    progress: List[int] = [0, 0]

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    try:
        progress[1] = 28  # Total steps for marketplace
        emit_progress_update(f"Performing marketplace listing: {task.action_name}")
        try:
            page.goto(
                "https://www.facebook.com/marketplace/create/item",
                timeout=MIN,
            )
            signals.task_progress_signal.emit(
                "Successfully navigated to Marketplace item creation page.",
                [progress[0], progress[1]],
            )
        except PlaywrightTimeoutError as e:
            emit_progress_update(
                "ERROR: Timeout while navigating to Marketplace creation page."
            )
            print(
                f"{log_prefix} ERROR: Timeout when navigating to Marketplace creation page: {e}",
                file=sys.stderr,
            )
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False
        except Exception as e:
            emit_progress_update(
                f"ERROR: An unexpected error occurred during navigation to Marketplace creation page."
            )
            print(
                f"{log_prefix} ERROR: An unexpected error occurred during navigation to Marketplace creation page: {e}",
                file=sys.stderr,
            )
            signals.error_signal.emit(task, str(e))
            return False

        is_listed_on_marketplace = list_on_marketplace(
            page, task, signals, settings, progress, emit_progress_update
        )
        if is_listed_on_marketplace:
            is_listed_on_more_place = list_on_more_place(
                page, task, signals, settings, progress, emit_progress_update
            )
            sleep(60)  # Original code had a sleep here, keeping it for now
            return is_listed_on_more_place
        return is_listed_on_marketplace
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


def list_on_marketplace(
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
    settings: dict,
    progress: List[int],
    emit_progress_update: callable,
) -> bool:
    log_prefix = f"[Task {task.user_info.username} - list_on_marketplace]"

    try:
        emit_progress_update("Starting listing on marketplace.")
        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            failed_msg = (
                f"Cannot start {task.action_name}. Please switch language to English."
            )
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            print(f"{log_prefix} ERROR: {failed_msg}", file=sys.stderr)
            return False

        emit_progress_update("Searching for marketplace form.")
        marketplace_forms = page.locator(selectors.S_MARKETPLACE_FORM)
        marketplace_form = None
        for (
            marketplace_form_candidate
        ) in marketplace_forms.all():  # Renamed to avoid shadowing
            if (
                marketplace_form_candidate.is_visible()
                and marketplace_form_candidate.is_enabled()
            ):
                marketplace_form = marketplace_form_candidate
                break
        if not marketplace_form:
            failed_msg = (
                f"{selectors.S_MARKETPLACE_FORM} is not found or is not interactive."
            )
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            print(f"{log_prefix} ERROR: {failed_msg}", file=sys.stderr)
            return False

        emit_progress_update("Closing any open dialogs.")
        close_dialog(page)

        emit_progress_update("Clicking the more details button.")
        expand_btn_locators = marketplace_form.locator(selectors.S_EXPAND_BUTTON)
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.click(timeout=MIN)
        emit_progress_update("Clicked the more details button.")

        emit_progress_update("Filling data into the description field.")
        description_locators = marketplace_form.locator(selectors.S_TEXTAREA)
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.fill(
            value=task.action_payload.description, timeout=MIN
        )
        emit_progress_update("Filled data into the description field.")

        input_text_locators = marketplace_form.locator(selectors.S_INPUT_TEXT)
        title_locator = input_text_locators.nth(0)
        price_locator = input_text_locators.nth(1)
        location_locator = input_text_locators.nth(3)

        emit_progress_update("Filling data into the title field.")
        sleep(random.uniform(0.2, 1.5))
        title_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        title_locator.fill(value=task.action_payload.title, timeout=MIN)
        emit_progress_update("Filled data into the title field.")

        emit_progress_update("Filling data into the price field.")
        sleep(random.uniform(0.2, 1.5))
        price_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        price_locator.fill(value="0", timeout=MIN)
        sleep(random.uniform(0.2, 1.5))
        emit_progress_update("Filled data into the price field.")

        emit_progress_update("Filling data into the location field.")
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
        emit_progress_update("Filled data into the location field.")

        combobox_locators = page.locator(selectors.S_LABEL_COMBOBOX_LISTBOX)
        category_locator = combobox_locators.nth(0)
        condition_locator = combobox_locators.nth(1)

        emit_progress_update("Filling data into the category field.")
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
        emit_progress_update("Filled data into the category field.")

        emit_progress_update("Filling data into the condition field.")
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
        emit_progress_update("Filled data into the condition field.")

        emit_progress_update("Filling data into the images field.")
        image_input_locators = marketplace_form.locator(selectors.S_IMG_INPUT)
        sleep(random.uniform(0.2, 1.5))
        image_input_locators.first.set_input_files(task.action_payload.image_paths)
        emit_progress_update("Filled data into the images field.")

        emit_progress_update("Clicking the 'Next' button.")
        clicked_next_result = click_button(page, selectors.S_NEXT_BUTTON, MIN)
        if clicked_next_result["status"]:
            emit_progress_update(clicked_next_result["message"])
            return True
        else:
            signals.failed_signal.emit(
                task, clicked_next_result["message"], settings.get("raw_proxy")
            )
            print(
                f"{log_prefix} ERROR: {clicked_next_result['message']}", file=sys.stderr
            )
            return False
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


def list_on_more_place(
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
    settings: dict,
    progress: List[int],
    emit_progress_update: callable,
):
    log_prefix = f"[Task {task.user_info.username} - list_on_more_place]"
    try:
        emit_progress_update("Starting listing on more places.")

        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            failed_msg = (
                f"Cannot start {task.action_name}. Please switch language to English."
            )
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            print(f"{log_prefix} ERROR: {failed_msg}", file=sys.stderr)
            return False

        emit_progress_update("Searching for marketplace form for additional listing.")
        marketplace_forms = page.locator(selectors.S_MARKETPLACE_FORM)
        marketplace_form = None
        for marketplace_form_candidate in marketplace_forms.all():
            if (
                marketplace_form_candidate.is_visible()
                and marketplace_form_candidate.is_enabled()
            ):
                marketplace_form = marketplace_form_candidate
                break
        if not marketplace_form:
            failed_msg = f"{selectors.S_MARKETPLACE_FORM} is not found or is not interactive for additional listing."
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            print(f"{log_prefix} ERROR: {failed_msg}", file=sys.stderr)
            return False

        emit_progress_update("Clicking checkboxes for additional listing locations.")
        checkbox_locators = marketplace_form.locator(selectors.S_CHECK_BOX)
        for checkbox_locator in checkbox_locators.all():
            if checkbox_locator.is_visible() and checkbox_locator.is_enabled():
                sleep(random.uniform(0.2, 0.8))
                checkbox_locator.scroll_into_view_if_needed()
                sleep(random.uniform(0.2, 0.8))
                checkbox_locator.click()
        emit_progress_update(
            "Finished clicking checkboxes for additional listing locations."
        )

        emit_progress_update("Clicking the 'Publish' button.")
        clicked_publish_result = click_button(page, selectors.S_PUBLISH_BUTTON, MIN)
        if clicked_publish_result["status"]:
            emit_progress_update(clicked_publish_result["message"])
            signals.succeeded_signal.emit(
                task, clicked_publish_result["message"], settings.get("raw_proxy")
            )
            return True
        else:
            signals.failed_signal.emit(
                task, clicked_publish_result["message"], settings.get("raw_proxy")
            )
            print(
                f"{log_prefix} ERROR: {clicked_publish_result['message']}",
                file=sys.stderr,
            )
            return False
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
