# src/controllers/user_task_manager.py
from typing import Optional, List
from datetime import datetime
import string, secrets

from PyQt6.QtCore import QObject, QThreadPool, pyqtSignal

from src.services.user_service import UserService
from src.controllers.base_controller import BaseController


class UserTaskManager(BaseController):
    def __init__(self, user_service: UserService, parent=None):
        super().__init__(service=user_service, parent=parent)
        self._user_service = user_service
        # self._current_task_progress:Optional[Robo]
