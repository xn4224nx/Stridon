import pytest
import stridon
import requests
from pathlib import Path

test_data_dir = "./stridon/tests/test_data"


def test_internet_connections():

    # Test the connection outside of the function to be tested
    try:
        respon = requests.get("https://www.google.com/").raise_for_status()
        connected = True
    except:
        connected = False

    # No ensure the function gets the same result
    try:
        stridon.utilities.is_internet_up()
        f_conn = True
    except:
        f_conn = False

    assert connected == f_conn


def test_reading_internet_jsons():
    assert stridon.utilities.read_json_url(
        "https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json"
    )[0] == {
        "name": "Adeel Solangi",
        "language": "Sindhi",
        "id": "V59OF92YF627HFY0",
        "bio": (
            "Donec lobortis eleifend condimentum. Cras dictum dolor lacinia "
            "lectus vehicula rutrum. Maecenas quis nisi nunc. Nam tristique "
            "feugiat est vitae mollis. Maecenas quis nisi nunc."
        ),
        "version": 6.1,
    }


def test_reading_bad_internet_jsons():
    with pytest.raises(Exception):
        stridon.utilities.read_json_url(
            "https://microsoftedge.github.io/Demos/json-dummy-data/missing-colon.json"
        )

    with pytest.raises(Exception):
        stridon.utilities.read_json_url(
            "https://microsoftedge.github.io/Demos/json-dummy-data/unterminated.json"
        )

    with pytest.raises(Exception):
        stridon.utilities.read_json_url(
            "https://microsoftedge.github.io/Demos/json-dummy-data/binary-data.json"
        )


def test_read_json_file():
    assert stridon.utilities.read_json_file(Path(test_data_dir, "example.JSON")) == {
        "first_name": "John",
        "last_name": "Smith",
        "is_alive": True,
        "age": 27,
        "address": {
            "street_address": "21 2nd Street",
            "city": "New York",
            "state": "NY",
            "postal_code": "10021-3100",
        },
        "phone_numbers": [
            {"type": "home", "number": "212 555-1234"},
            {"type": "office", "number": "646 555-4567"},
        ],
        "children": ["Catherine", "Thomas", "Trevor"],
        "spouse": None,
    }


def test_read_missing_json_file():
    assert stridon.utilities.read_json_file(Path(test_data_dir, "NO_SUCH_FILE")) == {}

    with pytest.raises(Exception):
        stridon.utilities.read_json_file(Path(test_data_dir, "NO_SUCH_FILE"), False)


def test_write_json_file():
    stridon.utilities.write_json_file(Path(test_data_dir, "TEMP_FILE.JSON"), {})

    with open(Path(test_data_dir, "TEMP_FILE.JSON"), "r") as file:
        assert file.readline().strip() == "{}"

    Path(test_data_dir, "TEMP_FILE.JSON").unlink(missing_ok=False)
