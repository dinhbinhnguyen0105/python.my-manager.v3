# src/views/product/product.py
import os, sys
from typing import List, Any, Optional
from PyQt6.QtGui import QAction, QPixmap, QMouseEvent
from PyQt6.QtWidgets import QWidget, QMenu, QMessageBox
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
    QPoint,
    QSortFilterProxyModel,
    QModelIndex,
    QVariant,
    QItemSelection,
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

from src.models.setting_model import SettingUserDataDirModel
from src.services.setting_service import SettingUserDataDirModel
from src.controllers.setting_controller import SettingUserDataDirController

from src.views.product.dialog_create_re_product import DialogCreateREProduct
from src.views.product.dialog_update_re_product import DialogUpdateREProduct

from src.my_types import RealEstateProductType


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
        setting_controller: SettingUserDataDirController,
        parent=None,
    ):
        super(RealEstateProductPage, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Real estate product")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._product_controller = product_controller
        self._template_controller = template_controller
        self._setting_controller = setting_controller

        self.base_product_model: RealEstateProductModel = (
            self._product_controller.service.model
        )
        self.base_template_model: RealEstateTemplateModel = (
            self._template_controller.service.model
        )
        self.proxy_product_model = MultiFieldFilterProxyModel()
        self.proxy_product_model.setSourceModel(self.base_product_model)

        self.udd_container_dir = self._setting_controller.get_selected_user_data_dir()
        self.current_product: Optional[RealEstateProductType] = None
        self.current_image_paths: List[str] = []

        self.init_ui()
        self.init_events()

    def init_ui(self):
        self.set_product_table()

    def init_events(self):
        self.action_create_btn.clicked.connect(self.on_create_product)
        self.details_container_w.setHidden(True)

    def get_selected_ids(self):
        selected_indexes = self.products_table.selectionModel().selectedRows()
        ids = []
        for proxy_index in selected_indexes:
            # Chuyển sang index của source model
            source_index = self.proxy_product_model.mapToSource(proxy_index)
            source_model = self.proxy_product_model.sourceModel()
            # Tìm cột id
            id_col = (
                source_model.fieldIndex("id")
                if hasattr(source_model, "fieldIndex")
                else 0
            )
            id_index = source_model.index(source_index.row(), id_col)
            id_value = source_model.data(id_index, Qt.ItemDataRole.DisplayRole)
            ids.append(id_value)
        return sorted(ids)

    def set_product_table(self):
        self.products_table.setModel(self.proxy_product_model)
        self.products_table.setSortingEnabled(True)
        self.products_table.setSelectionBehavior(
            self.products_table.SelectionBehavior.SelectRows
        )
        self.products_table.setSelectionMode(
            self.products_table.SelectionMode.SingleSelection
        )
        self.products_table.setEditTriggers(
            self.products_table.EditTrigger.NoEditTriggers
        )

        self.products_table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        for i in range(self.base_product_model.columnCount()):
            column_name = self.base_product_model.headerData(
                i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            )
            if column_name in [
                "id",
                "availability",
                "province",
                "district",
                "image_dir",
            ]:
                self.products_table.setColumnHidden(i, True)
        self.products_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.products_table.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos: QPoint):
        proxy_index = self.products_table.indexAt(pos)
        if not proxy_index.isValid():
            return

        # Chuyển sang index của source model
        source_index = self.proxy_product_model.mapToSource(proxy_index)
        source_model = self.proxy_product_model.sourceModel()

        # Tìm cột status
        availability_col = (
            source_model.fieldIndex("availability")
            if hasattr(source_model, "fieldIndex")
            else 0
        )
        availability_index = source_model.index(source_index.row(), availability_col)
        availability_value: int = source_model.data(
            availability_index, Qt.ItemDataRole.DisplayRole
        )

        id_col = (
            source_model.fieldIndex("id") if hasattr(source_model, "fieldIndex") else 0
        )
        id_index = source_model.index(source_index.row(), id_col)
        id_value = source_model.data(id_index, Qt.ItemDataRole.DisplayRole)

        global_pos = self.products_table.mapToGlobal(pos)
        menu = QMenu(self.products_table)

        if availability_value == 1:
            set_unavailable = QAction("Change to unavailable", self)
            menu.addAction(set_unavailable)
            set_unavailable.triggered.connect(self.handle_change_availability)
        else:
            set_available = QAction("Change to available", self)
            menu.addAction(set_available)
            set_available.triggered.connect(self.handle_change_availability)

        update_action = QAction("Update", self)
        delete_action = QAction("Delete", self)
        update_action.triggered.connect(
            lambda _, record_id=id_value: self.on_update_product(record_id)
        )
        delete_action.triggered.connect(
            lambda _, record_id=id_value: self.handle_delete_product(record_id)
        )
        menu.addAction(update_action)
        menu.addAction(delete_action)

        menu.popup(global_pos)

    @pyqtSlot()
    def on_create_product(self):
        self.re_create_product_dialog = DialogCreateREProduct(self)
        self.re_create_product_dialog.request_new_pid_signal.connect(
            self.handle_new_pid
        )
        self.re_create_product_dialog.product_data_signal.connect(
            self.handle_create_new_product
        )
        self.re_create_product_dialog.show()

    @pyqtSlot(int)
    def on_update_product(self, record_id: int):
        product_info = self._product_controller.read_product(record_id)
        product_images = self._product_controller.get_images_by_path(
            product_info.image_dir
        )
        self.re_update_re_dialog = DialogUpdateREProduct(
            image_paths=product_images,
            product_data=product_info,
            parent=self,
        )
        self.re_update_re_dialog.product_data_signal.connect(self.handle_update_product)
        self.re_update_re_dialog.show()

    @pyqtSlot(str)
    def handle_new_pid(self, transaction_type: str):
        new_pid = self._product_controller.initialize_new_pid(transaction_type)
        if hasattr(self, "re_create_product_dialog"):
            self.re_create_product_dialog.pid_input.setText(new_pid)

    @pyqtSlot(list, RealEstateProductType)
    def handle_create_new_product(
        self, image_paths: List[str], product_data: RealEstateProductType
    ):
        if not self.udd_container_dir:
            QMessageBox.critical(
                self,
                "ERROR",
                "The 'user_data_dir' path is not accessible. Please check your settings.",
            )
            return False
        self._product_controller.create_product(
            os.path.join(self.udd_container_dir, "..", "images"),
            image_paths,
            product_data,
        )

    @pyqtSlot(int)
    def handle_delete_product(self, record_id: int):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._product_controller.delete_product(record_id)

    @pyqtSlot()
    def handle_change_availability(self):
        selected_ids = self.get_selected_ids()
        if len(selected_ids):
            self._product_controller.toggle_availability(selected_ids[0])

    @pyqtSlot(RealEstateProductType)
    def handle_update_product(self, product_data: RealEstateProductType):
        self._product_controller.update_product(
            record_id=product_data.id, product_data=product_data
        )

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_selection_changed(
        self,
        selected: QItemSelection,
        deselected: QItemSelection,
    ):
        if not selected.indexes():
            self.details_container_w.setHidden(True)
            return
        selected_index = selected.indexes()[0]
        row = selected_index.row()
        item_id = self.proxy_product_model.data(
            self.proxy_product_model.index(row, 0), Qt.ItemDataRole.DisplayRole
        )
        self.current_product = self._product_controller.read_product(item_id)
        self.current_image_paths = self._product_controller.get_images_by_path(
            self.current_product.image_dir
        )
        self.details_container_w.setHidden(False)
        self.image_label.mousePressEvent = self.on_image_clicked
        self.display_image(self.current_image_paths)

        # TODO get data as RealEstateProductType  connect to template => display to detail

    def set_product_details(self):
        self.image_label
        self.detail_text
        self.action_templates_btn
        self.action_default_btn
        self.action_random_btn
        # self.

    def display_image(self, image_paths: List[str]):
        if not len(image_paths):
            self.image_label.setText("Failed to load image.")
        pixmap = QPixmap(image_paths[0])
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.image_label.setText("Failed to load image.")

    def display_template(self, product_data: RealEstateProductType):
        # self._template_controller.
        pass

    @pyqtSlot(QMouseEvent)
    def on_image_clicked(self, ev: QMouseEvent):
        if not self.current_image_paths:
            return
        image_path = self.current_image_paths[0]
        folder_path = os.path.dirname(image_path)
        if os.path.exists(folder_path):
            if sys.platform == "darwin":
                os.system(f'open "{folder_path}"')
            elif sys.platform.startswith("win"):
                os.startfile(folder_path)
            else:
                os.system(f'xdg-open "{folder_path}"')
