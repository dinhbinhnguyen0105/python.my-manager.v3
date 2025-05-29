# src/controllers/product_controller.py
from typing import Optional, List

from src.controllers.base_controller import BaseController
from src.services.product_service import (
    RealEstateProductService,
    RealEstateTemplateService,
    MiscProductService,
)
from src.my_types import RealEstateProductType, RealEstateTemplateType, MiscProductType


class RealEstateProductController(BaseController):
    def __init__(self, service: RealEstateProductService, parent=None):
        super().__init__(service, parent)
        self.service = service

    def create_product(
        self,
        image_dir_container: str,
        image_paths: List[str],
        product_data: RealEstateProductType,
    ):
        try:
            if not isinstance(product_data, RealEstateProductType):
                raise TypeError(
                    f"Expected RealEstateProductType, got {type(product_data)}"
                )
            if not self.service.create(image_dir_container, image_paths, product_data):
                self.error_signal.emit("Failed to create real estate product.")
                return False
            self.success_signal.emit("Successfully created real estate product.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.create_product] Error: {e}")
            self.error_signal.emit("Error occurred while creating real estate product.")
            return False

    def read_product(self, record_id: int) -> Optional[RealEstateProductType]:
        try:
            product = self.service.read(record_id)
            if not product:
                self.warning_signal.emit(
                    f"Failed to read real estate product (id: {record_id})."
                )
                return None
            return product
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_product] Error: {e}")
            self.error_signal.emit("Error occurred while reading real estate product.")
            return None

    def read_all_products(self) -> List[RealEstateProductType]:
        try:
            return self.service.read_all()
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_all_products] Error: {e}")
            self.error_signal.emit(
                "Error occurred while reading all real estate products."
            )
            return []

    def update_product(
        self, record_id: int, product_data: RealEstateProductType
    ) -> bool:
        try:
            if not isinstance(product_data, RealEstateProductType):
                raise TypeError(
                    f"Expected RealEstateProductType, got {type(product_data)}"
                )
            if not self.service.update(record_id, product_data):
                self.error_signal.emit("Failed to update real estate product.")
                return False
            self.success_signal.emit("Successfully updated real estate product.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.update_product] Error: {e}")
            self.error_signal.emit("Error occurred while updating real estate product.")
            return False

    def delete_product(self, record_id: int) -> bool:
        try:
            if not self.service.delete(record_id):
                self.operation_warning_signal.emit(
                    f"Failed to delete real estate product (id: {record_id})."
                )
                return False
            self.success_signal.emit(
                f"Successfully deleted real estate product (id: {record_id})."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_product] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting real estate product."
            )
            return False

    def delete_multiple_products(self, record_ids: List[int]) -> bool:
        try:
            self.service.delete_multiple(record_ids)
            self.success_signal.emit(
                "Successfully deleted multiple real estate products."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_multiple_products] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting multiple real estate products."
            )
            return False

    def import_products(self, products: List[RealEstateProductType]):
        try:
            self.service.import_data(products)
            self.success_signal.emit("Successfully imported real estate products.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.import_products] Error: {e}")
            self.error_signal.emit(
                "Error occurred while importing real estate products."
            )
            return False

    def toggle_availability(self, product_id: int) -> bool:
        try:
            result = self.service.toggle_availability(product_id)
            if result:
                self.success_signal.emit(f"Toggled status for product ID {product_id}.")
                self.data_changed_signal.emit()
            else:
                self.warning_signal.emit(
                    f"Failed to toggle status for product ID {product_id}."
                )
            return result
        except Exception as e:
            print(f"[{self.__class__.__name__}.toggle_availability] Error: {e}")
            self.error_signal.emit("Error occurred while toggling product status.")
            return False

    def initialize_new_pid(self, transaction_type: str) -> str:
        try:
            self.success_signal.emit(
                f"Successfully initialized new PID for transaction type '{transaction_type}'"
            )
            return self.service.initialize_new_pid(transaction_type)
        except Exception as e:
            print(f"[{self.__class__.__name__}.initialize_new_pid] Error: {e}")
            self.error_signal.emit(
                f"Failed to initialize new PID for transaction type '{transaction_type}'. Error: {e}"
            )
            return False


