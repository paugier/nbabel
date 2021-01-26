from pathlib import Path
import sys
from shutil import copy
import gzip

import numpy as np
import h5py

from getwatt import getwatt

path_in = Path(sys.argv[1])

assert path_in.exists()

path_out = path_in.with_name(
    path_in.stem.split("_incomplete")[0] + path_in.suffix
)

print(path_out)

if path_out.exists():
    print(f"file {path_out} already exists, nothing to do")
    sys.exit(1)

with h5py.File(path_in, "r") as file:
    node_shortname = file.attrs["node_shortname"]
    timestamp_before = file.attrs["timestamp_before"]
    timestamp_end = file.attrs["timestamp_end"]


try:
    conso = np.array(
        getwatt(node_shortname, timestamp_before, timestamp_end)
    )
except gzip.BadGzipFile:
    print(
        "Error gzip.BadGzipFile. "
        "Power data will need to be upload later."
    )
    sys.exit(1)

copy(path_in, path_out)

times = conso[:, 0]
watts = conso[:, 1]

with h5py.File(path_out, "a") as file:

    file.create_dataset(
        "times", data=times, compression="gzip", compression_opts=9
    )
    file.create_dataset(
        "watts", data=watts, compression="gzip", compression_opts=9
    )