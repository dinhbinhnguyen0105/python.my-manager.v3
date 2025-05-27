# src/views/product/product.py
from typing import List, Any
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
    QPoint,
    QSortFilterProxyModel,
    QModelIndex,
    QVariant,
)
from src.ui.page_re_product_ui import Ui_PageREProduct
from src.controllers.product_controller import (
    RealEstateProductController,
    RealEstateTemplateController,
)
from src.services.product_service import (
    RealEstateProductService,
    RealEstateTemplateService,
)
from src.models.product_model import (
    RealEstateProductModel,
    RealEstateTemplateModel,
)

from src.views.product.dialog_re_product import DialogREProduct


class MultiFieldFilterProxyModel(QSortFilterProxyModel):
    SERIAL_NUMBER_COLUMN_INDEX = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filters = {}

    def set_filter(self, column, text):
        self.filters[column] = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        for column, text in self.filters.items():
            if text:
                index = model.index(source_row, column, source_parent)
                data = str(model.data(index, Qt.ItemDataRole.DisplayRole)).lower()
                if text not in data:
                    return False
        return True


class RealEstateProductPage(QWidget, Ui_PageREProduct):
    def __init__(
        self,
        product_controller: RealEstateProductController,
        template_controller: RealEstateTemplateController,
        parent=None,
    ):
        super(RealEstateProductPage, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Real estate product")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._product_controller = product_controller
        self._template_controller = template_controller

        self.base_product_model: RealEstateProductModel = (
            self._product_controller.service.model
        )
        self.base_template_model: RealEstateTemplateModel = (
            self._template_controller.service.model
        )
        self.proxy_product_model = MultiFieldFilterProxyModel()
        self.proxy_product_model.setSourceModel(self.base_product_model)

        self.init_ui()
        self.init_events()

    def init_ui(self):
        self.set_product_table()

    def init_events(self):
        self.action_create_btn.clicked.connect(self.on_create_product)

    def set_product_table(self):
        self.products_table.setModel(self.proxy_product_model)
        self.products_table.setSortingEnabled(True)
        self.products_table.setSelectionBehavior(
            self.products_table.SelectionBehavior.SelectRows
        )
        self.products_table.setEditTriggers(
            self.products_table.EditTrigger.NoEditTriggers
        )

        for i in range(self.base_product_model.columnCount()):
            column_name = self.base_product_model.headerData(
                i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            )
            if column_name in ["id", "status", "province", "district"]:
                self.products_table.setColumnHidden(i, True)

    @pyqtSlot()
    def on_create_product(self):
        dialog = DialogREProduct(self)
        dialog.show()
        # dialog.accepted.connect(self.handle_create_product)

    # @pyqtSlot()
