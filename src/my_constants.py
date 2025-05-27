# src/my_constants.py
CONNECTION_DB_USER = "user_connection"
CONNECTION_DB_PRODUCT = "product_connection"
CONNECTION_DB_SETTING = "setting_connection"

PATH_DB_USER = "./src/repositories/db/db_user.db"
PATH_DB_PRODUCT = "./src/repositories/db/db_product.db"
PATH_DB_SETTING = "./src/repositories/db/db_setting.db"

TABLE_USER = "user"
TABLE_USER_LISTED_PRODUCT = "listed_products"
TABLE_USER_ACTION = "user_actions"
TABLE_SETTING_USER_DATA_DIR = "user_data_dir"
TABLE_SETTING_PROXY = "proxy"
TABLE_REAL_ESTATE_PRODUCT = "real_estate_product"
TABLE_MISC_PRODUCT = "misc"
TABLE_REAL_ESTATE_TEMPLATE = "real_estate_template"


RE_TRANSACTION = {"sell": "bán", "rent": "cho thuê", "assignment": "sang nhượng"}
RE_AVAILABILTY = {"available": "khả dụng", "not_available": "không khả dụng"}
RE_CATEGORY = {
    "apartment": "căn hộ/chung cư",
    "house": "nhà phố",
    "shop_house": "nhà mặt tiền",
    "land": "đất nền",
    "workshop": "kho/bãi",
}
RE_PROVINCE = {
    "lam_dong": "lâm đồng",
}
RE_DISTRICT = {"da_lat": "đà lạt"}
RE_WARD = {}
