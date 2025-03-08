import pytest
import requests
import tarfile
from pathlib import Path

from stridon import Curate

test_data_dir = "./stridon/tests/test_data"


def test_initation():
    test = Curate()

    assert "numpy" in test.pack_index
    assert "pandas" in test.pack_index
    assert test.pack_index["numpy"] == {}

    assert "numpy" in test.pack_popularity
    assert "pandas" in test.pack_popularity
    assert "boto3" in test.pack_popularity

    # Check the created files exist
    assert Path(test.data_dir, test.package_names_file).is_file()
    assert Path(test.data_dir, test.popular_packages).is_file()


def test_get_download_link():
    test = Curate()
    test.get_download_link("numpy")

    assert "src_link" in test.pack_index["numpy"]
    assert test.pack_index["numpy"]["src_link"].startswith("https")
    assert test.pack_index["numpy"]["src_hash"].startswith("sha256=")


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
    test.get_download_link("black")
    test.download_package_src("black", test_data_dir)
    downloaded_file = Path(test_data_dir, "black.tar.gz")

    assert downloaded_file.is_file()
    assert tarfile.is_tarfile(downloaded_file)

    downloaded_file.unlink(missing_ok=True)


def test_download_package_src_no_link():
    test = Curate()
    with pytest.raises(Exception):
        test.download_package_src("pandas", test_data_dir)

    Path(test_data_dir, "pandas.tar.gz").unlink(missing_ok=True)


def test_extract_package():
    test = Curate()
    test.extract_package(
        Path(test_data_dir, "example-module.tar.gz"), test_data_dir, "module-name"
    )
    extracted_file = Path(test_data_dir, "module-name.tar.xz")

    assert extracted_file.is_file()
    assert tarfile.is_tarfile(extracted_file)

    collected_file_names = []
    with tarfile.open(extracted_file, "r") as test_tar:
        for t_file in test_tar.getmembers():
            assert t_file.isfile()
            assert t_file.name.endswith(".py")
            collected_file_names.append(t_file.name)

    assert len(collected_file_names) == 64

    extracted_file.unlink(missing_ok=True)


def test_extract_package_no_file():
    test = Curate()
    with pytest.raises(Exception):
        test.extract_package(
            Path(test_data_dir, "no_such_package.tar.gz"), test_data_dir, "module-name"
        )
