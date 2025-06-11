# src/robot/action_mapping.py

from src.robot.actions.action_share_latest_product import share_latest_product
from src.robot.actions.action_discussion import discussion
from src.robot.actions.action_launch import launch_browser
from src.robot.actions.action_marketplace import marketplace

ACTION_MAP = {
    "launch_browser": launch_browser,
    "marketplace": marketplace,
    "discussion": discussion,
    "share_latest_product": share_latest_product,
}
