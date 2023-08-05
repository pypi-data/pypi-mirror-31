"""
This file contains a class that holds the TimeSeries class. This class is used
to "manage" the time series within PASTAS. It has methods to change a time
series in frequency and extend the time series, without losing the original
data.

August 2017, R.A. Collenteur

"""
from __future__ import print_function, division

import logging

import pandas as pd
from pastas.utils import get_dt, get_time_offset, timestep_weighted_resample

logger = logging.getLogger(__name__)


class TimeSeries(pd.Series):
    """Class that deals with all user-provided Time Series.

    Parameters
    ----------
    series: pandas.Series or pastas.TimeSeries
        Pandas Series with time indices and values or a Pastas.TimeSeries
        instance. If the latter is provided, a new TimeSeries.
    name: str, optional
        String with the name of the time series, if None is provided,
        pastas will try to derive the name from the series.
    settings: str or dict, optional
        String with the name of one of the predefined settings (obtained
        through ps.TimeSeries._predefined_settings.) or a dictionary with the
        settings to be applied. This does not have to include all the
        settings arguments.
    metadata: dict, optional
        Dictionary with metadata of the time series.
    freq_original str, optional
    **kwargs: dict, optional
        Any keyword arguments that are provided but are not listed will be
        passed as addiotional settings.

    Notes
    -----
    For the individual options for the different settings please refer to
    the docstring from the TimeSeries.update_series() method.

    See Also
    --------
    ps.TimeSeries.update_series

    Returns
    -------
    series: pastas.TimeSeries
        Returns a pastas.TimeSeries object.

    """
    _predefined_settings = {
        "oseries": {"fill_nan": "drop", "sample_down": "drop"},
        "prec": {"sample_up": "divide", "sample_down": "sum",
                 "fill_nan": 0.0, "fill_before": "mean", "fill_after": "mean"},
        "evap": {"sample_up": "divide", "sample_down": "sum",
                 "fill_before": "mean", "fill_after": "mean"},
        "well": {"sample_up": "divide", "sample_down": "sum",
                 "fill_nan": 0.0, "fill_before": 0.0, "fill_after": 0.0},
        "waterlevel": {"sample_up": "interpolate", "sample_down": "mean",
                       "fill_before": "mean", "fill_after": "mean"},
        "level": {"sample_up": "interpolate", "sample_down": "mean",
                  "fill_before": "mean", "fill_after": "mean"},
        "flux": {"sample_up": "bfill", "sample_down": "mean",
                 "fill_before": "mean", "fill_after": "mean"},
        "quantity": {"sample_up": "divide", "sample_down": "sum",
                     "fill_before": "mean", "fill_after": "mean"},
    }

    def __init__(self, series, name=None, settings=None, metadata=None,
                 freq_original=None, **kwargs):
        pd.Series.__init__(self)

        self.index.name = "Date"
        if isinstance(series, TimeSeries):
            self.series_original = series.series_original.copy()
            self.freq_original = series.freq_original
            self.settings = series.settings.copy()
            self.metadata = series.metadata.copy()
            self.series = series.series.copy()
            self._update_inplace(series)

            validate = False
            update = False

            if settings is None:
                settings = self.settings.copy()
        else:
            validate = True
            update = True
            # Store a copy of the original series
            self.series_original = series.copy()
            self.freq_original = freq_original
            self.settings = dict(
                freq=None,
                sample_up=None,
                sample_down=None,
                fill_nan="interpolate",
                fill_before=None,
                fill_after=None,
                tmin=None,
                tmax=None,
                norm=None
            )
            self.metadata = {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "projection": None
            }

        # Use user provided name or set from series
        if name is None:
            name = series.name
        self.name = name
        self.series_original.name = name

        if metadata is not None:
            self.metadata.update(metadata)

        # kind argument will be deprecated in version 0.9.6
        kind = kwargs.pop("kind", None)
        if kind:
            logger.warning("Deprecation error: the kind argument will be "
                           "deprecated in Pastas 0.9.6. Please provide "
                           "a string to the settings argument.")
            if kind in self._predefined_settings.keys():
                if self.update_settings(**self._predefined_settings[kind]):
                    update = True

        # Update the options with user-provided values, if any.
        if settings:
            if isinstance(settings, str):
                if settings in self._predefined_settings.keys():
                    settings = self._predefined_settings[settings]
                else:
                    logger.error("Settings shortcut code %s is not in the "
                                 "predefined settings options. Please choose "
                                 "from %s", self._predefined_settings.keys())
            if self.update_settings(**settings):
                update = True
        if kwargs:
            if self.update_settings(**kwargs):
                update = True

        # Create a validated series for computations and update
        if validate:
            self.series = self.validate_series(series)
        if update:
            self.update_series(force_update=True, **self.settings)

    def validate_series(self, series):
        """ This method performs some PASTAS specific tests for the TimeSeries.

        Parameters
        ----------
        series: pd.Series
            Pandas series object containing the series time series.

        Returns
        -------
        series: pandas.Series
            The validated series as pd.Series

        Notes
        -----
        The Series are validated for the following cases:

            1. Series is an actual pandas Series;
            2. Nan-values from begin and end are removed;
            3. Nan-values between observations are removed;
            4. Indices are in Timestamps (standard throughout PASTAS),
            making the index a pandas DateTimeIndex.
            5. Duplicate indices are removed (by averaging).

        """

        # 1. Check if series is a Pandas Series
        assert isinstance(series, pd.Series), "Expected a Pandas Series, " \
                                              "got %s" % type(series)

        # 2. Make sure the indices are Timestamps and sorted
        series.index = pd.to_datetime(series.index)
        series.sort_index(inplace=True)
        series.index.name = "Date"

        # 3. Drop nan-values at the beginning and end of the time series
        series = series.loc[series.first_valid_index():series.last_valid_index(
        )].copy(deep=True)

        # 4. Find the frequency of the original series
        if self.freq_original:
            pass
        elif pd.infer_freq(series.index):
            self.freq_original = pd.infer_freq(series.index)
            logger.info("Inferred frequency from time series %s: freq=%s " % (
                self.name, self.freq_original))
        else:
            self.freq_original = self.settings["freq"]
            if self.freq_original is None:
                logger.info(
                    "Cannot determine frequency of series %s" % self.name)
            elif self.settings["fill_nan"] and self.settings["fill_nan"] != \
                    "drop":
                logger.warning("User-provided frequency is applied when "
                               "validating the Time Series %s. Make sure the "
                               "provided frequency is close to the real "
                               "frequency of the original series." % self.name)

        # 5. Handle duplicate indices
        if not series.index.is_unique:
            logger.warning("duplicate time-indexes were found in the Time "
                           "Series %s. Values were averaged." % self.name)
            grouped = series.groupby(level=0)
            series = grouped.mean()

        # 6. drop nan-values
        if series.hasnans:
            series = self.fill_nan(series)

        if self.settings["tmin"] is None:
            self.settings["tmin"] = series.index.min()
        if self.settings["tmax"] is None:
            self.settings["tmax"] = series.index.max()

        return series

    def update_settings(self, **kwargs):
        """Internal method that check if an update is actually necessary.

        TODO still some bug in here when comparing timestamps. causing uneccesary updates..

        """
        update = False
        for key, value in kwargs.items():
            if key in ["tmin", "tmax"]:
                value = pd.Timestamp(value)
            if value != self.settings[key]:
                self.settings[key] = value
                update = True
        return update

    def update_series(self, force_update=False, **kwargs):
        """Method to update the series with new options, but most likely
        only a change in the frequency before solving a PASTAS model.

        Parameters
        ----------
        force_update: bool, optional
            argument that is used to force an update, even when no changes
            are found. Internally used by the __init__ method. Default is
            False.
        freq: str, optional
            String representing the desired frequency of the time series.
        sample_up: str or float, optional
            String with the method to use when the frequency is increased (
            e.g. Weekly to daily). Possible values are: "backfill", "bfill",
            "pad", "ffill", "mean", "interpolate", "divide" or a float value
            to fill the gaps.
        sample_down: str, optional
            String with the method to use when the frequency decreases
            (e.g. from daily to weekly values). Possible values are: "mean",
            "drop", "sum", "min", "max".
        fill_nan: str or float, optional
            Method to use when there ar nan-values in the time series.
            Possible values are: "mean", "drop", "interpolate" (default) or a
            float value.
        fill_before: str or float, optional
            Method used to extend a time series before any measurements are
            available. possible values are: "mean" or a float value.
        fill_after: str ir float, optional
            Method used to extens a time series after any measurements are
            available. Possible values are: "mean" or a float value.
        tmin: str or pandas.TimeStamp, optional
            String that can be converted to, or a Pandas TimeStamp with the
            minimum time of the series.
        tmax; str or pandas.TimeStamp, optional
            String that can be converted to, or a Pandas TimeStamp with the
            maximum time of the series.
        norm: str or flaot, optional
            String with the method to normalize the time series with.
            Possible values are: "mean" or "median", "min", "max" or a float
            value.

        Notes
        -----
        The method will validate if any of the settings is changed to
        determine if the series need to be updated.

        """
        if self.update_settings(**kwargs) or force_update:
            # Get the validated series to start with
            series = self.series.copy(deep=True)

            # Update the series with the new settings
            series = self.change_frequency(series)
            series = self.fill_before(series)
            series = self.fill_after(series)
            series = self.normalize(series)

            self._update_inplace(series)

    def change_frequency(self, series):
        """Method to change the frequency of the time series.

        """
        freq = self.settings["freq"]

        # 1. If no freq string is present or is provided (e.g. Oseries)
        if not freq:
            return series
        # 2. If original frequency could not be determined
        elif not self.freq_original:
            series = self.sample_weighted(series)
        else:
            dt_new = get_dt(freq)
            dt_org = get_dt(self.freq_original)
            # 3. If new and original frequency are not a multiple of each other
            eps = 1e-10
            if not ((dt_new % dt_org) < eps or (dt_org % dt_new) < eps):
                series = self.sample_weighted(series)
            # 4. If new frequency is lower than its original
            elif dt_new < dt_org:
                series = self.sample_up(series)
            # 5. If new frequency is higher than its original
            elif dt_new > dt_org:
                series = self.sample_down(series)
            # 6. If new frequency is equal to its original
            elif dt_new == dt_org:
                series = self.fill_nan(series)

        # Drop nan-values at the beginning and end of the time series
        series = series.loc[
                 series.first_valid_index():series.last_valid_index()]

        return series

    def sample_up(self, series):
        """Resample the time series when the frequency increases (e.g. from
        weekly to daily values).

        """
        method = self.settings["sample_up"]
        freq = self.settings["freq"]

        n = series.isnull().values.sum()

        if method in ["backfill", "bfill", "pad", "ffill"]:
            series = series.asfreq(freq, method=method)
        elif method is None:
            pass
        else:
            if method == "mean":  # when would you ever want this?
                series = series.asfreq(freq)
                series.fillna(series.mean(), inplace=True)  # Default option
            elif method == "interpolate":
                series = series.asfreq(freq)
                series.interpolate(method="time", inplace=True)
            elif method == "divide":
                dt = series.index.to_series().diff() / pd.Timedelta(1, freq)
                series = series.iloc[1:] / dt.iloc[1:]
                series = series.asfreq(freq, method="bfill")
            elif isinstance(method, float):
                series = series.asfreq(freq)
                series.fillna(method, inplace=True)
            else:
                logger.warning("User-defined option for sample_up %s is not "
                               "supported" % method)
        if n > 0:
            logger.info("%i nan-value(s) was/were found and filled with: %s"
                        % (n, method))

        return series

    def sample_down(self, series):
        """Resample the time series when the frequency decreases (e.g. from
        daily to weekly values).

        Notes
        -----
        make sure the labels are still at the end of each period, and
        data at the right side of the bucket is included (see
        http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.resample.html)

        """
        method = self.settings["sample_down"]
        freq = self.settings["freq"]

        # Provide some standard pandas arguments for all options
        kwargs = {"label": "right", "closed": "right"}

        if method == "mean":
            series = series.resample(freq, **kwargs).mean()
        elif method == "drop":  # does this work?
            series = series.resample(freq, **kwargs).mean().dropna()
        elif method == "sum":
            series = series.resample(freq, **kwargs).sum()
        elif method == "min":
            series = series.resample(freq, **kwargs).min()
        elif method == "max":
            series = series.resample(freq, **kwargs).max()
        else:
            logger.warning("User-defined option for sample_down %s is not "
                           "supported" % method)

        logger.info("Time Series %s were sampled down to freq %s with method "
                    "%s" % (self.name, freq, method))

        return series

    def sample_weighted(self, series):
        series0 = series
        freq = self.settings["freq"]
        series = series.resample(freq).mean()
        series = timestep_weighted_resample(series0, series.index)
        logger.info("Time Series %s were sampled down to freq %s with method "
                    "%s" % (self.name, freq, 'timestep_weighted_resample'))
        return series

    def fill_nan(self, series):
        """Fill up the nan-values when present and a constant frequency is
        required.

        """

        method = self.settings["fill_nan"]
        freq = self.freq_original

        if freq:
            series = series.asfreq(freq)
            n = series.isnull().values.sum()
            if method == "drop":
                series.dropna(inplace=True)
            elif method == "mean":
                series.fillna(series.mean(), inplace=True)  # Default option
            elif method == "interpolate":
                series.interpolate(method="time", inplace=True)
            elif isinstance(method, float):
                series.fillna(method, inplace=True)
            else:
                logger.warning("User-defined option for fill_nan %s is not "
                               "supported" % method)
        else:
            method = "drop"
            n = series.isnull().values.sum()
            series.dropna(inplace=True)
        if n > 0:
            logger.info("%i nan-value(s) was/were found and filled with: %s"
                        % (n, method))

        return series

    def fill_before(self, series):
        """Method to add a period in front of the available time series.

        """

        freq = self.settings["freq"]
        method = self.settings["fill_before"]
        tmin = self.settings["tmin"]

        if tmin is None:
            pass
        elif method is None:
            pass
        elif pd.Timestamp(tmin) >= series.index.min():
            series = series.loc[pd.Timestamp(tmin):]
        else:
            tmin = pd.Timestamp(tmin)
            # When time offsets are not equal
            time_offset = get_time_offset(tmin, freq)
            tmin = tmin - time_offset

            index_extend = pd.date_range(start=tmin, end=series.index.min(),
                                         freq=freq)
            index = series.index.union(index_extend[:-1])
            series = series.reindex(index)

            if method == "mean":
                series.fillna(series.mean(), inplace=True)  # Default option
            elif isinstance(method, float):
                series.fillna(method, inplace=True)
            else:
                logger.warning("User-defined option for fill_before %s is not "
                               "supported" % method)

        return series

    def fill_after(self, series):
        """Method to add a period in front of the available time series.

        """

        freq = self.settings["freq"]
        method = self.settings["fill_after"]
        tmax = self.settings["tmax"]

        if tmax is None:
            pass
        elif method is None:
            pass
        elif pd.Timestamp(tmax) <= series.index.max():
            series = series.loc[:pd.Timestamp(tmax)]
        else:
            # When time offsets are not equal
            time_offset = get_time_offset(tmax, freq)
            tmax = tmax - time_offset
            index_extend = pd.date_range(start=series.index.max(), end=tmax,
                                         freq=freq)
            index = series.index.union(index_extend)
            series = series.reindex(index)

            if method == "mean":
                series.fillna(series.mean(), inplace=True)  # Default option
            elif isinstance(method, float):
                series.fillna(method, inplace=True)
            else:
                logger.warning("User-defined option for fill_after %s is not "
                               "supported" % method)

        return series

    def normalize(self, series):
        """Method to normalize the time series.

        TODO: can we also choose to normalize by the fill_before-value?

        """
        method = self.settings["norm"]

        if method is None:
            pass
        elif method == "mean":
            series = series.subtract(series.mean())
        elif method == "median":
            series = series.subtract(series.median())
        elif method == "min":
            series = series.subtract(series.min())
        elif method == "max":
            series = series.subtract(series.max())
        elif isinstance(method, float):
            series = series.subtract(method)
        else:
            logger.info("Selected method %s to normalize the time series is "
                        "not supported" %method)

        return series

    def multiply(self, other):
        self.series = self.series.multiply(other)
        self.series_original = self.series_original.multiply(other)
        self.update_series(force_update=True)

    def transform_coordinates(self, to_projection):
        try:
            from pyproj import Proj, transform
            inProj = Proj(init=self.metadata['projection'])
            outProj = Proj(init=to_projection)
            x, y = transform(inProj, outProj, self.metadata['x'],
                             self.metadata['y'])
            self.metadata['x'] = x
            self.metadata['y'] = y
            self.metadata['projection'] = to_projection
        except ImportError:
            raise ImportError(
                'The module pyproj could not be imported. Please '
                'install through:'
                '>>> pip install pyproj'
                'or ... conda install pyproj')

    def dump(self, series=True, transformed_series=False):
        """Method to export the Time Series to a json format.

        Parameters
        ----------
        transformed_series
        series: Boolean
            True to export the original time series, False to only export
            the TimeSeries object"s name.

        Returns
        -------
        data: dict
            dictionary with the necessary information to recreate the
            TimeSeries object completely.

        """
        data = dict()

        if series:
            if transformed_series:
                data["series"] = self
            else:
                data["series"] = self.series_original

        data["name"] = self.name
        data["settings"] = self.settings
        data["metadata"] = self.metadata
        data["freq_original"] = self.freq_original

        return data
