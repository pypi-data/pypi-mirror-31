import math

import numpy as np

from . import calcs


def daily(tmin, tmax, ea, rs, uz, zw, elev, lat, doy, surface,
          method='asce', rso_type=None, rso=None,
          input_units={}, output_units={}):
    """ASCE Daily Standardized Reference Evapotranspiration (ET)

    Arguments
    ---------
    tmin : ndarray
        Minimum daily temperature [C].
    tmax : ndarray
        Maximum daily temperature [C].
    ea : ndarray
        Actual vapor pressure [kPa].
    rs : ndarray
        Incoming shortwave solar radiation [MJ m-2 day-1].
    uz : ndarray
        Wind speed [m/s].
    zw : float
        Wind speed height [m].
    elev : ndarray
        Elevation [m].
    lat : ndarray
        Latitude [radians].
    doy : ndarray
        Day of year.
    surface : {'eto', 'etr', 'grass', 'alfalfa', 'short', 'tall'}
        Specifies which reference crop surface.
        * 'etr', 'alfalfa', 'tall' -- Tall reference crop
        * 'eto', 'grass', 'short' -- Short reference crop
    method : {'asce' (default), 'refet'}, optional
        Specifies which calculation method to use.
        * 'asce' -- Calculations will follow ASCE-EWRI 2005 [1] equations.
        * 'refet' -- Calculations will follow RefET software.
    rso_type : {None (default), 'full' , 'simple', 'array'}, optional
        Specifies which clear sky solar radiation (Rso) model to use.
        * None -- Rso type will be determined from "method" parameter
        * 'full' -- Full clear sky solar formulation
        * 'simple' -- Simplified clear sky solar formulation
        * 'array' -- Read Rso values from "rso" function parameter
    rso : array_like or None, optional
        Clear sky solar radiation [MJ m-2 day-1] (the default is None).
        Only used if rso_type == 'array'.
    input_units : dict, optional
        Input unit types.
    output_units : dict, optional
        Output unit types.

    Returns
    -------
    etsz : ndarray
        Standardized reference ET [mm].

    Raises
    ------
    ValueError
        If 'surface', 'method' or 'rso_type' parameter is invalid.
        If latitude values are outside the range [-pi/2, pi/2].

    Notes
    -----
    cn: 900 for ETo, 1600 for ETr
    cd: 0.34 for ETo, 0.38 for ETr
    Divide solar radiation values by 0.0864 to convert MJ m-2 day-1 to W m-2

    References
    ----------
    .. [1] ASCE-EWRI (2005). The ASCE standardized reference evapotranspiration
        equation. ASCE-EWRI Standardization of Reference Evapotranspiration
        Task Committee Rep., ASCE Reston, Va.
        http://www.kimberly.uidaho.edu/water/asceewri/ascestzdetmain2005.pdf
        http://www.kimberly.uidaho.edu/water/asceewri/appendix.pdf
    """

    # Convert all inputs to NumPy arrays
    tmin = np.array(tmin, copy=True, ndmin=1)
    tmax = np.array(tmax, copy=True, ndmin=1)
    ea = np.array(ea, copy=True, ndmin=1)
    rs = np.array(rs, copy=True, ndmin=1)
    uz = np.array(uz, copy=True, ndmin=1)
    elev = np.array(elev, copy=True, ndmin=1)
    lat = np.array(lat, copy=True, ndmin=1)

    # Check that latitudes are in radians
    if np.any(np.fabs(lat) > (0.5 * math.pi)):
        raise ValueError('latitudes must be in radians [-pi/2, pi/2]')

    if method.lower() not in ['asce', 'refet']:
        raise ValueError('method must be "asce" or "refet"')

    if surface.lower() in ['eto', 'grass', 'short']:
        # Tall reference crop parameters
        cn, cd = 900, 0.34
    elif surface.lower() in ['etr', 'alfalfa', 'tall']:
        # Short reference crop parameters
        cn, cd = 1600, 0.38
    else:
        raise ValueError('surface must be "etr" or "eto"')

    if rso_type is None:
        pass
    elif rso_type.lower() not in ['simple', 'full', 'array']:
        raise ValueError('rso_type must be None, "simple", "full", or "array')
    elif rso_type.lower() in 'array':
        # Check that rso is an array
        pass

    # To match standardized form, pair is calculated from elevation
    pair = calcs._air_pressure(elev, method)

    psy = 0.000665 * pair

    tmean = 0.5 * (tmax + tmin)
    es_slope = calcs._es_slope(tmean, method)

    # Saturated vapor pressure
    es = 0.5 * (calcs._sat_vapor_pressure(tmax) + calcs._sat_vapor_pressure(tmin))

    # Vapor pressure deficit
    vpd = calcs._vpd(es, ea)

    # Extraterrestrial radiation
    ra = calcs._ra_daily(lat, doy, method)

    # Clear sky solar radiation
    # If rso_type is not set, use the method
    # If rso_type is set, use rso_type directly
    if rso_type is None :
        if method.lower() == 'asce':
            rso = calcs._rso_simple(ra, elev)
        elif method.lower() == 'refet':
            rso = calcs._rso_daily(ra, ea, pair, doy, lat)
    elif rso_type.lower() == 'simple':
        rso = calcs._rso_simple(ra, elev)
    elif rso_type.lower() == 'full':
        rso = calcs._rso_daily(ra, ea, pair, doy, lat)
    elif rso_type.lower() == 'array':
        # Use rso array passed to function
        pass

    # Cloudiness fraction
    fcd = calcs._fcd_daily(rs, rso)

    # Net long-wave radiation
    rnl = calcs._rnl_daily(tmax, tmin, ea, fcd)

    # Net radiation (Eqs. 15 and 16)
    rn = 0.77 * rs - rnl

    # Wind speed
    u2 = calcs._wind_height_adjust(uz, zw)

    # Daily reference ET (Eq. 1)
    etsz = (
        (0.408 * es_slope * rn + (psy * cn * u2 * vpd / (tmean + 273))) /
        (es_slope + psy * (cd * u2 + 1)))

    return etsz
