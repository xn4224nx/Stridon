"""
STRIDON - A PYPI SCRAPER
========================

Download data from the Python Package Index. Mainly using the simple index:

    https://pypi.org/simple/

"""


class Curate:
    def __init__(self):
        """
        Access the simple PyPI site page here:

            https://pypi.org/simple/

        Then download a list of all the available package names.
        """
        pass

    def get_package_metadata(self, pack_nm: str) -> dict:
        """
        Download the package metadata and return the result as a dictionary
        using the url: https://pypi.python.org/pypi/<package-name>/json
        """
        pass

    def get_download_link(self, pack_nm: str):
        """
        Access the PyPI and get the download link for a single package in the
        repository.
        """
        pass

    def download_package_src(self, pack_nm: str, down_loc: str):
        """
        Find a package and download its source code to disk in the specified
        download directory.
        """
        pass

    def extract_package(self, pack_fp: str):
        """
        After a package has been downloaded to disk, open the tarball and
        extract all the python script files and repackage then into a zip
        without nesting. The original filenames will be preserved within reason.
        """
        pass

    def rnd_packages(self, num_pack: int = 100):
        """
        Access the repository and download the entirety of a certain specified
        number of packages, both metadata and source files.
        """
        pass

    def all_metadata(self):
        """
        Download all package metadata from the PyPI repository and save it to
        disk.
        """

    def all_packages(self):
        """
        Download all packages and metadata from the PyPI.
        """
        pass
