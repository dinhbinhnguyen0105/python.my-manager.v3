# src/robot/browser_actions.py
import random
from typing import Any, List
from time import sleep
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from src.my_types import RobotTaskType, BrowserWorkerSignals
from src.robot import selector_constants as selectors
import sys, traceback

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


def _do_discussion(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    progress: List[int, int] = [0, 0]

    def emit_progress():
        signals.task_progress_signal.emit([progress[0], progress[1]])
        progress[0] += 1

    groups_num = settings.get("group_num", 5)
    progress[1] += int(groups_num)
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
            signals.failed_signal.emit(
                task, "Could not retrieve any group URLs", settings.get("raw_proxy")
            )
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
            signals.succeeded_signal.emit(
                task, f"Published in {group_url}.", settings.get("raw_proxy")
            )
            current_group += 1
            emit_progress()
            if current_group > groups_num:
                break
        return True
    except Exception as e:
        signals.error_signal.emit(task, str(e))
        return False


def do_discussion(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    # Log prefix for clarity in debug messages
    log_prefix = f"[Task {task.user_info.uid} - do_discussion]"
    print(f"{log_prefix} Bắt đầu thực hiện tác vụ thảo luận.")

    # progress[0] là current_step, progress[1] là total_steps
    progress: List[int] = [0, 0]

    def emit_progress_update():
        """Hàm trợ giúp để phát tín hiệu tiến độ và tăng bước hiện tại."""
        progress[
            0
        ] += 1  # Tăng bước hiện tại TRƯỚC khi phát tín hiệu để hiển thị chính xác số bước đã hoàn thành
        signals.task_progress_signal.emit([progress[0], progress[1]])
        print(f"{log_prefix} Tiến độ: {progress[0]}/{progress[1]}")

    # Tính toán tổng số bước dự kiến. Đây là ước tính để QProgressBar hoạt động tốt.
    groups_num = settings.get("group_num", 5)  # Mặc định 5 nhóm nếu không được chỉ định
    groups_num = int(groups_num)
    # Ước tính tổng số bước: 5 bước chung + (số nhóm cần xử lý * 5 bước/nhóm)
    progress[1] = 5 + int(groups_num) * 5
    print(
        f"{log_prefix} Tổng số bước dự kiến: {progress[1]}. Số nhóm cần xử lý: {groups_num}."
    )

    current_group_processed = (
        0  # Đếm số nhóm đã xử lý thành công (để so sánh với groups_num)
    )

    try:
        # Bước 1: Điều hướng đến trang nhóm Facebook
        print(f"{log_prefix} Bước 1: Điều hướng đến trang nhóm chung Facebook.")
        emit_progress_update()
        try:
            page.goto("https://www.facebook.com/groups/feed/", timeout=MIN)
            print(f"{log_prefix} Đã điều hướng thành công đến trang nhóm chung.")
        except PlaywrightTimeoutError as e:
            print(
                f"{log_prefix} LỖI: Hết thời gian chờ khi điều hướng đến trang nhóm chung: {e}",
                file=sys.stderr,
            )
            if settings.get("raw_proxy"):
                signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
            return False

        # Bước 2: Kiểm tra ngôn ngữ trang
        print(f"{log_prefix} Bước 2: Kiểm tra ngôn ngữ trang.")
        page_language = page.locator("html").get_attribute("lang")
        print(f"{log_prefix} Ngôn ngữ trang được phát hiện: '{page_language}'.")
        if page_language != "en":
            print(
                f"{log_prefix} CẢNH BÁO: Ngôn ngữ trang không phải tiếng Anh. Yêu cầu chuyển đổi ngôn ngữ."
            )
            signals.failed_signal.emit(
                task,
                "Yêu cầu chuyển đổi ngôn ngữ trang sang tiếng Anh.",
                settings.get("raw_proxy", None),
            )
            return False

        # Bước 3: Chờ sidebar tải xong (nếu có loading indicator)
        print(
            f"{log_prefix} Bước 3: Chờ sidebar nhóm tải xong (nếu có biểu tượng loading)."
        )
        sidebar_locator = page.locator(
            f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})"
        )
        emit_progress_update()
        loading_attempt = 0
        max_loading_attempts = 10  # Giới hạn số lần thử chờ loading
        while (
            sidebar_locator.first.locator(selectors.S_LOADING).count()
            and loading_attempt < max_loading_attempts
        ):
            loading_attempt += 1
            print(
                f"{log_prefix}   Phát hiện loading indicator trong sidebar. Đang chờ... (Lần {loading_attempt}/{max_loading_attempts})"
            )
            _loading_element = sidebar_locator.first.locator(selectors.S_LOADING)
            try:
                sleep(random.uniform(1, 3))
                _loading_element.first.scroll_into_view_if_needed(
                    timeout=100
                )  # Cuộn để đảm bảo tải
                print(f"{log_prefix}   Đã cuộn loading indicator vào chế độ xem.")
            except (
                PlaywrightTimeoutError
            ) as e:  # Catch specific Playwright timeout for scroll
                print(
                    f"{log_prefix}   LỖI: Hết thời gian chờ khi cuộn loading indicator: {e}. Có thể đã tải xong hoặc bị kẹt. Thoát vòng lặp chờ."
                )
                break
            except Exception as ex:  # Catch other potential exceptions during scroll
                print(
                    f"{log_prefix}   LỖI: Xảy ra lỗi không mong muốn khi cuộn loading indicator: {ex}. Thoát vòng lặp chờ."
                )
                break
        if loading_attempt >= max_loading_attempts:
            print(
                f"{log_prefix} CẢNH BÁO: Vượt quá số lần chờ loading tối đa ({max_loading_attempts}). Tiếp tục mà không chắc chắn sidebar đã tải đầy đủ."
            )
        else:
            print(
                f"{log_prefix} Sidebar nhóm đã tải xong hoặc không có loading indicator."
            )

        # Bước 4: Lấy danh sách URL các nhóm
        print(f"{log_prefix} Bước 4: Đang tìm kiếm các URL nhóm trong sidebar.")
        group_locators = sidebar_locator.first.locator(
            "a[href^='https://www.facebook.com/groups/']"
        )
        group_urls = [
            group_locator.get_attribute("href")
            for group_locator in group_locators.all()
        ]
        print(f"{log_prefix} Đã tìm thấy {len(group_urls)} URL nhóm.")
        if not group_urls:  # Sử dụng if not list để kiểm tra danh sách rỗng
            print(
                f"{log_prefix} CẢNH BÁO: Không thể lấy bất kỳ URL nhóm nào. Không có nhóm để đăng bài."
            )
            signals.failed_signal.emit(
                task,
                "Không thể truy xuất bất kỳ URL nhóm nào.",
                settings.get("raw_proxy"),
            )
            return False

        emit_progress_update()  # Tiến độ sau khi lấy nhóm

        # Bước 5: Lặp qua từng nhóm và đăng bài
        print(
            f"{log_prefix} Bước 5: Bắt đầu lặp qua các nhóm để đăng bài. (Tổng số nhóm tìm thấy: {len(group_urls)})"
        )
        for i, group_url in enumerate(group_urls):
            if current_group_processed >= groups_num:
                print(
                    f"{log_prefix} Đã xử lý đủ {groups_num} nhóm. Dừng vòng lặp nhóm."
                )
                break

            print(
                f"{log_prefix}   Xử lý nhóm {i+1}/{len(group_urls)} (Target: {groups_num} nhóm): {group_url}"
            )
            emit_progress_update()  # Tiến độ cho mỗi nhóm mới

            # 5.1: Điều hướng đến trang nhóm cụ thể
            try:
                page.goto(group_url, timeout=MIN)
                print(
                    f"{log_prefix}     Đã điều hướng thành công đến nhóm: {group_url}"
                )
            except PlaywrightTimeoutError as e:
                print(
                    f"{log_prefix}     LỖI: Hết thời gian chờ khi điều hướng đến nhóm {group_url}: {e}. Bỏ qua nhóm này."
                )
                continue  # Bỏ qua nhóm này và tiếp tục với nhóm tiếp theo

            main_locator = page.locator(selectors.S_MAIN)
            tablist_locator = main_locator.first.locator(selectors.S_TABLIST)

            # 5.2: Kiểm tra tab 'Discussion' (hoặc 'Buy/Sell Discussion')
            print(
                f"{log_prefix}     Kiểm tra các tab trong nhóm để tìm tab 'Discussion' hoặc 'Buy/Sell Discussion'."
            )
            is_discussion_tab_found = True
            if tablist_locator.first.is_visible(timeout=5000):
                tab_locators = tablist_locator.first.locator(selectors.S_TABLIST_TAB)
                print(
                    f"{log_prefix}     Đã tìm thấy {tab_locators.count()} tab trong nhóm."
                )
                for tab_index in range(tab_locators.count()):
                    tab_locator = tab_locators.nth(tab_index)  # Lấy tab theo chỉ mục
                    try:
                        tab_url = tab_locator.get_attribute("href", timeout=5_000)
                        if not tab_url:
                            print(
                                f"{log_prefix}       CẢNH BÁO: Tab {tab_index} không có URL. Bỏ qua."
                            )
                            continue

                        # Chuẩn hóa URL để so sánh
                        cleaned_tab_url = tab_url.rstrip("/")

                        print(
                            f"{log_prefix}       Kiểm tra Tab {tab_index}: URL = '{cleaned_tab_url}'"
                        )
                        if cleaned_tab_url.endswith("buy_sell_discussion"):
                            print(
                                f"{log_prefix}       Đã tìm thấy tab 'Buy/Sell Discussion' tại URL: {cleaned_tab_url}."
                            )
                            is_discussion_tab_found = False
                            break
                        if cleaned_tab_url.endswith("discussion"):
                            print(
                                f"{log_prefix}       Đã tìm thấy tab 'Discussion' tại URL: {cleaned_tab_url}. Click vào tab này."
                            )
                            tab_locator.click()
                            is_discussion_tab_found = True
                            sleep(random.uniform(1, 2))  # Đợi tab tải
                        # break
                        else:
                            print(
                                f"{log_prefix}       Tab {tab_index} không phải tab thảo luận."
                            )
                    except PlaywrightTimeoutError as e:
                        print(
                            f"{log_prefix}       LỖI: Hết thời gian chờ khi lấy URL tab {tab_index}: {e}. Bỏ qua tab này."
                        )
                        continue
                    except Exception as e:
                        print(
                            f"{log_prefix}       LỖI: Xảy ra lỗi khi xử lý tab {tab_index}: {e}. Bỏ qua tab này."
                        )
                        continue
            else:
                print(
                    f"{log_prefix}     CẢNH BÁO: Tablist không hiển thị cho nhóm này."
                )
                continue

            if not is_discussion_tab_found:
                print(
                    f"{log_prefix}     Đã tìm thấy tab 'Buy/Sell Discussion' trong nhóm này. Bỏ qua nhóm."
                )
                continue  # Bỏ qua nhóm này nếu không tìm thấy tab discussion

            # Bước 5.3: Chờ và cuộn đến khu vực tạo bài viết
            print(f"{log_prefix}     Chờ và cuộn đến khu vực tạo bài viết trong nhóm.")
            profile_locator = main_locator.first.locator(selectors.S_PROFILE)
            try:
                profile_locator.first.wait_for(state="attached", timeout=MIN)
                print(
                    f"{log_prefix}     Khu vực profile/tạo bài viết đã được đính kèm."
                )
            except Exception as e:
                print(
                    f"{log_prefix}     LỖI: Khu vực profile/tạo bài viết không được đính kèm: {e}. Bỏ qua nhóm này."
                )
                continue

            sleep(random.uniform(1, 3))
            profile_locator.first.scroll_into_view_if_needed()
            print(f"{log_prefix}     Đã cuộn khu vực profile vào chế độ xem.")

            # Bước 5.4: Tìm và click nút "Discussion" (hoặc "Write Something")
            print(
                f"{log_prefix}     Tìm và click nút 'Discussion' hoặc 'Write Something' để mở dialog tạo bài."
            )
            discussion_btn_locator = profile_locator
            button_found = False
            max_parent_walks = 5  # Giới hạn số lần đi lên cây DOM
            walk_count = 0
            while walk_count < max_parent_walks:
                walk_count += 1
                temp_locator = discussion_btn_locator.first.locator("..").locator(
                    selectors.S_BUTTON
                )
                if temp_locator.count():
                    discussion_btn_locator = (
                        temp_locator.first
                    )  # Lấy phần tử đầu tiên nếu có nhiều nút
                    print(
                        f"{log_prefix}       Đã tìm thấy nút 'Discussion' (hoặc tương tự) sau {walk_count} lần đi lên cây DOM."
                    )
                    button_found = True
                    break
                else:
                    discussion_btn_locator = discussion_btn_locator.first.locator(
                        ".."
                    )  # Đi lên một cấp cha nữa
                    print(
                        f"{log_prefix}       Không tìm thấy nút, tiếp tục đi lên cha. (Lần {walk_count})"
                    )

            if not button_found:
                print(
                    f"{log_prefix}     CẢNH BÁO: Không tìm thấy nút 'Discussion' hoặc 'Write Something' trong phạm vi giới hạn. Bỏ qua nhóm này."
                )
                continue

            sleep(random.uniform(1, 3))
            try:
                discussion_btn_locator.scroll_into_view_if_needed()
                discussion_btn_locator.click()
                print(
                    f"{log_prefix}     Đã click nút 'Discussion' để mở dialog tạo bài viết."
                )
            except Exception as e:
                print(
                    f"{log_prefix}     LỖI: Không thể click nút 'Discussion' hoặc cuộn vào chế độ xem: {e}. Bỏ qua nhóm này."
                )
                continue

            # Bước 5.5: Chờ dialog tạo bài viết xuất hiện và loading hoàn tất
            print(
                f"{log_prefix}     Chờ dialog tạo bài viết ('{selectors.S_DIALOG_CREATE_POST}') xuất hiện và loading hoàn tất."
            )
            dialog_locator = page.locator(selectors.S_DIALOG_CREATE_POST)
            try:
                # Chờ loading trong dialog biến mất
                dialog_locator.first.locator(selectors.S_LOADING).first.wait_for(
                    state="detached", timeout=30_000
                )
                print(f"{log_prefix}     Loading trong dialog tạo bài đã hoàn tất.")
            except PlaywrightTimeoutError as e:
                print(
                    f"{log_prefix}     LỖI: Hết thời gian chờ khi chờ loading trong dialog tạo bài: {e}. Bỏ qua nhóm này."
                )
                continue

            dialog_container_locator = dialog_locator.first.locator(
                "xpath=ancestor::*[contains(@role, 'dialog')][1]"
            )

            # Bước 5.6: Xử lý hình ảnh (nếu có)
            if task.action_payload.image_paths:
                print(
                    f"{log_prefix}     Phát hiện {len(task.action_payload.image_paths)} đường dẫn hình ảnh. Đang xử lý tải lên."
                )
                try:
                    # Thử chờ input hình ảnh trực tiếp nếu nó đã sẵn sàng
                    dialog_container_locator.locator(selectors.S_IMG_INPUT).wait_for(
                        state="attached", timeout=10_000
                    )
                    print(f"{log_prefix}     Input hình ảnh đã sẵn sàng trực tiếp.")
                except PlaywrightTimeoutError as e:
                    print(
                        f"{log_prefix}     CẢNH BÁO: Input hình ảnh không sẵn sàng trực tiếp: {e}. Thử click nút hình ảnh."
                    )
                    # Nếu không chờ được input trực tiếp, click nút hình ảnh để mở nó
                    try:
                        image_btn_locator = dialog_container_locator.first.locator(
                            selectors.S_IMAGE_BUTTON
                        )
                        sleep(random.uniform(1, 3))
                        image_btn_locator.click()
                        print(f"{log_prefix}     Đã click nút hình ảnh để mở input.")
                    except Exception as ex:
                        print(
                            f"{log_prefix}     LỖI: Không thể click nút hình ảnh: {ex}. Bỏ qua tải ảnh."
                        )
                        # Nếu không thể click nút, không thể tải ảnh, tiếp tục mà không có ảnh.
                        task.action_payload.image_paths = (
                            []
                        )  # Xóa đường dẫn ảnh để không cố gắng set files
                finally:
                    # Cố gắng đặt tệp sau khi input đã sẵn sàng (hoặc được mở)
                    if (
                        task.action_payload.image_paths
                    ):  # Kiểm tra lại nếu vẫn còn ảnh để tải
                        try:
                            image_input_locator = dialog_container_locator.locator(
                                selectors.S_IMG_INPUT
                            )
                            sleep(random.uniform(1, 3))
                            image_input_locator.set_input_files(
                                task.action_payload.image_paths, timeout=10000
                            )
                            print(
                                f"{log_prefix}     Đã đặt thành công các tệp hình ảnh."
                            )
                        except PlaywrightTimeoutError as e:
                            print(
                                f"{log_prefix}     LỖI: Hết thời gian chờ khi đặt tệp hình ảnh: {e}. Có thể không tải được ảnh."
                            )
                        except Exception as e:
                            print(
                                f"{log_prefix}     LỖI: Xảy ra lỗi khi đặt tệp hình ảnh: {e}. Có thể không tải được ảnh."
                            )
            else:
                print(
                    f"{log_prefix}     Không có đường dẫn hình ảnh nào được cung cấp. Bỏ qua tải ảnh."
                )

            # Bước 5.7: Điền tiêu đề và mô tả vào hộp văn bản
            print(
                f"{log_prefix}     Điền tiêu đề và mô tả vào hộp văn bản tạo bài viết."
            )
            textbox_locator = dialog_container_locator.first.locator(
                selectors.S_TEXTBOX
            )
            sleep(random.uniform(1, 3))
            try:
                content_to_fill = (
                    f"{task.action_payload.title}\n\n{task.action_payload.description}"
                )
                textbox_locator.fill(content_to_fill)
                print(
                    f"{log_prefix}     Đã điền nội dung bài viết (Tiêu đề: '{task.action_payload.title}', Mô tả: '{task.action_payload.description}')."
                )
            except Exception as e:
                print(
                    f"{log_prefix}     LỖI: Không thể điền nội dung vào hộp văn bản: {e}. Bỏ qua nhóm này."
                )
                continue  # Nếu không điền được nội dung thì bỏ qua

            # Bước 5.8: Chờ nút đăng bài được kích hoạt và click
            print(f"{log_prefix}     Chờ nút 'Đăng' được kích hoạt và click.")
            post_btn_locators = dialog_container_locator.first.locator(
                selectors.S_POST_BUTTON
            )
            try:
                # Chờ nút Đăng không còn bị vô hiệu hóa (aria-disabled)
                dialog_container_locator.locator(
                    f"{selectors.S_POST_BUTTON}[aria-disabled]"
                ).wait_for(
                    state="detached", timeout=30_000
                )  # Khi aria-disabled detached, nghĩa là nó đã bị xóa/thay đổi -> nút đã kích hoạt
                print(f"{log_prefix}     Nút 'Đăng' đã được kích hoạt.")
                post_btn_locators.first.click()
                print(f"{log_prefix}     Đã click nút 'Đăng'.")
            except PlaywrightTimeoutError as e:
                print(
                    f"{log_prefix}     LỖI: Hết thời gian chờ khi chờ nút 'Đăng' được kích hoạt hoặc click: {e}. Bài viết có thể chưa được đăng."
                )
                signals.failed_signal.emit(
                    task,
                    "Không thể click nút Đăng hoặc nút bị vô hiệu hóa.",
                    settings.get("raw_proxy"),
                )
                continue  # Bỏ qua nhóm này vì không thể đăng bài

            # Bước 5.9: Chờ dialog tạo bài viết đóng lại (detached)
            print(f"{log_prefix}     Chờ dialog tạo bài viết đóng lại.")
            try:
                dialog_container_locator.wait_for(state="detached", timeout=MIN)
                print(f"{log_prefix}     Dialog tạo bài viết đã đóng thành công.")
            except PlaywrightTimeoutError as e:
                print(
                    f"{log_prefix}     LỖI: Hết thời gian chờ khi chờ dialog tạo bài viết đóng lại: {e}. Có thể bài viết chưa đăng thành công hoặc dialog bị kẹt."
                )
                signals.failed_signal.emit(
                    task,
                    "Dialog tạo bài viết không đóng lại sau khi đăng. Có thể đăng thất bại.",
                    settings.get("raw_proxy"),
                )
                continue  # Bỏ qua nhóm này nếu dialog không đóng

            sleep(random.uniform(1, 3))  # Dừng một chút sau khi đăng thành công

            # Bước 5.10: Phát tín hiệu thành công cho nhóm này
            signals.succeeded_signal.emit(
                task,
                f"Đã đăng bài thành công trong nhóm: {group_url}.",
                settings.get("raw_proxy"),
            )
            current_group_processed += 1
            print(
                f"{log_prefix}   Đã xử lý thành công {current_group_processed}/{groups_num} nhóm."
            )
            emit_progress_update()  # Tiến độ sau khi đăng bài thành công cho nhóm này

            # Kiểm tra nếu đã xử lý đủ số nhóm mong muốn
            if current_group_processed >= groups_num:
                print(
                    f"{log_prefix} Đã xử lý đủ {groups_num} nhóm. Kết thúc tác vụ đăng bài."
                )
                break  # Dừng vòng lặp nếu đã đạt số nhóm cần xử lý

        print(
            f"{log_prefix} Đã hoàn thành vòng lặp xử lý nhóm. Tổng số nhóm đã đăng: {current_group_processed}/{groups_num}."
        )

        # Kết thúc tác vụ
        print(f"{log_prefix} Tác vụ thảo luận hoàn tất thành công.")
        return True
    except Exception as e:
        # Bắt các lỗi không mong đợi khác trong toàn bộ hàm
        error_type = type(e).__name__
        error_message = str(e)

        # Lấy toàn bộ traceback, bao gồm file và dòng
        full_traceback = traceback.format_exc()

        print(
            f"{log_prefix} LỖI KHÔNG MONG ĐỢI: Xảy ra lỗi tổng quát trong quá trình thực hiện tác vụ:",
            file=sys.stderr,
        )
        print(f"  Loại lỗi: {error_type}", file=sys.stderr)
        print(f"  Thông báo: {error_message}", file=sys.stderr)
        print(f"  Chi tiết Traceback:\n{full_traceback}", file=sys.stderr)

        # Gửi thông tin lỗi chi tiết hơn qua signal
        signals.error_signal.emit(
            task,
            f"Lỗi không mong đợi: {error_message}\nChi tiết: Xem log console để biết đầy đủ traceback.",
        )
        return False


ACTION_MAP = {
    "launch_browser": do_launch_browser,
    "marketplace": do_marketplace,
    # "marketplace_and_groups": do_marketplace_and_groups,
    "discussion": do_discussion,
}
