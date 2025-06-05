# src/controllers/robot_controller.py

from src.robot.browser_manager import BrowserManager
from src.controllers.base_controller import BaseController
from src.services.user_service import UserService
from src.services.setting_service import SettingProxyService, SettingUserDataDirService
from src.services.product_service import (
    MiscProductService,
    RealEstateProductService,
    RealEstateTemplateService,
)


class RobotController(BaseController):
    def __init__(
        self,
        user_service: UserService,
        misc_product_service: MiscProductService,
        re_product_service: RealEstateProductService,
        re_template_service: RealEstateTemplateService,
        setting_proxy_service: SettingProxyService,
        setting_udd_service: SettingUserDataDirService,
        parent=None,
    ):
        super().__init__(service=user_service, parent=parent)
        self._user_service = user_service
        self._misc_product_service = misc_product_service
        self._re_product_service = re_product_service
        self._re_template_service = re_template_service
        self._setting_proxy_service = setting_proxy_service
        self._setting_udd_service = setting_udd_service
