import math

import numpy as np
import xarray as xr
from tqdm import tqdm

from ..aqd import aqdutils
from ..core import qaqc, utils


def cdf_to_nc(cdf_filename, atmpres=False):
    """
    Load a raw .cdf file and generate a processed .nc file
    """

    # Load raw .cdf data
    ds = aqdutils.load_cdf(cdf_filename, atmpres=atmpres)

    # Clip data to in/out water times or via good_ens
    ds = utils.clip_ds(ds)

    ds = utils.create_nominal_instrument_depth(ds)

    ds, T, T_orig = set_orientation(ds, ds["TransMatrix"].values)

    u, v, w = aqdutils.coord_transform(
        ds["VEL1"],
        ds["VEL2"],
        ds["VEL3"],
        ds["Heading"].values,
        ds["Pitch"].values,
        ds["Roll"].values,
        T,
        T_orig,
        ds.attrs["VECCoordinateSystem"],
    )

    ds["U"] = xr.DataArray(u, dims=("time", "sample"))
    ds["V"] = xr.DataArray(v, dims=("time", "sample"))
    ds["W"] = xr.DataArray(w, dims=("time", "sample"))

    ds = aqdutils.magvar_correct(ds)

    # Rename DataArrays for EPIC compliance
    ds = aqdutils.ds_rename(ds)

    # Drop unused variables
    ds = ds_drop(ds)

    # Add EPIC and CMG attributes
    ds = aqdutils.ds_add_attrs(ds, inst_type="VEC")

    ds = ds.rename({"Burst": "burst"})
    for v in ds.data_vars:
        # need to do this or else a "coordinates" attribute with value of "Burst" hangs around
        ds[v].encoding["coordinates"] = None

    ds["burst"].encoding["dtype"] = "i4"

    # Add start_time and stop_time attrs
    ds = utils.add_start_stop_time(ds)

    # Add history showing file used
    ds = utils.add_history(ds)

    ds = utils.add_standard_names(ds)

    if "prefix" in ds.attrs:
        nc_filename = ds.attrs["prefix"] + ds.attrs["filename"] + "-a.nc"
    else:
        nc_filename = ds.attrs["filename"] + "-a.nc"

    ds.to_netcdf(nc_filename, encoding={"time": {"dtype": "i4"}})
    utils.check_compliance(nc_filename, conventions=ds.attrs["Conventions"])

    print("Done writing netCDF file", nc_filename)

    return ds


def set_orientation(VEL, T):
    """
    Create z variable depending on instrument orientation
    Mostly taken from ../aqd/aqdutils.py
    """

    if "Pressure_ac" in VEL:
        presvar = "Pressure_ac"
    else:
        presvar = "Pressure"

    geopotential_datum_name = None

    if "NAVD88_ref" in VEL.attrs or "NAVD88_elevation_ref" in VEL.attrs:
        # if we have NAVD88 elevations of the bed, reference relative to the instrument height in NAVD88
        if "NAVD88_ref" in VEL.attrs:
            elev = VEL.attrs["NAVD88_ref"] + VEL.attrs["transducer_offset_from_bottom"]
        elif "NAVD88_elevation_ref" in VEL.attrs:
            elev = (
                VEL.attrs["NAVD88_elevation_ref"]
                + VEL.attrs["transducer_offset_from_bottom"]
            )
        long_name = "height relative to NAVD88"
        geopotential_datum_name = "NAVD88"
    elif "height_above_geopotential_datum" in VEL.attrs:
        elev = (
            VEL.attrs["height_above_geopotential_datum"]
            + VEL.attrs["transducer_offset_from_bottom"]
        )
        long_name = f"height relative to {VEL.attrs['geopotential_datum_name']}"
        geopotential_datum_name = VEL.attrs["geopotential_datum_name"]
    else:
        # if we don't have NAVD88 elevations, reference to sea-bed elevation
        elev = VEL.attrs["transducer_offset_from_bottom"]
        long_name = "height relative to sea bed"

    T_orig = T.copy()

    if VEL.attrs["orientation"] == "UP":
        print("User instructed that instrument was pointing UP")

        VEL["z"] = xr.DataArray(elev + [0.15], dims="z")
        VEL["depth"] = xr.DataArray(np.nanmean(VEL[presvar]) - [0.15], dims="depth")

    elif VEL.attrs["orientation"] == "DOWN":
        print("User instructed that instrument was pointing DOWN")
        T[1, :] = -T[1, :]
        T[2, :] = -T[2, :]

        VEL["z"] = xr.DataArray(elev - [0.15], dims="z")
        VEL["depth"] = xr.DataArray(np.nanmean(VEL[presvar]) + [0.15], dims="depth")

    VEL["z"].attrs["standard_name"] = "height"
    VEL["z"].attrs["units"] = "m"
    VEL["z"].attrs["positive"] = "up"
    VEL["z"].attrs["axis"] = "Z"
    VEL["z"].attrs["long_name"] = long_name
    if geopotential_datum_name:
        VEL["z"].attrs["geopotential_datum_name"] = geopotential_datum_name

    VEL["depth"].attrs["standard_name"] = "depth"
    VEL["depth"].attrs["units"] = "m"
    VEL["depth"].attrs["positive"] = "down"
    VEL["depth"].attrs["long_name"] = "depth below mean sea level"

    return VEL, T, T_orig


def ds_drop(ds):
    """
    Drop old DataArrays from Dataset that won't make it into the final .nc file
    """

    todrop = [
        "VEL1",
        "VEL2",
        "VEL3",
        "AMP1",
        "AMP2",
        "AMP3",
        "TransMatrix",
        "AnalogInput1",
        "AnalogInput2",
        "Depth",
        "Checksum",
    ]

    if ("AnalogInput1" in ds.attrs) and (ds.attrs["AnalogInput1"].lower() == "true"):
        todrop.remove("AnalogInput1")

    if ("AnalogInput2" in ds.attrs) and (ds.attrs["AnalogInput2"].lower() == "true"):
        todrop.remove("AnalogInput2")

    return ds.drop([t for t in todrop if t in ds.variables])
