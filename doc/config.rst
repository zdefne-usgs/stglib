Configuration files
*******************

There are two required configuration files for processing data: the global attributes file, which describes attributes that apply to the mooring, and the instrument configuration file, which describes attributes that apply to an instrument on a mooring. Contents of both files will be included as attributes in both the xarray Dataset and the netCDF files.

Transitioning from EPIC to CF Conventions
=========================================

Historically, data have been released according to NOAA PMEL/EPIC conventions. Today, `CF Conventions <http://cfconventions.org>`_ are used much more frequently, and stglib supports only CF Conventions. Specifying conventions is done via ``Conventions`` keyword in either the global attributes file or the instrument configuration file.

Setting CF in global attributes
-------------------------------

::

  Conventions; CF-1.8

Setting CF in the instrument configuration file
-----------------------------------------------

::

  Conventions: 'CF-1.8'

Specifying CF-1.8 or a later release of the standard will enable straight-to-CF processing.

Global attributes configuration file
====================================

This file describes attributes that apply to the mooring, and uses a peculiar formatting as shown in the example below.

.. literalinclude:: ../examples/glob_att1076a.txt
   :linenos:

Instrument configuration file
=============================

This file is instrument-specific and is YAML formatted. A few examples are given below.

Options common to most (all?) instrument config files:

- ``Conventions``: version of the CF Conventions, ``'CF-1.8'`` presently
- ``basefile``: the input filename without extension
- ``filename``: output filename, to which ``-raw.cdf``, ``-a.nc``, etc. will be appended
- ``ClockError``: number, in seconds, negative is slow. Applies a simple offset for times. Useful if the instrument was deployed in an incorrect time zone.
- ``ClockDrift``: number, in seconds, negative is slow. Linearly interpolates times for when the instrument clock has drifted.
- ``initial_instrument_height``: elevation of instrument in meters
- ``initial_instrument_height_note``
- ``P_1ac_note``: a note on the atmospheric pressure source used
- ``zeroed_pressure``: a note detailing whether the pressure sensor was zeroed before deployment, and other pertinent details such as date and time of zeroing.
- ``good_dates``: a list of dates to clip data by instead of the default ``Deployment_date`` and ``Recovery_date``. Example: ``good_dates: ['2021-01-22 18:32', '2021-04-13 19:27'] # first burst looked suspect``. Multiple date ranges can also be used. Example: ``good_dates: ['2021-01-22 18:32', '2021-02-28 23:59', '2021-04-01 00:00', '2021-04-13 19:27'] # the month of March was bad``
- ``good_ens``: a list of good indices (based on the raw file, zero-based) to clip the data by. Example: ``good_ens: [10, 500]``. To specify multiple good ranges, add additional pairs of indices: ``good_ens: [10, 500, 560, 600]`` will clip the data to samples 10-500 and 560-600 in the final file.

Multiple instruments
--------------------

Options applicable to many instrument types include:

- ``<VAR>_bad_ens``: specify bad ensemble ranges (either index numbers or dates) that should be set to ``_FillValue``. If you want multiple ranges, you can do this with additional values in the array. For example, ``Turb_bad_ens: ['2017-09-30 21:15', '2017-10-02 09:30', '2017-10-12 20:45', '2017-10-16 00:30']``. This will set the ranges in late September and early October, and again in mid-October, to ``_FillValue``.
- ``<VAR>_min``: fill values less than this minimum valid value. Values outside this range will become ``_FillValue``. Substitute your variable for ``<VAR>``, e.g. ``fDOMQSU_min``.
- ``<VAR>_max``: fill values more than this maximum valid value.
- ``<VAR>_min_diff``: fill values where data decreases by more than this number of units in a single time step. Should be a negative number.
- ``<VAR>_max_diff``: fill values where data increases by more than this number of units in a single time step.
- ``<VAR>_med_diff``: fill values where difference between a 5-point (default) median filter and original values is greater than this number.
- ``<VAR>_med_diff_pct``: fill values where percent difference between a 5-point (default) median filter and original values is greater than this number.
- ``<VAR>_trim_fliers``: fill flier values, which are data points surrounded by filled data. Set to the maximum size of flier clumps to remove.

Aquadopp
--------

