import hashlib
import os
import pathlib
import tarfile
import urllib.request


try:
    from google.colab import drive
    drive.mount("/gdrive")
    core_path = "/gdrive/MyDrive/L&D/Own projects/Space science with Python/AsteroidSpectra/asteroid_taxonomy"
except ModuleNotFoundError:
    core_path = ""


# Define function to compute the sha256 value of the downloaded files
def comp_sha256(file_name):
    """
    Compute the SHA256 hash of a file.
    Parameters
    ----------
    file_name : str
        Absolute or relative pathname of the file that shall be parsed.
    Returns
    -------
    sha256_res : str
        Resulting SHA256 hash.
    """
    # Set the SHA256 hashing
    hash_sha256 = hashlib.sha256()

    # Open the file in binary mode (read-only) and parse it in 65,536 byte chunks (in case of
    # large files, the loading will not exceed the usable RAM)
    with pathlib.Path(file_name).open(mode="rb") as f_temp:
        for _seq in iter(lambda: f_temp.read(65536), b""):
            hash_sha256.update(_seq)

    # Digest the SHA256 result
    sha256_res = hash_sha256.hexdigest()

    return sha256_res


pathlib.Path(os.path.join(core_path,"data/lvl0/")).mkdir(parents=True, exist_ok=True)

# Set a dictionary that contains the taxonomy classification data and corresponding sha256 values
files_to_dl = \
    {'file1': {'url': 'http://smass.mit.edu/data/smass/Bus.Taxonomy.txt',
               'sha256': '0ce970a6972dd7c49d512848b9736d00b621c9d6395a035bd1b4f3780d4b56c6'},
     'file2': {'url': 'http://smass.mit.edu/data/smass/smass2data.tar.gz',
               'sha256': 'dacf575eb1403c08bdfbffcd5dbfe12503a588e09b04ed19cc4572584a57fa97'}}

for dl_key in files_to_dl:

    split = urllib.parse.urlsplit(files_to_dl[dl_key]["url"])
    filename = pathlib.Path(os.path.join(core_path,"data/lvl0/", split.path.split("/")[-1]))

    if not filename.is_file():
        print(f"Downloading now: {files_to_dl[dl_key]['url']}")

        # Download file and retrieve the created filepath
        download_file_path, _ = urllib.request.urlretrieve(url=files_to_dl[dl_key]['url'], filename=filename)

        # Compute and compare the hash value
        tax_hash = comp_sha256(download_file_path)
        assert tax_hash == files_to_dl[dl_key]["sha256"]

tar = tarfile.open(os.path.join(core_path,"data/lvl0/smass2data.tar.gz"))
tar.extractall(path=os.path.join(core_path,"data/lvl0/"))
tar.close()
