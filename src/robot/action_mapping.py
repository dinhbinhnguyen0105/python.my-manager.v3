# src/robot/action_mapping.py

from src.robot.actions.action_share_latest_product import share_latest_product
from src.robot.actions.action_discussion import discussion
from src.robot.actions.action_launch import launch_browser
from src.robot.actions.action_marketplace import marketplace
from src.robot.actions.action_list_on_marketplace import list_on_marketplace

ACTION_MAP = {
    "marketplace": marketplace,
    "launch_browser": launch_browser,
    "discussion": discussion,
    "list_on_marketplace": list_on_marketplace,
    "share_latest_product": share_latest_product,
}
