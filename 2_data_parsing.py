# Import standard libraries
import glob
import os
import pathlib
import re

# Import installed libraries
import pandas as pd

try:
  from google.colab import drive
  drive.mount("/gdrive")
  core_path = "/gdrive/MyDrive/L&D/Own projects/Space science with Python/AsteroidSpectra/asteroid_taxonomy"
except ModuleNotFoundError:
  core_path = ""

# Get a sorted list of all spectra files (consider only the spfit files that have been explained in
# the references)
spectra_filepaths = sorted(glob.glob(os.path.join(core_path, "data/lvl0/", "smass2/*spfit*")))

# Separate the filepaths into designation and non-designation files
des_file_paths = spectra_filepaths[:-8]
non_file_paths = spectra_filepaths[-8:]

# Convert the arrays to dataframes
des_file_paths_df = pd.DataFrame(des_file_paths, columns=["FilePath"])
non_file_paths_df = pd.DataFrame(non_file_paths, columns=["FilePath"])

# Add now the designation / "non"-designation number
des_file_paths_df.loc[:, "DesNr"] = des_file_paths_df["FilePath"] \
                                        .apply(lambda x: int(re.search(r'smass2/a(.*).spfit',
                                                                       x).group(1)))
non_file_paths_df.loc[:, "DesNr"] = non_file_paths_df["FilePath"] \
                                        .apply(lambda x: re.search(r'smass2/au(.*).spfit',
                                                                   x).group(1))

print(des_file_paths_df.head(5))
print(non_file_paths_df.head(5))

# Read the classification file
asteroid_class_df = pd.read_csv(os.path.join(core_path, "data/lvl0/", "Bus.Taxonomy.txt"),
                                skiprows=21,
                                sep="\t",
                                names=["Name",
                                       "Tholen_Class",
                                       "Bus_Class",
                                       "unknown1",
                                       "unknown2"
                                      ]
                               )

# Remove white spaces
asteroid_class_df.loc[:, "Name"] = asteroid_class_df["Name"].apply(lambda x: x.strip()).copy()

# Separate between designated and non-designated asteroid classes
des_ast_class_df = asteroid_class_df[:1403].copy()
non_ast_class_df = asteroid_class_df[1403:].copy()

print(des_ast_class_df.head(5))
print(non_ast_class_df.head(5))

# Now split the designated names and get the designation number (to link with the spfit files)
des_ast_class_df.loc[:, "DesNr"] = des_ast_class_df["Name"].apply(lambda x: int(x.split(" ")[0]))

# Merge with the spectra file paths
des_ast_class_join_df = des_ast_class_df.merge(des_file_paths_df, on="DesNr")

# For the non designated names, one needs to remove the white space between number and name and
# compare with the file paths
non_ast_class_df.loc[:, "DesNr"] = non_ast_class_df["Name"].apply(lambda x: x.replace(" ", ""))

# Merge with the spectra file paths
non_ast_class_join_df = non_ast_class_df.merge(non_file_paths_df, on="DesNr")

print(des_ast_class_join_df.head(5))
print(non_ast_class_join_df.head(5))

# Merge now both datasets
asteroids_df = pd.concat([des_ast_class_join_df, non_ast_class_join_df], axis=0)

# Reset the index
asteroids_df.reset_index(drop=True, inplace=True)

# Remove the tholen class and both unknown columns
asteroids_df.drop(columns=["Tholen_Class", "unknown1", "unknown2"], inplace=True)

# Drop now all rows that do not contains a Bus Class
asteroids_df.dropna(subset=["Bus_Class"], inplace=True)

print(asteroids_df.head(5))

# Read and store the spectra
asteroids_df.loc[:, "SpectrumDF"] = \
    asteroids_df["FilePath"].apply(lambda x: pd.read_csv(x, sep="\t",
                                                         names=["Wavelength_in_microm",
                                                                "Reflectance_norm550nm"]
                                                        )
                                  )
# Reset the index
asteroids_df.reset_index(drop=True, inplace=True)

# Convert the Designation Number to string
asteroids_df.loc[:, "DesNr"] = asteroids_df["DesNr"].astype(str)

print(asteroids_df.head(5))

# Create (if applicable) the level 1 directory
pathlib.Path(os.path.join(core_path, "data/lvl1")).mkdir(parents=True, exist_ok=True)

# Save the dataframe as a pickle file
asteroids_df.to_pickle(os.path.join(core_path, "data/lvl1/", "asteroids_merged.pkl"), protocol=4)