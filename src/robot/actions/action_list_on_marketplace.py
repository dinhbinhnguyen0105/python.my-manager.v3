import random
from typing import List, Optional
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.my_types import RobotTaskType, BrowserWorkerSignals
from src.robot import selector_constants as selectors
import sys, traceback
from src.robot.actions.action_funcs import click_button, close_dialog, except_handle

MIN = 60_000

# page.wait_for_selector(SELECTORS["root"], timeout=MIN)


def list_on_marketplace(
    page: Page,
    task: RobotTaskType,
    settings: dict,
    signals: BrowserWorkerSignals,
) -> bool:
    log_prefix = f"[Task {task.user_info.username} - list_on_marketplace]"
    progress: List[int] = [0, 0]

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    progress[1] = 22
    emit_progress_update(f"Step 0: Estimated total steps: {progress[1]}")
    try:
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
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False

        emit_progress_update("Starting listing on marketplace.")
        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            failed_msg = (
                f"Cannot start {task.action_name}. Please switch language to English."
            )
            raise RuntimeError(failed_msg)

        emit_progress_update(
            f"Locating marketplace_form with selector: {selectors.S_MARKETPLACE_FORM}"
        )
        page.wait_for_selector(selectors.S_MARKETPLACE_FORM, timeout=MIN)
        marketplace_forms = page.locator(selectors.S_MARKETPLACE_FORM)
        if not marketplace_forms.count():
            _msg = f"marketplace_form locator not found (selector: {selectors.S_MARKETPLACE_FORM})."
            raise RuntimeError(_msg)
        marketplace_form: Optional[Locator] = None
        for marketplace_form_candidate in marketplace_forms.all():
            if (
                marketplace_form_candidate.is_visible()
                and marketplace_form_candidate.is_enabled()
            ):
                marketplace_form = marketplace_form_candidate
                break
        if not marketplace_form.count():
            _msg = f"marketplace_form is not found or is not interactive."
            raise RuntimeError(_msg)

        emit_progress_update("Try closing anonymous dialogs.")
        close_dialog(page)

        emit_progress_update(
            f"Locating expand_button with selector: {selectors.S_EXPAND_BUTTON}."
        )
        page.wait_for_selector(selectors.S_EXPAND_BUTTON, timeout=MIN)
        expand_btn_locators = marketplace_form.locator(selectors.S_EXPAND_BUTTON)
        if not expand_btn_locators.count():
            _msg = f"expand_button locator not found (selector: {selectors.S_EXPAND_BUTTON})"
            raise RuntimeError(_msg)
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.click(timeout=MIN)
        emit_progress_update("Clicked the more details button.")

        emit_progress_update(
            f"Locating description with selector: {selectors.S_TEXTAREA}."
        )
        page.wait_for_selector(selectors.S_TEXTAREA, timeout=MIN)
        description_locators = marketplace_form.locator(selectors.S_TEXTAREA)
        if not description_locators.count():
            _msg = f"description locator not found (selector: {selectors.S_TEXTAREA})"
            raise RuntimeError(_msg)
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.fill(
            value=task.action_payload.description, timeout=MIN
        )
        emit_progress_update("Filled data into the description field.")

        # --------------

        emit_progress_update(
            f"Locating title_locator, price_locator, location_locator with selector: {selectors.S_INPUT_TEXT}."
        )
        page.wait_for_selector(selectors.S_INPUT_TEXT, timeout=MIN)
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

        # ------- click next

        emit_progress_update("Clicking the 'Next' button.")
        clicked_next_result = click_button(page, selectors.S_NEXT_BUTTON, 30_000)
        emit_progress_update(clicked_next_result["message"])
        if clicked_next_result["status"]:
            return True
        else:
            emit_progress_update(clicked_next_result["message"])
            clicked_publish_result = click_button(
                page, selectors.S_PUBLISH_BUTTON, 30_000
            )
            if not clicked_publish_result["status"]:
                raise RuntimeError("Could not click Next button or Publish button")
            sleep(10)
            return True

    except RuntimeError as e:
        signals.failed_signal.emit(task, str(e), settings.get("raw_proxy"))
        return False
    except Exception as e:
        except_handle(e)
        signals.error_signal.emit(
            task,
            f"Details: See console log for full traceback.",
        )
        return False
