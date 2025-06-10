# src/my_types.py
from dataclasses import dataclass
from typing import Optional, List

from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class UserType:
    id: Optional[int]
    uid: Optional[str]
    username: Optional[str]
    password: Optional[str]
    two_fa: Optional[str]
    email: Optional[str]
    email_password: Optional[str]
    phone_number: Optional[str]
    note: Optional[str]
    type: Optional[str]
    user_group: Optional[int]
    mobile_ua: Optional[str]
    desktop_ua: Optional[str]
    status: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class UserListedProductType:
    id: Optional[int]
    id_user: int
    pid: str
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class SettingProxyType:
    id: Optional[int]
    value: str
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class SettingUserDataDirType:
    id: Optional[int]
    value: str
    is_selected: int
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class RealEstateProductType:
    id: Optional[int]
    pid: Optional[str]
    status: Optional[int]
    transaction_type: Optional[str]
    province: Optional[str]
    district: Optional[str]
    ward: Optional[str]
    street: Optional[str]
    category: Optional[str]
    area: Optional[float]
    price: Optional[float]
    legal: Optional[str]
    structure: Optional[float]
    function: Optional[str]
    building_line: Optional[str]
    furniture: Optional[str]
    description: Optional[str]
    image_dir: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class RealEstateTemplateType:
    id: Optional[int]
    transaction_type: Optional[str]
    category: Optional[str]
    is_default: Optional[int]
    part: Optional[str]
    value: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class MiscProductType:
    id: Optional[int]
    pid: Optional[str]
    category: Optional[int]
    title: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[int]


@dataclass
class SellPayloadType:
    title: str
    description: str
    image_paths: List[str]


@dataclass
class RobotTaskType:
    user_info: UserType
    action_name: Optional[str]
    action_payload: Optional[SellPayloadType]


@dataclass
class BrowserType(RobotTaskType):
    is_mobile: bool
    headless: bool
    udd: str


class BrowserWorkerSignals(QObject):
    progress_signal = pyqtSignal(
        BrowserType, str, int, int
    )  # task, message, current_progress, total_progress
    task_progress_signal = pyqtSignal(str, list)
    failed_signal = pyqtSignal(BrowserType, str, str)  # task, message, raw_proxy
    error_signal = pyqtSignal(BrowserType, str)  # task, message
    succeeded_signal = pyqtSignal(BrowserType, str, str)  # task, message, raw_proxy
    proxy_unavailable_signal = pyqtSignal(BrowserType, str)  # task, raw_proxy
    proxy_not_ready_signal = pyqtSignal(BrowserType, str)  # task, raw_proxy
