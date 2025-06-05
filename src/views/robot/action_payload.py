# src/views/robot/action_payload.py

from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
)
from src.ui.action_payload_ui import Ui_ActionPayloadContainer


class ActionPayload(QWidget, Ui_ActionPayloadContainer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Action payload")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        self.action_name
        self.action_payload
        pass

    def setup_events(self):
        pass


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    w = ActionPayload()
    w.show()
    sys.exit(app.exec())
