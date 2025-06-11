import random
from typing import List
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from src.my_types import RobotTaskType, BrowserWorkerSignals
from src.robot import selector_constants as selectors
import sys, traceback

MIN = 60_000


def discussion(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    log_prefix = f"[Task {task.user_info.username} - do_discussion]"

    progress: List[int] = [0, 0]

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    groups_num = settings.get("group_num", 5)
    groups_num = int(groups_num)
    progress[1] = 5 + int(groups_num) * 5
    signals.task_progress_signal.emit(
        f"Estimated total steps: {progress[1]}. Number of groups to process: {groups_num}.",
        [progress[0], progress[1]],
    )
    print(
        f"{log_prefix} Estimated total steps: {progress[1]}. Number of groups to process: {groups_num}."
    )

    current_group_processed = 0

    try:
        emit_progress_update("Navigating to Facebook general groups page.")
        try:
            page.goto("https://www.facebook.com/groups/feed/", timeout=MIN)
            signals.task_progress_signal.emit(
                "Successfully navigated to general groups page.",
                [progress[0], progress[1]],
            )
        except PlaywrightTimeoutError as e:
            signals.task_progress_signal.emit(
                f"ERROR: Timeout while navigating to general groups page.",
                [progress[0], progress[1]],
            )
            print(
                f"{log_prefix} ERROR: Timeout when navigating to general groups page: {e}",
                file=sys.stderr,
            )
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False

        emit_progress_update("Checking page language.")
        page_language = page.locator("html").get_attribute("lang")
        signals.task_progress_signal.emit(
            f"Detected page language: '{page_language}'.", [progress[0], progress[1]]
        )
        if page_language != "en":
            signals.task_progress_signal.emit(
                "WARNING: Page language is not English. Language conversion required.",
                [progress[0], progress[1]],
            )
            signals.failed_signal.emit(
                task,
                "Page language conversion to English required.",
                settings.get("raw_proxy", None),
            )
            return False

        emit_progress_update(
            "Waiting for group sidebar to load (if loading icon is present)."
        )
        sidebar_locator = page.locator(
            f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})"
        )
        loading_attempt = 0
        max_loading_attempts = 10
        while (
            sidebar_locator.first.locator(selectors.S_LOADING).count()
            and loading_attempt < max_loading_attempts
        ):
            loading_attempt += 1
            signals.task_progress_signal.emit(
                f"Loading indicator detected in sidebar. Waiting... (Attempt {loading_attempt}/{max_loading_attempts})",
                [progress[0], progress[1]],
            )
            _loading_element = sidebar_locator.first.locator(selectors.S_LOADING)
            try:
                sleep(random.uniform(1, 3))
                _loading_element.first.scroll_into_view_if_needed(timeout=100)
                signals.task_progress_signal.emit(
                    "Loading indicator scrolled into view.", [progress[0], progress[1]]
                )
            except PlaywrightTimeoutError as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Timeout while scrolling loading indicator.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Timeout when scrolling loading indicator: {e}. Might be loaded or stuck. Exiting wait loop.",
                    file=sys.stderr,
                )
                break
            except Exception as ex:
                signals.task_progress_signal.emit(
                    f"ERROR: An unexpected error occurred while scrolling loading indicator.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: An unexpected error occurred when scrolling loading indicator: {ex}. Exiting wait loop.",
                    file=sys.stderr,
                )
                break
        if loading_attempt >= max_loading_attempts:
            signals.task_progress_signal.emit(
                f"WARNING: Exceeded maximum loading wait attempts ({max_loading_attempts}). Continuing without full sidebar load confirmation.",
                [progress[0], progress[1]],
            )
        else:
            signals.task_progress_signal.emit(
                "Group sidebar loaded or no loading indicator found.",
                [progress[0], progress[1]],
            )

        emit_progress_update("Searching for group URLs in the sidebar.")
        group_locators = sidebar_locator.first.locator(
            "a[href^='https://www.facebook.com/groups/']"
        )
        group_urls = [
            group_locator.get_attribute("href")
            for group_locator in group_locators.all()
        ]
        signals.task_progress_signal.emit(
            f"Found {len(group_urls)} group URLs.", [progress[0], progress[1]]
        )
        if not group_urls:
            signals.task_progress_signal.emit(
                "WARNING: No group URLs could be retrieved. No groups to post in.",
                [progress[0], progress[1]],
            )
            signals.failed_signal.emit(
                task,
                "Could not retrieve any group URLs.",
                settings.get("raw_proxy"),
            )
            return False

        signals.task_progress_signal.emit(
            f"Starting loop through groups to post. (Total groups found: {len(group_urls)})",
            [progress[0], progress[1]],
        )
        for i, group_url in enumerate(group_urls):
            if current_group_processed >= groups_num:
                signals.task_progress_signal.emit(
                    f"Processed {groups_num} groups. Stopping group loop.",
                    [progress[0], progress[1]],
                )
                break

            emit_progress_update(
                f"Processing group {i+1}/{len(group_urls)} (Target: {groups_num} groups): {group_url}"
            )

            try:
                page.goto(group_url, timeout=MIN)
                signals.task_progress_signal.emit(
                    f"Successfully navigated to group: {group_url}",
                    [progress[0], progress[1]],
                )
            except PlaywrightTimeoutError as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Timeout while navigating to group {group_url}. Skipping this group.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Timeout when navigating to group {group_url}: {e}. Skipping this group.",
                    file=sys.stderr,
                )
                continue

            main_locator = page.locator(selectors.S_MAIN)
            tablist_locator = main_locator.first.locator(selectors.S_TABLIST)

            signals.task_progress_signal.emit(
                "Checking group tabs for 'Discussion' or 'Buy/Sell Discussion' tab.",
                [progress[0], progress[1]],
            )
            is_discussion_tab_found = True
            if tablist_locator.first.is_visible(timeout=5000):
                tab_locators = tablist_locator.first.locator(selectors.S_TABLIST_TAB)
                signals.task_progress_signal.emit(
                    f"Found {tab_locators.count()} tabs in the group.",
                    [progress[0], progress[1]],
                )
                for tab_index in range(tab_locators.count()):
                    tab_locator = tab_locators.nth(tab_index)
                    try:
                        tab_url = tab_locator.get_attribute("href", timeout=5_000)
                        if not tab_url:
                            signals.task_progress_signal.emit(
                                f"WARNING: Tab {tab_index} has no URL. Skipping.",
                                [progress[0], progress[1]],
                            )
                            continue

                        cleaned_tab_url = tab_url.rstrip("/")

                        signals.task_progress_signal.emit(
                            f"Checking Tab {tab_index}: URL = '{cleaned_tab_url}'",
                            [progress[0], progress[1]],
                        )
                        if cleaned_tab_url.endswith("buy_sell_discussion"):
                            signals.task_progress_signal.emit(
                                f"Found 'Buy/Sell Discussion' tab at URL: {cleaned_tab_url}.",
                                [progress[0], progress[1]],
                            )
                            is_discussion_tab_found = False
                            break
                        if cleaned_tab_url.endswith("discussion"):
                            signals.task_progress_signal.emit(
                                f"Found 'Discussion' tab at URL: {cleaned_tab_url}. Clicking this tab.",
                                [progress[0], progress[1]],
                            )
                            tab_locator.click()
                            is_discussion_tab_found = True
                    except PlaywrightTimeoutError as e:
                        signals.task_progress_signal.emit(
                            f"ERROR: Timeout while getting URL for tab {tab_index}. Skipping this tab.",
                            [progress[0], progress[1]],
                        )
                        print(
                            f"{log_prefix} ERROR: Timeout when getting URL for tab {tab_index}: {e}. Skipping this tab.",
                            file=sys.stderr,
                        )
                        continue
                    except Exception as e:
                        signals.task_progress_signal.emit(
                            f"ERROR: An error occurred while processing tab {tab_index}. Skipping this tab.",
                            [progress[0], progress[1]],
                        )
                        print(
                            f"{log_prefix} ERROR: An error occurred when processing tab {tab_index}: {e}. Skipping this tab.",
                            file=sys.stderr,
                        )
                        continue
            else:
                signals.task_progress_signal.emit(
                    "WARNING: Tablist not visible for this group.",
                    [progress[0], progress[1]],
                )
                continue

            if not is_discussion_tab_found:
                signals.task_progress_signal.emit(
                    "Found 'Buy/Sell Discussion' tab in this group or no suitable discussion tab found. Skipping group.",
                    [progress[0], progress[1]],
                )
                continue

            signals.task_progress_signal.emit(
                "Waiting and scrolling to the post creation area in the group.",
                [progress[0], progress[1]],
            )
            profile_locator = main_locator.first.locator(selectors.S_PROFILE)
            try:
                profile_locator.first.wait_for(state="attached", timeout=MIN)
                signals.task_progress_signal.emit(
                    "Profile/post creation area is attached.",
                    [progress[0], progress[1]],
                )
            except Exception as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Profile/post creation area not attached. Skipping this group.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Profile/post creation area not attached: {e}. Skipping this group.",
                    file=sys.stderr,
                )
                continue

            sleep(random.uniform(1, 3))
            profile_locator.first.scroll_into_view_if_needed()
            signals.task_progress_signal.emit(
                "Profile area scrolled into view.", [progress[0], progress[1]]
            )

            signals.task_progress_signal.emit(
                "Finding and clicking 'Discussion' or 'Write Something' button to open post creation dialog.",
                [progress[0], progress[1]],
            )
            discussion_btn_locator = profile_locator
            button_found = False
            max_parent_walks = 5
            walk_count = 0
            while walk_count < max_parent_walks:
                walk_count += 1
                temp_locator = discussion_btn_locator.first.locator("..").locator(
                    selectors.S_BUTTON
                )
                if temp_locator.count():
                    discussion_btn_locator = temp_locator.first
                    signals.task_progress_signal.emit(
                        f"Found 'Discussion' (or similar) button after {walk_count} DOM tree walks.",
                        [progress[0], progress[1]],
                    )
                    button_found = True
                    break
                else:
                    discussion_btn_locator = discussion_btn_locator.first.locator("..")
                    signals.task_progress_signal.emit(
                        f"Button not found, moving up parent. (Attempt {walk_count})",
                        [progress[0], progress[1]],
                    )

            if not button_found:
                signals.task_progress_signal.emit(
                    "WARNING: 'Discussion' or 'Write Something' button not found within limit. Skipping this group.",
                    [progress[0], progress[1]],
                )
                continue

            sleep(random.uniform(1, 3))
            try:
                discussion_btn_locator.scroll_into_view_if_needed()
                discussion_btn_locator.click()
                signals.task_progress_signal.emit(
                    "Clicked 'Discussion' button to open post creation dialog.",
                    [progress[0], progress[1]],
                )
            except Exception as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Could not click 'Discussion' button or scroll into view. Skipping this group.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Could not click 'Discussion' button or scroll into view: {e}. Skipping this group.",
                    file=sys.stderr,
                )
                continue

            signals.task_progress_signal.emit(
                f"Waiting for post creation dialog ('{selectors.S_DIALOG_CREATE_POST}') to appear and loading to complete.",
                [progress[0], progress[1]],
            )
            dialog_locator = page.locator(selectors.S_DIALOG_CREATE_POST)
            try:
                dialog_locator.first.locator(selectors.S_LOADING).first.wait_for(
                    state="detached", timeout=30_000
                )
                signals.task_progress_signal.emit(
                    "Loading in post creation dialog completed.",
                    [progress[0], progress[1]],
                )
            except PlaywrightTimeoutError as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Timeout while waiting for loading in post creation dialog. Skipping this group.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Timeout when waiting for loading in post creation dialog: {e}. Skipping this group.",
                    file=sys.stderr,
                )
                continue

            dialog_container_locator = dialog_locator.first.locator(
                "xpath=ancestor::*[contains(@role, 'dialog')][1]"
            )

            if task.action_payload.image_paths:
                signals.task_progress_signal.emit(
                    f"Detected {len(task.action_payload.image_paths)} image paths. Processing upload.",
                    [progress[0], progress[1]],
                )
                try:
                    dialog_container_locator.locator(selectors.S_IMG_INPUT).wait_for(
                        state="attached", timeout=10_000
                    )
                    signals.task_progress_signal.emit(
                        "Image input is directly ready.", [progress[0], progress[1]]
                    )
                except PlaywrightTimeoutError as e:
                    signals.task_progress_signal.emit(
                        "WARNING: Image input not directly ready. Attempting to click image button.",
                        [progress[0], progress[1]],
                    )
                    print(
                        f"{log_prefix} WARNING: Image input not directly ready: {e}. Trying to click image button.",
                        file=sys.stderr,
                    )
                    try:
                        image_btn_locator = dialog_container_locator.first.locator(
                            selectors.S_IMAGE_BUTTON
                        )
                        sleep(random.uniform(1, 3))
                        image_btn_locator.click()
                        signals.task_progress_signal.emit(
                            "Clicked image button to open input.",
                            [progress[0], progress[1]],
                        )
                    except Exception as ex:
                        signals.task_progress_signal.emit(
                            f"ERROR: Could not click image button. Skipping image upload.",
                            [progress[0], progress[1]],
                        )
                        print(
                            f"{log_prefix} ERROR: Could not click image button: {ex}. Skipping image upload.",
                            file=sys.stderr,
                        )
                        task.action_payload.image_paths = []
                finally:
                    if task.action_payload.image_paths:
                        try:
                            image_input_locator = dialog_container_locator.locator(
                                selectors.S_IMG_INPUT
                            )
                            sleep(random.uniform(1, 3))
                            image_input_locator.set_input_files(
                                task.action_payload.image_paths, timeout=10000
                            )
                            signals.task_progress_signal.emit(
                                "Successfully set image files.",
                                [progress[0], progress[1]],
                            )
                        except PlaywrightTimeoutError as e:
                            signals.task_progress_signal.emit(
                                f"ERROR: Timeout while setting image files. Image might not be uploaded.",
                                [progress[0], progress[1]],
                            )
                            print(
                                f"{log_prefix} ERROR: Timeout when setting image files: {e}. Image might not be uploaded.",
                                file=sys.stderr,
                            )
                        except Exception as e:
                            signals.task_progress_signal.emit(
                                f"ERROR: An error occurred while setting image files. Image might not be uploaded.",
                                [progress[0], progress[1]],
                            )
                            print(
                                f"{log_prefix} ERROR: An error occurred when setting image files: {e}. Image might not be uploaded.",
                                file=sys.stderr,
                            )
            else:
                signals.task_progress_signal.emit(
                    "No image paths provided. Skipping image upload.",
                    [progress[0], progress[1]],
                )

            signals.task_progress_signal.emit(
                "Filling title and description into the post creation text box.",
                [progress[0], progress[1]],
            )
            textbox_locator = dialog_container_locator.first.locator(
                selectors.S_TEXTBOX
            )
            sleep(random.uniform(1, 3))
            try:
                content_to_fill = task.action_payload.description
                textbox_locator.fill(content_to_fill)
                signals.task_progress_signal.emit(
                    f"Filled post content (Title: '{task.action_payload.title}', Description: '{task.action_payload.description}').",
                    [progress[0], progress[1]],
                )
            except Exception as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Could not fill content into the text box. Skipping this group.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Could not fill content into the text box: {e}. Skipping this group.",
                    file=sys.stderr,
                )
                continue

            signals.task_progress_signal.emit(
                "Waiting for 'Post' button to be enabled and clicking.",
                [progress[0], progress[1]],
            )
            post_btn_locators = dialog_container_locator.first.locator(
                selectors.S_POST_BUTTON
            )
            try:
                dialog_container_locator.locator(
                    f"{selectors.S_POST_BUTTON}[aria-disabled]"
                ).wait_for(state="detached", timeout=30_000)
                signals.task_progress_signal.emit(
                    "'Post' button is now enabled.", [progress[0], progress[1]]
                )
                post_btn_locators.first.click()
                signals.task_progress_signal.emit(
                    "Clicked 'Post' button.", [progress[0], progress[1]]
                )
            except PlaywrightTimeoutError as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Timeout while waiting for 'Post' button to be enabled or clicked. Post might not have been published.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Timeout when waiting for 'Post' button to be enabled or clicked: {e}. Post might not have been published.",
                    file=sys.stderr,
                )
                signals.failed_signal.emit(
                    task,
                    "Could not click Post button or button remained disabled.",
                    settings.get("raw_proxy"),
                )
                continue

            signals.task_progress_signal.emit(
                "Waiting for post creation dialog to close.", [progress[0], progress[1]]
            )
            try:
                dialog_container_locator.wait_for(state="detached", timeout=30_000)
                signals.task_progress_signal.emit(
                    "Post creation dialog closed successfully.",
                    [progress[0], progress[1]],
                )
            except PlaywrightTimeoutError as e:
                signals.task_progress_signal.emit(
                    f"ERROR: Timeout while waiting for post creation dialog to close. Post might not have been published successfully or dialog is stuck.",
                    [progress[0], progress[1]],
                )
                print(
                    f"{log_prefix} ERROR: Timeout when waiting for post creation dialog to close: {e}. Post might not have been published successfully or dialog is stuck.",
                    file=sys.stderr,
                )
                signals.failed_signal.emit(
                    task,
                    "Post creation dialog did not close after publishing. Post might have failed.",
                    settings.get("raw_proxy"),
                )
                break

            sleep(random.uniform(1, 3))

            signals.succeeded_signal.emit(
                task,
                f"Successfully posted in group: {group_url}.",
                settings.get("raw_proxy"),
            )
            current_group_processed += 1
            signals.task_progress_signal.emit(
                f"Successfully processed {current_group_processed}/{groups_num} groups.",
                [progress[0], progress[1]],
            )

            if current_group_processed >= groups_num:
                signals.task_progress_signal.emit(
                    f"Processed {groups_num} groups. Ending posting task.",
                    [progress[0], progress[1]],
                )
                break

        signals.task_progress_signal.emit(
            f"Completed group processing loop. Total groups posted: {current_group_processed}/{groups_num}.",
            [progress[0], progress[1]],
        )

        signals.task_progress_signal.emit(
            "Discussion task completed successfully.", [progress[0], progress[1]]
        )
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
