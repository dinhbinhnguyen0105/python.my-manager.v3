# src/services/product_service.py
from typing import Optional, List
from src.services.base_service import BaseService
from src.models.product_model import (
    RealEstateProductModel,
    RealEstateTemplateModel,
    MiscProductModel,
)
from src.my_types import RealEstateProductType, RealEstateTemplateType, MiscProductType


class RealEstateProductService(BaseService):
    DATA_TYPE = RealEstateProductType

    def __init__(self, model: RealEstateProductModel):
        if not isinstance(model, RealEstateProductModel):
            raise TypeError(
                "model must be an instance of RealEstateProductModel or its subclass."
            )
        super().__init__(model)

    def create(self, payload: RealEstateProductType) -> bool:
        return super().create(payload)

    def read(self, record_id: int) -> Optional[RealEstateProductType]:
        return super().read(record_id)

    def read_all(self) -> List[RealEstateProductType]:
        return super().read_all()

    def update(self, record_id: int, payload: RealEstateProductType) -> bool:
        return super().update(record_id, payload)

    def delete(self, record_id: int) -> bool:
        return super().delete(record_id)

    def delete_multiple(self, record_ids: List[int]):
        return super().delete_multiple(record_ids)

    def import_data(self, payload: List[RealEstateProductType]):
        return super().import_data(payload)

    def find_by_pid(self, pid: str) -> Optional[RealEstateProductType]:
        return self._find_by_model_index(find_method_name="find_row_by_pid", value=pid)

    def toggle_status(self, product_id: str) -> bool:
        product = self.find_by_pid(product_id)
        if product is None:
            print(
                f"[{self.__class__.__name__}.toggle_status] Product with ID '{product_id}' not found."
            )
            return False

        current_status = product.status
        if current_status == 0:
            new_status = 1
        elif current_status == 1:
            new_status = 0
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Unexpected status value for product ID '{product_id}': {current_status}. Cannot toggle."
            )
            return False

        product.status = new_status
        update_success = self.update(product.id, product)
        if update_success:
            print(
                f"[{self.__class__.__name__}.toggle_status] Successfully toggled status for product ID '{product_id}' to {new_status}."
            )
            return True
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Failed to update status for product ID '{product_id}'."
            )
            return False


class RealEstateTemplateService(BaseService):
    DATA_TYPE = RealEstateTemplateType

    def __init__(self, model: RealEstateTemplateModel):
        if not isinstance(model, RealEstateTemplateModel):
            raise TypeError(
                "model must be an instance of RealEstateTemplateModel or its subclass."
            )
        super().__init__(model)

    def create(self, payload: RealEstateTemplateType) -> bool:
        return super().create(payload)

    def read(self, record_id: int) -> Optional[RealEstateTemplateType]:
        return super().read(record_id)

    def read_all(self) -> List[RealEstateTemplateType]:
        return super().read_all()

    def update(self, record_id: int, payload: RealEstateTemplateType) -> bool:
        return super().update(record_id, payload)

    def delete(self, record_id: int) -> bool:
        return super().delete(record_id)

    def delete_multiple(self, record_ids: List[int]):
        return super().delete_multiple(record_ids)

    def import_data(self, payload: List[RealEstateTemplateType]):
        return super().import_data(payload)


class MiscProductService(BaseService):
    DATA_TYPE = MiscProductType

    def __init__(self, model: MiscProductModel):
        if not isinstance(model, MiscProductModel):
            raise TypeError(
                "model must be an instance of MiscProductModel or its subclass."
            )
        super().__init__(model)

    def create(self, payload: MiscProductModel) -> bool:
        return super().create(payload)

    def read(self, record_id: int) -> Optional[MiscProductModel]:
        return super().read(record_id)

    def read_all(self) -> List[MiscProductModel]:
        return super().read_all()

    def update(self, record_id: int, payload: MiscProductModel) -> bool:
        return super().update(record_id, payload)

    def delete(self, record_id: int) -> bool:
        return super().delete(record_id)

    def delete_multiple(self, record_ids: List[int]):
        return super().delete_multiple(record_ids)

    def import_data(self, payload: List[MiscProductModel]):
        return super().import_data(payload)

    def find_by_pid(self, pid: str) -> Optional[MiscProductModel]:
        return self._find_by_model_index(find_method_name="find_row_by_pid", value=pid)

    def toggle_status(self, product_id: str) -> bool:
        product = self.find_by_pid(product_id)
        if product is None:
            print(
                f"[{self.__class__.__name__}.toggle_status] Product with ID '{product_id}' not found."
            )
            return False

        current_status = product.status
        if current_status == 0:
            new_status = 1
        elif current_status == 1:
            new_status = 0
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Unexpected status value for product ID '{product_id}': {current_status}. Cannot toggle."
            )
            return False

        product.status = new_status
        update_success = self.update(product.id, product)
        if update_success:
            print(
                f"[{self.__class__.__name__}.toggle_status] Successfully toggled status for product ID '{product_id}' to {new_status}."
            )
            return True
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Failed to update status for product ID '{product_id}'."
            )
            return False
