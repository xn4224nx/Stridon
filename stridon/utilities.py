"""
STRIDON UTILITIES
=================

Universal function that are applicable in most areas.
"""

import socket
import json


def is_internet_up():
    """
    Ensure this system is connected to the internet. Otherwise halt execution.
    """
    try:
        socket.create_connection(("8.8.8.8", 53))
    except Exception as err:
        raise Exception(f"Could not connect due to '{err}'")


def read_json_url(url: str) -> dict:
    """
    Open a URL from an internet address and parse it as a dictionary.
    """
    pass


def read_json_file(file_path: str, ret_empty: bool = True) -> dict:
    """
    Open a JSON file on disk and return its contents as a python dictionary. If
    the parse fails or the item doesn't exist return an empty dictionary.
    """
    pass


def write_json_file(file_path: str, data: dict):
    """
    Save a dictionary in memory to disk as a pretty printed JSON file.
    """
    pass
