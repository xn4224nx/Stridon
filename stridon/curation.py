"""
STRIDON - A PYPI SCRAPER
========================

Download data from the Python Package Index. Mainly using the simple index:

    https://pypi.org/simple/

"""

import requests
import tarfile
from zipfile import ZipFile
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm


from . import utilities


class Curate:
    def __init__(self):
        """
        Access the simple PyPI site page here:

            https://pypi.org/simple/

        Then download a list of all the available package names.
        """
        utilities.is_internet_up()
        self.data_dir = "data"
        self.package_names_file = "package_names.json"
        pack_name_file = Path(self.data_dir, self.package_names_file)
        self.pack_index = utilities.read_json_file(pack_name_file)

        # If the package names can't be found download the simple webpage and
        # extract all the package names and create the files.
        if not self.pack_index:
            simp_page = requests.get("https://pypi.org/simple/").text

            for link in BeautifulSoup(simp_page, "html.parser").find_all("a"):
                self.pack_index[link.get("href").split("/")[-2]] = {}

            print(f"Package Names Downloaded:    {len(self.pack_index)}")

            # Recreate the data folder and save the names to disk
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)
            utilities.write_json_file(pack_name_file, self.pack_index)
            print(f"Package Names Saved to Disk: '{pack_name_file}'")

        else:
            print(f"Package Names Loaded:        {len(self.pack_index)}")

    def get_package_metadata(self, pack_nm: str) -> dict:
        """
        Download the package metadata and return the result as a dictionary
        using the url: https://pypi.python.org/pypi/<package-name>/json
        """
        return utilities.read_json_url(f"https://pypi.python.org/pypi/{pack_nm}/json")

    def get_download_link(self, pack_nm: str):
        """
        Access the PyPI and get the download link for a single package in the
        repository.
        """
        srcs_page = requests.get(f"https://pypi.org/simple/{pack_nm}").text

        # Find the links in the page that leads to a tarball
        tar_links = []
        for link in BeautifulSoup(srcs_page, "html.parser").find_all("a"):
            raw_link = link.get("href")

            if ".tar.gz" in raw_link:
                tar_links.append(raw_link)

        if tar_links:
            ful_lnk, sha_digest = tar_links[-1].rsplit("#", 1)
            self.pack_index[pack_nm]["src_link"] = ful_lnk
            self.pack_index[pack_nm]["src_hash"] = sha_digest

    def download_package_src(self, pack_nm: str, down_loc: str):
        """
        Find a package and download its source code to disk in the specified
        download directory.
        """
        if "src_link" not in self.pack_index[pack_nm]:
            raise Exception(f"Link for package {pack_nm} not found!")

        response = requests.get(self.pack_index[pack_nm]["src_link"], stream=True)

        with open(Path(down_loc, pack_nm + ".tar.gz"), "wb") as handle:
            for data in tqdm(response.iter_content(chunk_size=1024), unit="kB"):
                handle.write(data)

    def extract_package(self, in_pack_fp: str, out_pack_dir: str, pack_nm: str):
        """
        After a package has been downloaded to disk, open the tarball and
        extract all the python script files and repackage then into a zip
        without nesting. The original filenames will be preserved within reason.
        """
        with tarfile.open(in_pack_fp, "r") as ts_fp:
            with tarfile.open(Path(out_pack_dir, pack_nm + ".tar.xz"), "w:xz") as td_fp:

                # Get the names of files in the archive smaller than 50MB and
                # greater than zero that have the file extension .py and add
                # these files to the new tarball.
                for t_subfile in ts_fp.getmembers():
                    if (
                        t_subfile.name.endswith(".py")
                        and t_subfile.isfile()
                        and t_subfile.size < 50 * 10 ^ 6
                        and t_subfile.size > 0
                    ):
                        td_fp.addfile(t_subfile, ts_fp.extractfile(t_subfile.name))

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
        pass

    def all_packages(self):
        """
        Download all packages and metadata from the PyPI.
        """
        pass
