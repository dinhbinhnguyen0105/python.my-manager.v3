# src/views/product/dialog_re_product.py
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QDialog

from src.my_types import RealEstateProductType
from src.ui.dialog_re_product_ui import Ui_Dialog_REProduct


class DialogREProduct(QDialog, Ui_Dialog_REProduct):
    product_data = pyqtSignal(RealEstateProductType)

    def __init__(self, parent=None):
        super(DialogREProduct, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Real estate product")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setModal(False)
        self.buttonBox.button(self.buttonBox.StandardButton.Save).disconnect()
        self.buttonBox.button(self.buttonBox.StandardButton.Save).clicked.connect(
            self.on_accepted
        )

        # self.

        # TODO: initialize options

    @pyqtSlot()
    def on_accepted(self):
        print("accepted!")
        self.accept()