Aquadopp-specific options include:

- ``head_rotation``: probably will be ``'horizontal'``
- ``cutoff_ampl``: will probably always be ``0``
- ``trim_method``: can be ``'water level'``, ``'water level sl'``, ``'bin range'``, ``None``, or ``'none'``. Or just omit the option entirely if you don't want to use it.
- ``<VAR>_trim_single_bins``: trim data where only a single bin of data (after trimming via ``trim_method``) remains. Set this value to ``true`` to enable.
- ``<VAR>_maxabs_diff_2d``: trim values in a 2D DataArray when the absolute value of the increase is greater than a specified amount

.. literalinclude:: ../examples/aqd_config.yaml
   :language: yaml
   :linenos:

Signature
---------

Signature-specific options include (see Aquadopp for others):

- ``outdir``: output directory (make sure it exists) to write individual ``cdf`` files before being compiled into a single ``cdf`` file per data type
- ``orientation``: can be ``UP`` or ``DOWN`` use this to identify orientation of profiler
- ``head_rotation``: probably will be ``'horizontal'``

.. literalinclude:: ../examples/aqd_config.yaml
   :language: yaml
   :linenos:

d|wave
------

d|wave-specific options include:

- ``basefile``: the input filename without extension or data type. For example, if your exported text files are named ``055170_20190219_1547_burst.txt``, ``055170_20190219_1547_data.txt``, etc., ``basefile`` will be ``055170_20190219_1547``.
- ``wp_min``, ``wp_max``: min/max allowable wave period, in seconds
- ``wh_min``, ``wh_max``: min/max allowable wave height, in meters
- ``wp_ratio``: maximum allowable ratio between peak period (``wp_peak``) and mean period (``wp_4060``).
- ``<VAR>_min``: fill values less than this minimum valid value. Values outside this range will become ``_FillValue``. Substitute your variable for ``<VAR>``, e.g. ``P_1ac_min``. Only works for ``P_1`` and ``P_1ac``. Useful for trimming by minimum pressure for instruments that go dry on some tidal cycles. Any data within the burst less than the threshold will result in the full burst being filled.

.. literalinclude:: ../examples/dw_config.yaml
   :language: yaml
   :linenos:

EXO
---

EXO-specific options include:

- ``skiprows``: number of lines to skip in the CSV before the real data begins
- ``trim_by_salinity``: if ``'true'``, use salinity (``S_41``) as a master variable. Wherever salinity is ``_FillValue``, all other variables will be filled as well. Useful for when the instrument comes out of the water.
- ``drop_vars``: a list of variables to be removed from the final file. For example, ``drop_vars: ['nLF_Cond_µS_per_cm', 'Wiper_Position_volt', 'Cable_Pwr_V']``.

Note that negative numeric values in the YAML config file must be treated with care so as not to be interpreted as strings. If you want the minimum value to be, say, -0.2 units for a particular parameter, you must write this as ``-0.2`` and not ``-.2`` in the config file. The latter format will be interpreted as a string and will cause an error.

.. literalinclude:: ../examples/exo_config.yaml
   :language: yaml
   :linenos:

WET Labs ECO NTU
----------------

NTU-specific options include:

- All the _min, _max, _bad_ens, etc. options available to the EXO.
- ``Turb_std_max``: fill turbidity based on a maximum standard deviation value.
- ``spb``: samples per burst
- ``user_ntucal_coeffs``: polynomial coefficients, e.g., ``[9.078E-07, 5.883E-02, -2.899E+00]``.

Vaisala WXT536
--------------

WXT-specific options include:

- ``RTK_elevation_NAVD88``: RTK elevation of the sensor referenced to NAVD88 in meters.
- ``dir_offset``: a direction offset in degrees from magnetic north to be applied if the sensor was not pointing toward magnetic north.
- ``dir_offset_note``: a note about the direction offset being used.

EofE ECHOLOGGER
---------------
- All the _min, _max, _bad_ens, etc. options available to the EXO.
- instrument_type: types "ea" and "aa" are supported.
- orientation: orientation of transducers types 'DOWN' or 'UP' are supported.
- average_salinity: average salinity value (PSU) for the water mass for the deployment site and time period.
- average_salinity_note: source of average salinity value.
