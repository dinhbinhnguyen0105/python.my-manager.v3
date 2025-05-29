# src/views/product/dialog_update_re_product.py
from typing import List
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QDialog, QRadioButton, QMessageBox
from PyQt6.QtGui import QDoubleValidator, QDragEnterEvent, QDropEvent, QPixmap

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


class DialogUpdateREProduct(QDialog, Ui_Dialog_REProduct):
    def __init__(
        self, image_paths: List[str], product_data: RealEstateProductType, parent=None
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Update new re product")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setModal(False)
        self.buttonBox.button(self.buttonBox.StandardButton.Save).disconnect()
        self.buttonBox.button(self.buttonBox.StandardButton.Save).clicked.connect(
            self.on_accepted
        )
        # self.transaction_option_widgets: List[QRadioButton] = []
        self.image_paths: List[str] = image_paths
        # self.transaction_value: str = ""

        self._display_image(image_paths)

    def init_options(self):
        # for transaction_type in RE_TRANSACTION.keys():
        #     transaction_option = QRadioButton(
        #         RE_TRANSACTION[transaction_type].capitalize()
        #     )

        #     transaction_option.setStyleSheet("padding: 0 24px;")
        #     transaction_option.setProperty("value", transaction_type)
        #     transaction_option.clicked.connect(
        #         lambda _, opt=transaction_option: self.on_transaction_option_clicked(
        #             opt.property("value")
        #         )
        #     )
        #     self.transaction_option_widgets.append(transaction_option)
        #     self.transaction_container_w.layout().addWidget(transaction_option)
        # self.transaction_container_w.layout().setAlignment(
        #     Qt.AlignmentFlag.AlignJustify
        # )

        self.transaction_container_w.setHidden(True)
        self.pid_input.setDisabled(True)

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

    def init_data(self):

        pass

    def _display_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_input.setPixmap(
                pixmap.scaled(
                    self.image_input.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.image_input.setText("Failed to load image.")
