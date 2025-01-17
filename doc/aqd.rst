Aquadopp (currents)
*******************

Data will generally be processed using a series of run scripts that use command line arguments.  For AQD currents it's a 2 step process.

Instrument data to raw .cdf
===========================

First, in AquaPro, export data to text files using the default options.

Convert from text to a raw netCDF file with ``.cdf`` extension using runaqdhdr2cdf.py. This script
depends on two arguments, the global attribute file and extra configuration information :doc:`configuration files </config>`.

runaqdhdr2cdf.py
----------------

.. argparse::
   :ref: stglib.core.cmd.aqdhdr2cdf_parser
   :prog: runaqdhdr2cdf.py

Raw .cdf to CF-compliant .nc
============================

Convert the raw .cdf data into an CF-compliant netCDF file with .nc extension, optionally including :doc:`atmospheric correction </atmos>` of the pressure data.  Correcting pressure for atmospheric is a side-bar task- use the .ipynb examples to see what to do.

runaqdcdf2nc.py
---------------

.. argparse::
   :ref: stglib.core.cmd.aqdcdf2nc_parser
   :prog: runaqdcdf2nc.py