class RealEstateTemplateController(BaseController):
    def __init__(self, service: RealEstateTemplateService, parent=None):
        super().__init__(service, parent)

    def create_template(self, template_data: RealEstateTemplateType):
        try:
            if not isinstance(template_data, RealEstateTemplateType):
                raise TypeError(
                    f"Expected RealEstateTemplateType, got {type(template_data)}"
                )
            if not self.service.create(template_data):
                self.error_signal.emit("Failed to create real estate template.")
                return False
            self.success_signal.emit("Successfully created real estate template.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.create_template] Error: {e}")
            self.error_signal.emit(
                "Error occurred while creating real estate template."
            )
            return False

    def read_template(self, record_id: int) -> Optional[RealEstateTemplateType]:
        try:
            template = self.service.read(record_id)
            if not template:
                self.warning_signal.emit(
                    f"Failed to read real estate template (id: {record_id})."
                )
                return None
            return template
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_template] Error: {e}")
            self.error_signal.emit("Error occurred while reading real estate template.")
            return None

    def read_all_templates(self) -> List[RealEstateTemplateType]:
        try:
            return self.service.read_all()
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_all_templates] Error: {e}")
            self.error_signal.emit(
                "Error occurred while reading all real estate templates."
            )
            return []

    def update_template(
        self, record_id: int, template_data: RealEstateTemplateType
    ) -> bool:
        try:
            if not isinstance(template_data, RealEstateTemplateType):
                raise TypeError(
                    f"Expected RealEstateTemplateType, got {type(template_data)}"
                )
            if not self.service.update(record_id, template_data):
                self.error_signal.emit("Failed to update real estate template.")
                return False
            self.success_signal.emit("Successfully updated real estate template.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.update_template] Error: {e}")
            self.error_signal.emit(
                "Error occurred while updating real estate template."
            )
            return False

    def delete_template(self, record_id: int) -> bool:
        try:
            if not self.service.delete(record_id):
                self.operation_warning_signal.emit(
                    f"Failed to delete real estate template (id: {record_id})."
                )
                return False
            self.success_signal.emit(
                f"Successfully deleted real estate template (id: {record_id})."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_template] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting real estate template."
            )
            return False

    def delete_multiple_templates(self, record_ids: List[int]) -> bool:
        try:
            self.service.delete_multiple(record_ids)
            self.success_signal.emit(
                "Successfully deleted multiple real estate templates."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_multiple_templates] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting multiple real estate templates."
            )
            return False

    def import_templates(self, templates: List[RealEstateTemplateType]):
        try:
            self.service.import_data(templates)
            self.success_signal.emit("Successfully imported real estate templates.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.import_templates] Error: {e}")
            self.error_signal.emit(
                "Error occurred while importing real estate templates."
            )
            return False


class MiscProductController(BaseController):
    def __init__(self, service: MiscProductService, parent=None):
        super().__init__(service, parent)

    def create_product(self, product_data: MiscProductType):
        try:
            if not isinstance(product_data, MiscProductType):
                raise TypeError(f"Expected MiscProductType, got {type(product_data)}")
            if not self.service.create(product_data):
                self.error_signal.emit("Failed to create misc product.")
                return False
            self.success_signal.emit("Successfully created misc product.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.create_product] Error: {e}")
            self.error_signal.emit("Error occurred while creating misc product.")
            return False

    def read_product(self, record_id: int) -> Optional[MiscProductType]:
        try:
            product = self.service.read(record_id)
            if not product:
                self.warning_signal.emit(
                    f"Failed to read misc product (id: {record_id})."
                )
                return None
            return product
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_product] Error: {e}")
            self.error_signal.emit("Error occurred while reading misc product.")
            return None

    def read_all_products(self) -> List[MiscProductType]:
        try:
            return self.service.read_all()
        except Exception as e:
            print(f"[{self.__class__.__name__}.read_all_products] Error: {e}")
            self.error_signal.emit("Error occurred while reading all misc products.")
            return []

    def update_product(self, record_id: int, product_data: MiscProductType) -> bool:
        try:
            if not isinstance(product_data, MiscProductType):
                raise TypeError(f"Expected MiscProductType, got {type(product_data)}")
            if not self.service.update(record_id, product_data):
                self.error_signal.emit("Failed to update misc product.")
                return False
            self.success_signal.emit("Successfully updated misc product.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.update_product] Error: {e}")
            self.error_signal.emit("Error occurred while updating misc product.")
            return False

    def delete_product(self, record_id: int) -> bool:
        try:
            if not self.service.delete(record_id):
                self.operation_warning_signal.emit(
                    f"Failed to delete misc product (id: {record_id})."
                )
                return False
            self.success_signal.emit(
                f"Successfully deleted misc product (id: {record_id})."
            )
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_product] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting misc product."
            )
            return False

    def delete_multiple_products(self, record_ids: List[int]) -> bool:
        try:
            self.service.delete_multiple(record_ids)
            self.success_signal.emit("Successfully deleted multiple misc products.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.delete_multiple_products] Error: {e}")
            self.operation_error_signal.emit(
                "Error occurred while deleting multiple misc products."
            )
            return False

    def import_products(self, products: List[MiscProductType]):
        try:
            self.service.import_data(products)
            self.success_signal.emit("Successfully imported misc products.")
            self.data_changed_signal.emit()
            return True
        except Exception as e:
            print(f"[{self.__class__.__name__}.import_products] Error: {e}")
            self.error_signal.emit("Error occurred while importing misc products.")
            return False

    def toggle_availability(self, product_id: str) -> bool:
        try:
            result = self.service.toggle_availability(product_id)
            if result:
                self.success_signal.emit(
                    f"Toggled status for misc product ID {product_id}."
                )
                self.data_changed_signal.emit()
            else:
                self.warning_signal.emit(
                    f"Failed to toggle status for misc product ID {product_id}."
                )
            return result
        except Exception as e:
            print(f"[{self.__class__.__name__}.toggle_availability] Error: {e}")
            self.error_signal.emit("Error occurred while toggling misc product status.")
            return False
