# src/views/product/dialog_re_product.py
from typing import List
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QDialog, QRadioButton
from PyQt6.QtGui import QDoubleValidator

from src.my_types import RealEstateProductType
from src.ui.dialog_re_product_ui import Ui_Dialog_REProduct

from src.my_constants import (
    RE_TRANSACTION,
    RE_AVAILABILITY,
    RE_CATEGORY,
    RE_PROVINCE,
    RE_DISTRICT,
    RE_WARD,
    RE_BUILDING_LINE,
    RE_LEGAL,
    RE_FURNITURE,
)


class DialogREProduct(QDialog, Ui_Dialog_REProduct):
    product_data = pyqtSignal(RealEstateProductType)
    request_new_pid_signal = pyqtSignal(str)

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

        self.transaction_option_widgets: List[QRadioButton] = []

        self.init_options()
        self.init_validate_input()
        self.init_events()

    def init_options(self):
        for _key in RE_TRANSACTION.keys():
            transaction_option = QRadioButton(RE_TRANSACTION[_key].capitalize())

            transaction_option.setStyleSheet("padding: 0 24px;")
            # transaction_option.setProperty("value", )
            transaction_option.clicked.connect(
                # lambda: self.request_new_pid_signal(transaction_option.property("value"))
                lambda: print(_key)
            )
            self.transaction_option_widgets.append(transaction_option)
            self.transaction_container_w.layout().addWidget(transaction_option)
        self.transaction_container_w.layout().setAlignment(
            Qt.AlignmentFlag.AlignJustify
        )

        self.categories_combobox.clear()
        for _key in RE_CATEGORY.keys():
            self.categories_combobox.addItem(RE_CATEGORY[_key].capitalize(), _key)
        self.availability_combobox.clear()
        for _key in RE_AVAILABILITY:
            self.availability_combobox.addItem(RE_AVAILABILITY[_key].capitalize(), _key)
        self.wards_combobox.clear()
        for _key in RE_WARD:
            self.wards_combobox.addItem(RE_WARD[_key].capitalize(), _key)
        self.districts_combobox.clear()
        for _key in RE_DISTRICT:
            self.districts_combobox.addItem(RE_DISTRICT[_key].capitalize(), _key)
        self.provinces_combobox.clear()
        for _key in RE_PROVINCE:
            self.provinces_combobox.addItem(RE_PROVINCE[_key].capitalize(), _key)
        self.furniture_s_combobox.clear()
        for _key in RE_FURNITURE:
            self.furniture_s_combobox.addItem(RE_FURNITURE[_key].capitalize(), _key)
        self.building_line_s_combobox.clear()
        for _key in RE_BUILDING_LINE:
            self.building_line_s_combobox.addItem(
                RE_BUILDING_LINE[_key].capitalize(), _key
            )
        self.legal_s_combobox.clear()
        for _key in RE_LEGAL:
            self.legal_s_combobox.addItem(RE_LEGAL[_key].capitalize(), _key)

    def init_validate_input(self):
        validator = QDoubleValidator(self)
        validator.setDecimals(2)
        self.area_input.setValidator(validator)
        self.price_input.setValidator(validator)
        self.structure_input.setValidator(validator)

    def init_events(self):
        pass
        # for transaction_option in self.transaction_option_widgets:
        # print(transaction_option.property("value"))

    # @pyqtSlot(str)
    # def on_transaction_clicked(self, str):

    @pyqtSlot()
    def on_accepted(self):
        print("accepted!")
        self.accept()
