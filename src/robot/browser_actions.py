# src/robot/browser_actions.py
import random
from typing import Any, List
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.my_types import RobotTaskType, BrowserWorkerSignals
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
                "message": "✔️ Clicked button successfully.",
            }

        except PlaywrightTimeoutError:
            return {
                "status": False,
                "message": f"❌ Could not click button within {current_timeout/1000}s.",
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"❌ Unexpected error when clicking button: {e}",
            }

    clicked_result = try_click_btn(btn_locator, timeout)
    if clicked_result["status"]:
        return clicked_result

    close_dialog(page)
    return try_click_btn(btn_locator, timeout)


def do_launch_browser(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    try:
        signals.progress_signal.emit(task, "Launching ...", 0, 1)
        try:
            page.goto(task.action_payload.get("url", ""), timeout=MIN)
        except TimeoutError:
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False
        except Exception as e:
            if "ERR_ABORTED" in str(e):
                pass

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
        total_progress = 12
        msg = f"[{task.user_info.username}] Performing {task.action_name}"
        signals.progress_signal.emit(task, msg, 0, total_progress)
        try:
            page.goto(
                "https://www.facebook.com/marketplace/create/item",
                timeout=MIN,
            )
        except TimeoutError:
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False
        is_listed_on_marketplace = handle_list_on_marketplace(
            page, task, signals, settings, total_progress
        )
        if is_listed_on_marketplace:
            is_listed_on_more_place = handle_list_on_more_place(
                page, task, signals, settings, total_progress
            )
            sleep(60)
            return is_listed_on_more_place
        return is_listed_on_marketplace
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


def handle_list_on_marketplace(
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
    settings: dict,
    total_progress: int,
) -> bool:
    def emit_progress(msg: str, current_progress: int):
        msg = f"[{task.user_info.username}] {msg}"
        signals.progress_signal.emit(task, msg, current_progress, total_progress)

    try:
        emit_progress(" ✔️Start listing on marketplace", 1)
        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            failed_msg = (
                f"Cannot start {task.action_name}. Please switch language to English."
            )
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            return False

        marketplace_forms = page.locator(selectors.S_MARKETPLACE_FORM)
        marketplace_form = None
        for marketplace_form in marketplace_forms.all():
            if marketplace_form.is_visible() and marketplace_form.is_enabled():
                break
        if not marketplace_form:
            failed_msg = f"[{task.user_info.username}] {selectors.S_MARKETPLACE_FORM} is not found or is not interactive."
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            return False

        close_dialog(page)
        expand_btn_locators = marketplace_form.locator(selectors.S_EXPAND_BUTTON)
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        expand_btn_locators.first.click(timeout=MIN)
        emit_progress(" ✔️Clicked the more details button", 2)

        description_locators = marketplace_form.locator(selectors.S_TEXTAREA)
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        description_locators.first.fill(
            value=task.action_payload.description, timeout=MIN
        )
        emit_progress(" ✔️Filled data into the description field.", 3)

        input_text_locators = marketplace_form.locator(selectors.S_INPUT_TEXT)
        title_locator = input_text_locators.nth(0)
        price_locator = input_text_locators.nth(1)
        location_locator = input_text_locators.nth(3)

        sleep(random.uniform(0.2, 1.5))
        title_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        title_locator.fill(value=task.action_payload.title, timeout=MIN)
        emit_progress(" ✔️Filled data into the title field.", 4)

        sleep(random.uniform(0.2, 1.5))
        price_locator.scroll_into_view_if_needed()
        sleep(random.uniform(0.2, 1.5))
        price_locator.fill(value="0", timeout=MIN)
        sleep(random.uniform(0.2, 1.5))
        emit_progress(" ✔️Filled data into the price field.", 5)

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
        emit_progress(" ✔️Filled data into the location field.", 6)

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
        emit_progress(" ✔️Filled data into the category field.", 7)

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
        emit_progress(" ✔️Filled data into the condition field.", 8)

        image_input_locators = marketplace_form.locator(selectors.S_IMG_INPUT)
        sleep(random.uniform(0.2, 1.5))
        image_input_locators.first.set_input_files(task.action_payload.image_paths)
        emit_progress(" ✔️Filled data into the images field.", 9)

        clicked_next_result = click_button(page, selectors.S_NEXT_BUTTON, MIN)
        if clicked_next_result["status"]:
            emit_progress(clicked_next_result["message"], 10)
            return True
        else:
            signals.failed_signal.emit(
                task, clicked_next_result["message"], settings.get("raw_proxy")
            )
            return False
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


def handle_list_on_more_place(
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
    settings: dict,
    total_progress: int,
):
    try:
        msg = f"[{task.user_info.username}] Start list on more place"
        signals.progress_signal.emit(task, msg, 11, total_progress)

        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            failed_msg = (
                f"Cannot start {task.action_name}. Please switch language to English."
            )
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            return False

        marketplace_forms = page.locator(selectors.S_MARKETPLACE_FORM)
        marketplace_form = None
        for marketplace_form in marketplace_forms.all():
            if marketplace_form.is_visible() and marketplace_form.is_enabled():
                break
        if not marketplace_form:
            failed_msg = f"[{task.user_info.username}] {selectors.S_MARKETPLACE_FORM} is not found or is not interactive."
            signals.failed_signal.emit(task, failed_msg, settings.get("raw_proxy"))
            return False

        checkbox_locators = marketplace_form.locator(selectors.S_CHECK_BOX)
        for checkbox_locator in checkbox_locators.all():
            if checkbox_locator.is_visible() and checkbox_locator.is_enabled():
                sleep(random.uniform(0.2, 0.8))
                checkbox_locator.scroll_into_view_if_needed()
                sleep(random.uniform(0.2, 0.8))
                checkbox_locator.click()

        clicked_publish_result = click_button(page, selectors.S_PUBLISH_BUTTON, MIN)
        if clicked_publish_result["status"]:
            signals.progress_signal.emit(
                task,
                f"[{task.user_info.username}] {clicked_publish_result["message"]}",
                12,
                total_progress,
            )
            return True
        else:
            signals.failed_signal.emit(
                task, clicked_publish_result["message"], settings.get("raw_proxy")
            )
            return False
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


def handle_discussion(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    progress: List[int, int] = [0, 0]

    def emit_progress():
        signals.task_progress_signal.emit(progress[0], progress[1])
        progress[0] += 1

    groups_num = settings.get("group_num", 5)
    progress[1] += groups_num
    current_group = 0

    try:
        try:
            emit_progress()
            page.goto("https://www.facebook.com/groups/feed/", timeout=MIN)
        except TimeoutError:
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False
        page_language = page.locator("html").get_attribute("lang")
        if page_language != "en":
            signals.failed_signal.emit(
                task, "Switch to English.", settings.get("raw_proxy", None)
            )
            return False
        sidebar_locator = page.locator(
            f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})"
        )
        emit_progress()
        while sidebar_locator.first.locator(selectors.S_LOADING).count():
            _ = sidebar_locator.first.locator(selectors.S_LOADING)
            if _.count():
                try:
                    sleep(random.uniform(1, 3))
                    _.first.scroll_into_view_if_needed(timeout=100)
                except:
                    break
        group_locators = sidebar_locator.first.locator(
            "a[href^='https://www.facebook.com/groups/']"
        )
        group_urls = [
            group_locator.get_attribute("href")
            for group_locator in group_locators.all()
        ]
        if not len(group_urls):
            signals.log_message.emit("Could not retrieve any group URLs")
            return
        emit_progress()
        for group_url in group_urls:
            page.goto(group_url, timeout=MIN)
            main_locator = page.locator(selectors.S_MAIN)
            tablist_locator = main_locator.first.locator(selectors.S_TABLIST)
            if tablist_locator.first.is_visible(timeout=5000):
                continue
            tab_locators = tablist_locator.first.locator(selectors.S_TABLIST_TAB)
            is_discussion = False
            for tab_locator in tab_locators.all():
                is_discussion = True
                try:
                    tab_url = tab_locator.get_attribute("href", timeout=5_000)
                except TimeoutError:
                    continue
                if not tab_url:
                    continue
                tab_url = tab_url[:-1] if tab_url.endswith("/") else tab_url
                if tab_url.endswith("buy_sell_discussion"):
                    is_discussion = False
                    break

            if not is_discussion:
                continue
            profile_locator = main_locator.first.locator(selectors.S_PROFILE)
            try:
                profile_locator.first.wait_for(state="attached", timeout=MIN)
            except Exception as e:
                continue
            sleep(random.uniform(1, 3))
            profile_locator.first.scroll_into_view_if_needed()
            discussion_btn_locator = profile_locator
            while True:
                if (
                    discussion_btn_locator.first.locator("..")
                    .locator(selectors.S_BUTTON)
                    .count()
                ):
                    discussion_btn_locator = discussion_btn_locator.first.locator(
                        ".."
                    ).locator(selectors.S_BUTTON)
                    break
                else:
                    discussion_btn_locator = discussion_btn_locator.first.locator("..")
            sleep(random.uniform(1, 3))
            discussion_btn_locator.first.scroll_into_view_if_needed()
            try:
                discussion_btn_locator.first.click()
            except Exception as e:
                continue
            page.locator(selectors.S_DIALOG_CREATE_POST).first.locator(
                selectors.S_LOADING
            ).first.wait_for(state="detached", timeout=30_000)
            dialog_locator = page.locator(selectors.S_DIALOG_CREATE_POST)
            dialog_container_locator = dialog_locator.first.locator(
                "xpath=ancestor::*[contains(@role, 'dialog')][1]"
            )
            if len(task.action_payload.image_paths):
                try:
                    dialog_container_locator.locator(selectors.S_IMG_INPUT).wait_for(
                        state="attached", timeout=10_000
                    )
                except PlaywrightTimeoutError:
                    image_btn_locator = dialog_container_locator.first.locator(
                        selectors.S_IMAGE_BUTTON
                    )
                    sleep(random.uniform(1, 3))
                    image_btn_locator.click()
                finally:
                    image_input_locator = dialog_container_locator.locator(
                        selectors.S_IMG_INPUT
                    )
                    sleep(random.uniform(1, 3))
                    image_input_locator.set_input_files(
                        task.action_payload.image_paths, timeout=10000
                    )
            textbox_locator = dialog_container_locator.first.locator(
                selectors.S_TEXTBOX
            )
            sleep(random.uniform(1, 3))
            textbox_locator.fill(
                f"{task.action_payload.title}\n\n{task.action_payload.description}"
            )
            post_btn_locators = dialog_container_locator.first.locator(
                selectors.S_POST_BUTTON
            )

            dialog_container_locator.locator(
                f"{selectors.S_POST_BUTTON}[aria-disabled]"
            ).wait_for(state="detached", timeout=30_000)
            post_btn_locators.first.click()
            try:
                dialog_container_locator.wait_for(state="detached", timeout=MIN)
            except TimeoutError:
                signals.failed_signal.emit(
                    task, "Publish failed", settings.get("raw_proxy")
                )
                return False
            sleep(random.uniform(1, 3))
            signals.log_message.emit(f"Published in {group_url}.")
            current_group += 1
            emit_progress()
            if current_group > groups_num:
                break
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
