# src/services/product_service.py
import uuid
import glob
import os
import shutil
from typing import Optional, List
from src.services.base_service import BaseService
from src.models.product_model import (
    RealEstateProductModel,
    RealEstateTemplateModel,
    MiscProductModel,
)
from src.my_types import RealEstateProductType, RealEstateTemplateType, MiscProductType
from src.my_constants import RE_TRANSACTION


class RealEstateProductService(BaseService):
    DATA_TYPE = RealEstateProductType

    def __init__(self, model: RealEstateProductModel):
        if not isinstance(model, RealEstateProductModel):
            raise TypeError(
                "model must be an instance of RealEstateProductModel or its subclass."
            )
        super().__init__(model)

    def create(
        self,
        image_dir_container: str,
        image_paths: List[str],
        payload: RealEstateProductType,
    ) -> bool:
        product_dir = os.path.abspath(os.path.join(image_dir_container, payload.pid))
        if not os.path.exists(product_dir):
            os.makedirs(product_dir)

        for idx, image_path in enumerate(image_paths):
            if os.path.isfile(image_path):
                ext = os.path.splitext(image_path)[1]
                base_name = getattr(payload, "uid", None) or getattr(
                    payload, "pid", "img"
                )
                new_name = f"{base_name}_{idx+1}{ext}"
                dest_path = os.path.join(product_dir, new_name)
                shutil.copy(image_path, dest_path)
        payload.image_dir = product_dir
        return super().create(payload)

    def read(self, record_id: int) -> Optional[RealEstateProductType]:
        return super().read(record_id)

    def read_all(self) -> List[RealEstateProductType]:
        return super().read_all()

    def update(self, record_id: int, payload: RealEstateProductType) -> bool:
        return super().update(record_id, payload)

    def delete(self, record_id: int) -> bool:
        product_data = self.read(record_id)
        if product_data and getattr(product_data, "image_dir", None):
            image_dir = product_data.image_dir
            if os.path.isdir(image_dir):
                try:
                    shutil.rmtree(image_dir)
                except Exception as e:
                    print(
                        f"[{self.__class__.__name__}.delete] Warning: Failed to remove image directory '{image_dir}': {e}"
                    )
        return super().delete(record_id)

    def delete_multiple(self, record_ids: List[int]):
        return super().delete_multiple(record_ids)

    def import_data(self, payload: List[RealEstateProductType]):
        return super().import_data(payload)

    def find_by_pid(self, pid: str) -> Optional[RealEstateProductType]:
        return self._find_by_model_index(find_method_name="find_row_by_pid", value=pid)

    def toggle_status(self, record_id: int) -> bool:
        product = self.read(record_id)
        if product is None:
            print(
                f"[{self.__class__.__name__}.toggle_status] Product with record_id '{record_id}' not found."
            )
            return False

        current_status = product.status
        if current_status == 0:
            new_status = 1
        elif current_status == 1:
            new_status = 0
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Unexpected status value for record_id '{record_id}': {current_status}. Cannot toggle."
            )
            return False

        product.status = new_status
        update_success = self.update(record_id, product)
        if update_success:
            print(
                f"[{self.__class__.__name__}.toggle_status] Successfully toggled status for record_id '{record_id}' to {new_status}."
            )
            return True
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Failed to update status for record_id '{record_id}'."
            )
            return False

    def initialize_new_pid(self, transaction_type: str) -> str:
        """
        Initializes and generates a new unique product identifier (PID).

        Returns:
            str: The newly generated unique product identifier.
        """
        try:
            if not transaction_type in RE_TRANSACTION.keys():
                raise KeyError()
            else:
                while True:
                    uuid_str = str(uuid.uuid4())
                    pid = uuid_str.replace("-", "")[:8]
                    if transaction_type == "sell":
                        pid = "S." + pid
                    elif transaction_type == "rent":
                        pid = "R." + pid
                    elif transaction_type == "assignment":
                        pid = "A." + pid
                    pid = "RE." + pid
                    if not self.find_by_pid(pid):
                        return pid
        except KeyError:
            raise KeyError(
                f"[{__class__.__name__}.initialize_new_pid] Error: Invalid transaction type ({transaction_type})."
            )

    def get_images_by_id(self, record_id: int) -> List[str]:
        """
        Retrieves image file paths from a directory associated with a product ID.

        This method is designed to locate a specific directory linked to the given
        `record_id` (e.g., a product or item ID) and then collect all image
        file paths found within that directory.

        Args:
            record_id (int): The unique identifier of the product or item for which
                             images are to be retrieved.

        Returns:
            List[str]: A list of absolute file paths to the images found in the
                       corresponding directory. Returns an empty list if no images
                       are found or if the directory does not exist.
        """
        product = self.read(record_id)
        if not product or not getattr(product, "image_dir", None):
            return []
        return self.get_images_by_path(product.image_dir)

    def get_images_by_path(self, path: str) -> List[str]:
        """
        Retrieves image file paths from a specified directory.

        This method scans the directory provided by `path` and collects all
        image file paths found directly within it. It does not recurse into
        subdirectories.

        Args:
            path (str): The absolute or relative path to the directory from which
                        to retrieve image files.

        Returns:
            List[str]: A list of absolute file paths to the images found in the
                       specified directory. Returns an empty list if no images
                       are found or if the directory does not exist.
        """
        if not path or not os.path.isdir(path):
            return []
        image_extensions = (
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.bmp",
            "*.gif",
            "*.webp",
            "*.PNG",
            "*.JPG",
            "*.JPEG",
        )
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(path, ext)))
        return sorted(image_files)


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

    def get_random(self, part: str, transaction_type: str, category: str) -> str:
        query = """
            SELECT value FROM real_estate_template
            WHERE (? = '' OR part = ?)
            AND (? = '' OR transaction_type = ?)
            AND (? = '' OR category = ?)
            ORDER BY RANDOM() LIMIT 1
        """
        params = (part, part, transaction_type, transaction_type, category, category)
        cursor = self.model.db.connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row[0] if row else ""


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

    def toggle_status(self, record_id: int) -> bool:
        product = self.read(record_id)
        if product is None:
            print(
                f"[{self.__class__.__name__}.toggle_status] Product with record_id '{record_id}' not found."
            )
            return False

        current_status = product.status
        if current_status == 0:
            new_status = 1
        elif current_status == 1:
            new_status = 0
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Unexpected status value for product ID '{record_id}': {current_status}. Cannot toggle."
            )
            return False

        product.status = new_status
        update_success = self.update(product.id, product)
        if update_success:
            print(
                f"[{self.__class__.__name__}.toggle_status] Successfully toggled status for product ID '{record_id}' to {new_status}."
            )
            return True
        else:
            print(
                f"[{self.__class__.__name__}.toggle_status] Failed to update status for product ID '{record_id}'."
            )
            return False
