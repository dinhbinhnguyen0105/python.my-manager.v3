# src/database/user_database.py
from PyQt6.QtSql import QSqlDatabase, QSqlQuery

from src.my_contants import (
    CONNE
)
from src.database.sql_commands import (
    CREATE_USER_TABLE,
    CREATE_USER_LISTED_PRODUCT_TABLE,
    CREATE_USER_ACTION_TABLE,
)

def initialize_user_database():
    if QSqlDatabase.contains()