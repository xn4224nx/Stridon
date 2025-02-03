import pytest
import requests
from pathlib import Path
from stridon import Curate

test_data_dir = "./stridon/tests/test_data"


def test_initation():
    test = Curate()

    assert "numpy" in test.pack_records
    assert "pandas" in test.pack_records
    assert test.pack_records["numpy"] == {}


def test_get_download_link():
    test = Curate()
    test.get_download_link("numpy")

    assert "src_link" in test.pack_records["numpy"]
    assert test.pack_records["numpy"]["src_link"].startswith("https")
    assert len(test.pack_records["numpy"]["src_sha256"]) == 64


def test_get_package_metadata():
    test = Curate()
    result = test.get_package_metadata("numpy")

    assert isinstance(result, dict)
    assert "info" in result
    assert "last_serial" in result
    assert "releases" in result
    assert "urls" in result
    assert "vulnerabilities" in result


def test_download_package_src():
    test = Curate()
    test.download_package_src("black", test_data_dir)
    downloaded_file = Path(test_data_dir, "black.tar.gz")

    assert downloaded_file.is_file()

    downloaded_file.unlink(missing_ok=True)


def test_extract_package():
    test = Curate()
    file_path = Path(test_data_dir, "example-module.tar.gz")
    test.extract_package(str(file_path))
    extracted_file = Path(test_data_dir, "example-module.zip")

    assert extracted_file.is_file()

    extracted_file.unlink(missing_ok=True)
