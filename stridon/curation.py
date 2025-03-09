"""
STRIDON - A PYPI SCRAPER
========================

Download data from the Python Package Index. Mainly using the simple index:

    https://pypi.org/simple/

Avoid popular packages within the top 150,000 downloaded weekly.
"""

import requests
import tarfile
from zipfile import ZipFile
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import shutil
import time
import random

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
        self.popular_packages = "popular_packages.json"

        pack_name_file = Path(self.data_dir, self.package_names_file)
        popular_name_file = Path(self.data_dir, self.popular_packages)

        self.pack_index = utilities.read_json_file(pack_name_file)
        self.pack_popularity = set(utilities.read_json_file(popular_name_file))

        # If the package names can't be found download the simple webpage and
        # extract all the package names and create the files.
        if not self.pack_index:
            simp_page = requests.get("https://pypi.org/simple/").text

            for link in BeautifulSoup(simp_page, "html.parser").find_all("a"):
                self.pack_index[link.get("href").split("/")[-2]] = {}

            print(f"Package Names Downloaded:             {len(self.pack_index)}")

            # Recreate the data folder and save the names to disk
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)
            utilities.write_json_file(pack_name_file, self.pack_index)
            print(f"Package Names Saved to Disk:          '{pack_name_file}'")

        else:
            print(f"Package Names Loaded:                 {len(self.pack_index)}")

        # Using a third party index extract a list of the most downloaded packages from PyPI
        if not self.pack_popularity:
            raw_popularity = utilities.read_json_url(
                "https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json"
            )

            # Extract only the names of the top 15,000
            for pack_details in raw_popularity["rows"]:
                self.pack_popularity.add(pack_details["project"])
            print(f"Popular Packages Names Downloaded:    {len(self.pack_popularity)}")

            # Recreate the data folder and save the names to disk
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)
            utilities.write_json_file(popular_name_file, list(self.pack_popularity))
            print(f"Popular Packages Names Saved to Disk: '{popular_name_file}'")

        else:
            print(f"Package Packages Names Loaded:        {len(self.pack_popularity)}")

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
        pack_down_path = Path(down_loc, pack_nm + ".tar.gz")

        if "src_link" not in self.pack_index[pack_nm]:
            raise Exception(f"Link for package {pack_nm} not found!")

        response = requests.get(self.pack_index[pack_nm]["src_link"], stream=True)

        with open(pack_down_path, "wb") as handle:
            for data in tqdm(response.iter_content(chunk_size=1024), unit="kB"):
                handle.write(data)

        self.pack_index[pack_nm]["tar_path"] = str(pack_down_path)

    def extract_setup_files(self, pack_nm: str, extract_dir: str) -> bool:
        """
        Open a downloaded tar ball and extract all the `setup.py` files and
        extract them to a specified folder. Rename the extracted file with a
        uuid and the original name of the tarball.
        """
        with tarfile.open(self.pack_index[pack_nm]["tar_path"], "r") as ts_fp:
            extract_cnt = 0

            # Iterate over each of the files in the tarball and extract setup.py
            for t_subfile in ts_fp.getmembers():
                print(t_subfile.name)

                if (
                    Path(t_subfile.name).name == "setup.py"
                    and t_subfile.isfile()
                    and t_subfile.size > 0
                ):
                    out_file = Path(extract_dir, f"{pack_nm}-{extract_cnt}.py")

                    # Extract the file
                    with open(out_file, "wb") as out_fp:
                        shutil.copyfileobj(ts_fp.extractfile(t_subfile), out_fp)

                    extract_cnt += 1

        # Confirm if any setup files were found
        return extract_cnt > 0

    def rnd_uncommon_setups(self, extract_dir: str, down_dir: str, num_pack: int = 100):
        """
        Access the repository and download uncommon packages and extract their
        setup files to a specified directory `extract_dir`, and save the
        raw data in `down_dir`.
        """
        down_packs = 0
        print("\nDOWNLOADING RANDOM PACKAGES\n===========================\n")

        unc_packs = [x for x in self.pack_index if x not in self.pack_popularity]
        print(f"Uncommon Packages Found: {len(unc_packs)}")

        # Loop until the required number are downloaded
        while down_packs < num_pack:
            pack_name = random.choice(unc_packs)
            print(f"\n{down_packs+1:6} {pack_name}")

            # Check this has not already been picked
            if "downloaded" not in self.pack_index[pack_name]:
                try:
                    self.get_download_link(pack_name)

                    if "src_link" not in self.pack_index[pack_name]:
                        print(f"\tTarball download link found!")
                        self.download_package_src(pack_name, down_dir)

                        if self.extract_setup_files(pack_name, extract_dir):
                            print(f"\tSetup files found!")
                            down_packs += 1
                    else:
                        print(f"\tNo download link found!")

                except Exception as err:
                    print(f"\tError: {err}")

            else:
                print(f"\tAlready downloaded.")

            # Make a record of the downloaded packages
            unc_packs.remove(pack_name)
            self.pack_index[pack_name]["downloaded"] = True

    def all_metadata(self):
        """
        Download all package metadata from the PyPI repository and save it to
        disk.
        """
        print("\nDOWNLOADING METADATA\n====================\n")

        for pack_idx, pack_name in enumerate(self.pack_index):
            print(f"\n{pack_idx+1:6}: Downloading Link For {pack_name}")

            if "src_link" not in self.pack_index[pack_name]:
                self.get_download_link(pack_name)

                # Check something got downloaded
                if "src_link" in self.pack_index[pack_name]:
                    print(f"\tURL: {self.pack_index[pack_name]["src_link"]}")
                else:
                    print(f"\tNo Tarballs found!")

            else:
                print(f"\tLink already exists.")

            # Save the updated index to file
            if (pack_idx + 1) % 10 == 0:
                print("\tSaved data to disk.")
                utilities.write_json_file(
                    Path(self.data_dir, self.package_names_file), self.pack_index
                )

            # Wait to ensure the api is not overwelmed
            time.sleep(2)

        utilities.write_json_file(
            Path(self.data_dir, self.package_names_file), self.pack_index
        )

    def all_packages(self, save_direct: str):
        """
        Download all packages from the PyPI.
        """
        for pack_idx, pack_name in pack_idx, pack_name in enumerate(self.pack_index):
            if "src_link" in self.pack_index[pack_name]:
                self.download_package_src(pack_name, save_direct)

                # Wait to ensure the api is not overwelmed
                time.sleep(2)
