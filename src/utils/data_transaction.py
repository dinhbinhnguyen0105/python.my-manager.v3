# src/utils/data_transaction.py
import json
from typing import Union, Optional, Dict, Type, List, TypeAlias, Any
from dataclasses import fields, asdict
from src.my_types import UserType, RealEstateProductType


MyDataInstanceList: TypeAlias = List[Union[UserType, RealEstateProductType]]


def import_from_json_file(
    file_path: str,
    data_type: Union[
        Type[UserType],
        Type[RealEstateProductType],
    ],
) -> Optional[MyDataInstanceList]:
    """
    Reads a JSON file (expected to contain a list of dictionaries) and
    converts each dictionary into an instance of the specified dataclass type.

    Args:
        file_path (str): The path to the JSON file.
        data_type (Union[Type[UserType], Type[RealEstateProductType]]):
            The dataclass type to convert the JSON dictionaries into.

    Returns:
        Optional[MyDataInstanceList]: A list of dataclass instances
        if successful, otherwise None.
    """
    raw_data_list = read_json_file(file_path)
    if raw_data_list is None:  # read_json_file now returns None on error
        return None

    parsed_instances: MyDataInstanceList = []

    dataclass_field_types = {f.name: f.type for f in fields(data_type)}

    for item_dict in raw_data_list:
        instance_data: Dict[str, Any] = {}

        for field_name, field_type in dataclass_field_types.items():
            value = item_dict.get(field_name)

            actual_type = field_type
            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                non_none_types = [t for t in field_type.__args__ if t is not type(None)]
                if len(non_none_types) == 1:
                    actual_type = non_none_types[0]

            if value is not None:
                if actual_type is int:
                    try:
                        instance_data[field_name] = int(value)
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Could not convert '{value}' to int for field '{field_name}'. Setting to None."
                        )
                        instance_data[field_name] = None
                elif actual_type is float:
                    try:
                        instance_data[field_name] = float(value)
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Could not convert '{value}' to float for field '{field_name}'. Setting to None."
                        )
                        instance_data[field_name] = None
                elif actual_type is str:
                    instance_data[field_name] = str(value)
                else:
                    instance_data[field_name] = value
            else:
                instance_data[field_name] = None

        try:
            instance = data_type(**instance_data)
            parsed_instances.append(instance)
        except TypeError as e:
            print(
                f"Error: Could not create instance of {data_type.__name__} from data: {item_dict}. Details: {e}"
            )
            return None
        except Exception as e:
            print(f"Unexpected error while creating instance: {e}")
            return None
    return parsed_instances


def read_json_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Reads a JSON file and returns its content as a list of dictionaries.
    Returns None on error (FileNotFoundError, JSONDecodeError, or other errors).
    """
    try:
        with open(file_path, mode="r", encoding="utf8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(
                    f"Error: JSON file '{file_path}' does not contain a top-level list."
                )
                return None
            for item in data:
                if not isinstance(item, dict):
                    print(
                        f"Error: JSON file '{file_path}' contains non-dictionary items in the list."
                    )
                    return None
            return data
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON syntax in '{file_path}'. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
        return None


# --- New export function ---
def export_to_json_file(data_list: MyDataInstanceList, file_path: str) -> bool:
    """
    Exports a list of dataclass instances (UserType or RealEstateProductType)
    to a JSON file.

    Args:
        data_list (MyDataInstanceList): The list of dataclass instances to export.
        file_path (str): The path to the destination JSON file.

    Returns:
        bool: True if export was successful, False on error.
    """
    if not data_list:
        print("Warning: Data list is empty. Nothing to export.")
        try:
            with open(file_path, mode="w", encoding="utf8") as f:
                json.dump([], f, indent=4)  # Write an empty array
            return True
        except IOError as e:
            print(f"Error: Could not write JSON file '{file_path}'. Details: {e}")
            return False

    export_data = []
    for item in data_list:
        try:
            # asdict() converts a dataclass instance to a dictionary
            export_data.append(asdict(item))
        except TypeError as e:
            print(
                f"Error: Could not convert instance of {type(item).__name__} to dictionary: {e}"
            )
            return False
        except Exception as e:
            print(f"Unexpected error converting instance to dict: {e}")
            return False

    try:
        with open(file_path, mode="w", encoding="utf8") as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error: Could not write JSON file '{file_path}'. Details: {e}")
        return False
    except Exception as e:
        print(
            f"An unexpected error occurred while exporting JSON file '{file_path}': {e}"
        )
        return False
