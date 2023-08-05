"""The stressmodels module contains all the stressmodels that available in
Pastas.

Supported Stressmodels
----------------------
The following stressmodels are supported and tested:

- StressModel
- StressModel2
- Constant

All other stressmodels are for research purposes only and are not (yet)
fully supported and tested.

TODO
----
- Test and support StepModel
- Test and support LinearTrend

"""

from __future__ import print_function, division

import logging

import numpy as np
import pandas as pd
from scipy.signal import fftconvolve

from .decorators import set_parameter
from .rfunc import One
from .timeseries import TimeSeries

logger = logging.getLogger(__name__)

__all__ = ["StressModel", "StressModel2", "Constant", "StepModel",
           "LinearTrend"]


class StressModelBase:
    """StressModel Base class called by each StressModel object.

    Attributes
    ----------
    nparam : int
        Number of parameters.
    name : str
        Name of this stressmodel object. Used as prefix for the parameters.
    parameters : pandas.DataFrame
        Dataframe containing the parameters.

    """
    _name = "StressModelBase"

    def __init__(self, rfunc, name, tmin, tmax, up, meanstress, cutoff):
        self.rfunc = rfunc(up, meanstress, cutoff)
        self.parameters = pd.DataFrame(
            columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        self.nparam = self.rfunc.nparam
        self.name = name
        self.tmin = tmin
        self.tmax = tmax
        self.freq = None
        self.stress = []

    def set_init_parameters(self):
        """Set the initial parameters (back) to their default values.

        """
        pass

    @set_parameter
    def set_initial(self, name, value):
        """Internal method to set the initial parameter value.

        Notes
        -----
        The preferred method for parameter setting is through the model.

        """
        self.parameters.loc[name, 'initial'] = value

    @set_parameter
    def set_pmin(self, name, value):
        """Internal method to set the lower bound of the parameter value.

        Notes
        -----
        The preferred method for parameter setting is through the model.

        """
        self.parameters.loc[name, 'pmin'] = value

    @set_parameter
    def set_pmax(self, name, value):
        """Internal method to set the upper bound of the parameter value.

        Notes
        -----
        The preferred method for parameter setting is through the model.

        """
        self.parameters.loc[name, 'pmax'] = value

    @set_parameter
    def set_vary(self, name, value):
        """Internal method to set if the parameter is varied during
        optimization.

        Notes
        -----
        The preferred method for parameter setting is through the model.

        """
        self.parameters.loc[name, 'vary'] = value

    def update_stress(self, **kwargs):
        """Method to change the frequency of the individual TimeSeries in
        the Pandas DataFrame.

        Parameters
        ----------
        freq

        Returns
        -------

        """
        for stress in self.stress:
            stress.update_series(**kwargs)

        if "freq" in kwargs:
            self.freq = kwargs["freq"]

    def handle_stress(self, stress, settings):
        """Method to handle user provided stress in init

        Parameters
        ----------
        stress: pandas.Series, pastas.TimeSeries or iterable
        settings: dict or iterable

        Returns
        -------
        stress: dict
            dictionary with strings

        """
        data = []

        if isinstance(stress, pd.Series):
            data.append(TimeSeries(stress, settings))
        elif isinstance(stress, dict):
            for i, value in enumerate(stress.values()):
                data.append(TimeSeries(value, settings=settings[i]))
        elif isinstance(stress, list):
            for i, value in enumerate(stress):
                data.append(TimeSeries(value, settings=settings[i]))
        else:
            logger.warning("provided stress format is unknown. Provide a"
                           "Series,dict or list.")
        return data

    def dump_stress(self, series=True, transformed_series=False):
        """Method to dump all stresses in the stresses list.

        Parameters
        ----------
        data: dict
            Dictionary for the data to go into.
        series: Boolean
            True if time series are to be exported, False if only the name
            of the time series are needed. Settings are always exported.

        Returns
        -------
        data: dict
            dictionary with the dump of the stresses.

        """
        data = []

        for stress in self.stress:
            data.append(stress.dump(series=series,
                                    transformed_series=transformed_series))

        return data

    def get_stress(self, p=None):
        """Returns the stress or stresses of the time series object as a pandas
        DataFrame.

        If the time series object has multiple stresses each column
        represents a stress.

        Returns
        -------
        stress: pd.Dataframe
            Pandas dataframe of the stress(es)

        """
        return self.stress

    def dump(self, series=True):
        data = dict()
        data["stressmodel"] = "StressModelBase"

        return data


class StressModel(StressModelBase):
    """Time series model consisting of the convolution of one stress with one
    response function.

    Parameters
    ----------
    stress: pandas.Series
        pandas Series object containing the stress.
    rfunc: rfunc class
        Response function used in the convolution with the stress.
    name: str
        Name of the stress.
    up: Boolean, optional
        True if response function is positive (default), False if negative.
    cutoff: float, optional
        float between 0 and 1 to determine how long the response is (default
        is 99% of the actual response time). Used to reduce computation times.
    settings: dict or str, optional
        The settings of the stress. This can be a string referring to a
        predefined settings dict, or a dict with the settings to apply.
        Refer to the docstring of pastas.Timeseries for further information.
    metadata: dict, optional
        dictionary containing metadata about the stress. This is passed onto
        the TimeSeries object.

    Examples
    --------
    >>> import pastas as ps
    >>> import pandas as pd
    >>> sm = ps.StressModel(stress=pd.Series(), rfunc=ps.Gamma, name="Prec", \
    >>> settings="prec")

    See Also
    --------
    pastas.rfunc
    pastas.TimeSeries

    """
    _name = "StressModel"

    def __init__(self, stress, rfunc, name, up=True, cutoff=0.99,
                 settings=None, metadata=None, meanstress=None, **kwargs):
        if isinstance(stress, list):
            stress = stress[0]  # Temporary fix Raoul, 2017-10-24

        kind = kwargs.pop("kind", None)
        stress = TimeSeries(stress, kind=kind, settings=settings,
                            metadata=metadata)

        if meanstress is None:
            meanstress = stress.mean()

        StressModelBase.__init__(self, rfunc, name, stress.index.min(),
                                 stress.index.max(), up, meanstress, cutoff)
        self.freq = stress.settings["freq"]
        self.stress = [stress]
        self.set_init_parameters()

    def set_init_parameters(self):
        """Set the initial parameters (back) to their default values.

        """
        self.parameters = self.rfunc.set_parameters(self.name)

    def simulate(self, p, tindex=None, dt=1):
        """Simulates the head contribution.

        Parameters
        ----------
        p: 1D array
           Parameters used for simulation.
        tindex: pandas.Series, optional
           Time indices to simulate the model.

        Returns
        -------
        pandas.Series
            The simulated head contribution.

        """
        b = self.rfunc.block(p, dt)
        stress = self.stress[0]
        npoints = stress.index.size
        h = pd.Series(data=fftconvolve(stress, b, 'full')[:npoints],
                      index=stress.index, name=self.name, fastpath=True)
        if tindex is not None:
            h = h.loc[tindex]
        return h

    def dump(self, series=True, transformed_series=False):
        """Method to export the StressModel object.

        Returns
        -------
        data: dict
            dictionary with all necessary information to reconstruct the
            StressModel object.

        """
        data = dict()
        data["stressmodel"] = self._name
        data["rfunc"] = self.rfunc._name
        data["name"] = self.name
        data["up"] = True if self.rfunc.up == 1 else False
        data["cutoff"] = self.rfunc.cutoff
        data["stress"] = self.dump_stress(series,
                                          transformed_series=transformed_series)

        return data


class StressModel2(StressModelBase):
    """Time series model consisting of the convolution of two stresses with one
    response function. The first stress causes the head to go up and the second
    stress causes the head to go down.

    Parameters
    ----------
    stress: list of pandas.Series
        list of pandas.Series or pastas.TimeSeries objects containing the
        stresses.
    rfunc: pastas.rfunc instance
        Response function used in the convolution with the stress.
    name: str
        Name of the stress
    up: Boolean, optional
        True if response function is positive (default), False if negative.
    cutoff: float
        float between 0 and 1 to determine how long the response is (default
        is 99% of the actual response time). Used to reduce computation times.
    settings: Tuple with two dicts
        The settings of the individual TimeSeries.
    settings: list of dicts or strs, optional
        The settings of the stresses. This can be a string referring to a
        predefined settings dict, or a dict with the settings to apply.
        Refer to the docstring of pastas.Timeseries for further information.
        Default is ("prec", "evap").
    metadata: list of dicts, optional
        dictionary containing metadata about the stress. This is passed onto
        the TimeSeries object.

    Notes
    -----
    The order in which the stresses are provided is the order the metadata
    and settings dictionaries or string are passed onto the TimeSeries
    objects. By default, the precipitation stress is the first and the
    evaporation stress the second stress.

    See Also
    --------
    pastas.rfunc
    pastas.TimeSeries

    """
    _name = "StressModel2"

    def __init__(self, stress, rfunc, name, up=True, cutoff=0.99,
                 settings=("prec", "evap"), metadata=(None, None),
                 meanstress=None, **kwargs):
        # First check the series, then determine tmin and tmax
        kind = kwargs.pop("kind", (None, None))

        stress0 = TimeSeries(stress[0], kind=kind[0], settings=settings[0],
                             metadata=metadata[0])
        stress1 = TimeSeries(stress[1], kind=kind[1], settings=settings[1],
                             metadata=metadata[1])

        # Select indices from validated stress where both series are available.
        index = stress0.series.index.intersection(stress1.series.index)
        if index.size is 0:
            logger.warning('The two stresses that were provided have no '
                           'overlapping time indices. Please make sure time indices overlap or apply to separate time series objects.')

        # First check the series, then determine tmin and tmax
        stress0.update_series(tmin=index.min(), tmax=index.max())
        stress1.update_series(tmin=index.min(), tmax=index.max())

        if meanstress is None:
            meanstress = stress0.mean() - stress1.mean()

        StressModelBase.__init__(self, rfunc, name, index.min(), index.max(),
                                 up, meanstress, cutoff)
        self.stress.append(stress0)
        self.stress.append(stress1)

        self.freq = stress0.settings["freq"]
        self.set_init_parameters()

    def set_init_parameters(self):
        """Set the initial parameters back to their default values.

        """
        self.parameters = self.rfunc.set_parameters(self.name)
        self.parameters.loc[self.name + '_f'] = (-1.0, -2.0, 2.0, 1, self.name)
        self.nparam += 1

    def simulate(self, p, tindex=None, dt=1, istress=None):
        """Simulates the head contribution.

        Parameters
        ----------
        p: 1D array
           Parameters used for simulation.
        tindex: pandas.Series, optional
           Time indices to simulate the model.

        Returns
        -------
        pandas.Series
            The simulated head contribution.

        """
        b = self.rfunc.block(p[:-1], dt)
        npoints = self.stress[0].index.size
        stress = self.get_stress(p=p, istress=istress)
        h = pd.Series(data=fftconvolve(stress, b, 'full')[:npoints],
                      index=self.stress[0].index, name=self.name,
                      fastpath=True)
        if tindex is not None:
            h = h.loc[tindex]
        if istress is not None:
            if self.stress[istress].name is not None:
                h.name = h.name + ' (' + self.stress[istress].name + ')'
        # see whether it makes a difference to subtract gain * mean_stress
        # h -= self.rfunc.gain(p) * stress.mean()
        return h

    def get_stress(self, p=None, istress=None):
        if istress is None:
            return self.stress[0].add(p[-1] * self.stress[1])
        elif istress == 0:
            return self.stress[0]
        else:
            return p[-1] * self.stress[1]

    def dump(self, series=True, transformed_series=False):
        """Method to export the StressModel object.

        Returns
        -------
        data: dict
            dictionary with all necessary information to reconstruct the
            StressModel object.

        """
        data = dict()
        data["stressmodel"] = self._name
        data["rfunc"] = self.rfunc._name
        data["name"] = self.name
        data["up"] = True if self.rfunc.up == 1 else False
        data["cutoff"] = self.rfunc.cutoff
        data["stress"] = self.dump_stress(series,
                                          transformed_series=transformed_series)

        return data


class StepModel(StressModelBase):
    """Stressmodel that simulates a step trend.

    A stress consisting of a step resonse from a specified time. The
    amplitude and form (if rfunc is not One) of the step is calibrated. Before
    t_step the response is zero.

    """
    _name = "StepModel"

    def __init__(self, start, name, rfunc=One, up=True):
        StressModelBase.__init__(self, rfunc, name, pd.Timestamp.min,
                                 pd.Timestamp.max, up, 1.0, None)
        self.t_step = start
        self.set_init_parameters()

    def set_init_parameters(self):
        self.parameters = self.rfunc.set_parameters(self.name)
        tmin = pd.Timestamp.min.toordinal()
        tmax = pd.Timestamp.max.toordinal()

        self.parameters.loc['start'] = (
            self.t_step.value, tmin, tmax,
            0, self.name)
        self.nparam += 1

    def simulate(self, p, tindex=None, dt=1):
        assert tindex is not None, 'Error: Need an index'
        h = pd.Series(0, tindex, name=self.name)
        td = tindex - pd.Timestamp(p[-1])
        h[td.days > 0] = self.rfunc.step(p[:-1], td[td.days > 0].days)
        return h


class LinearTrend(StressModelBase):
    """Stressmodel that simulated a linear trend.

    name: str
        String with the name of the stressmodel
    start: str
        String with a date to start the trend, will be transformed to an
        ordinal number internally. E.g. "2018-01-01"
    end: str
        String with a date to end the trend, will be transformed to an ordinal
        number internally. E.g. "2018-01-01"

    """
    _name = "LinearTrend"

    def __init__(self, name="linear_trend", start=0, end=0):
        StressModelBase.__init__(self, One, name, pd.Timestamp.min,
                                 pd.Timestamp.max, 1, 0, 0)
        self.nparam = 3
        self.set_init_parameters(start, end)

    def set_init_parameters(self, start, end):
        start = pd.Timestamp(start).toordinal()
        end = pd.Timestamp(end).toordinal()
        tmin = pd.Timestamp.min.toordinal()
        tmax = pd.Timestamp.max.toordinal()

        self.parameters.loc[self.name + "_a"] = (
            0, -np.inf, np.inf, 1, self.name)
        self.parameters.loc[self.name + "_tstart"] = (
            start, tmin, tmax, 1, self.name)
        self.parameters.loc[self.name + "_tend"] = (
            end, tmin, tmax, 1, self.name)

    def simulate(self, p, tindex, dt=1):
        if tindex is None:
            logger.error("A time index has to be provided to simulate this "
                         "stressmodel")

        if p[1] < tindex[0].toordinal():
            tmin = tindex[0]
        else:
            tmin = pd.Timestamp.fromordinal(int(p[1]))

        if p[2] >= tindex[-1].toordinal():
            tmax = tindex[-1]
        else:
            tmax = pd.Timestamp.fromordinal(int(p[2]))

        trend = tindex.to_series().diff() / pd.Timedelta(1, "D")
        trend.loc[:tmin] = 0
        trend.loc[tmax:] = 0
        trend = trend.cumsum() * p[0]
        return trend


class NoConvModel(StressModelBase):
    """Time series model consisting of the calculation of one stress
     with one response function, without the use of convolution (so it is much
     slower). The advantage is that you do not have to interpolate the
     simulation to the observation timesteps, because you calculate the
     simulation at the exact moment of the observations. This StressModel works
     well for models with short observation-series and/or short stress series.

    Parameters
    ----------
    stress: pandas.Series
        pandas Series object containing the stress.
    rfunc: pastas.rfunc
        Response function used in the convolution with the stess.
    name: str
        Name of the stress
    metadata: dict, optional
        dictionary containing metadata about the stress.
    xy: tuple, optional
        XY location in lon-lat format used for making maps.
    freq: str, optional
        Frequency to which the stress series are transformed. By default,
        the frequency is inferred from the data and that frequency is used.
        The required string format is found
        at http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
    fillnan: str or float, optional
        Methods or float number to fill nan-values. Default values is
        'mean'. Currently supported options are: 'interpolate', float,
        and 'mean'. Interpolation is performed with a standard linear
        interpolation.

    """
    _name = "NoConvModel"

    def __init__(self, stress, rfunc, name, metadata=None, up=True,
                 cutoff=0.99, settings=None, **kwargs):

        kind = kwargs.pop("kind", None)

        stress = TimeSeries(stress, kind=kind, settings=settings,
                            metadata=metadata)
        StressModelBase.__init__(self, rfunc, name, stress.index.min(),
                                 stress.index.max(), up, stress.mean(), cutoff)
        self.freq = stress.settings["freq"]
        self.stress = [stress]
        self.set_init_parameters()

    def set_init_parameters(self):
        """Set the initial parameters (back) to their default values.

        """
        self.parameters = self.rfunc.set_parameters(self.name)

    def simulate(self, p, tindex=None, dt=None):
        """ Simulates the head contribution, without convolution.

        Parameters
        ----------
        p: array_like
           Parameters used for simulation.
        tindex: pandas.Series, optional
           Time indices to simulate the model.

        Returns
        -------
        pandas.Series
            The simulated head contribution.

        """

        # take the difference in values,
        # as we will calculate the step response
        stress = self.stress[0].diff()
        # set the index at the beginning of each period (it was at the end),
        # as we will calculate the step response from the start of the period
        stress = stress.shift(-1).dropna()
        # add a first value
        ind = self.stress[0].index
        stress = pd.concat((pd.Series(self.stress[0][0],
                                      index=[ind[0] - (ind[1] - ind[0])]),
                            stress))
        # remove steps that do not change
        stress = stress[~(stress == 0)]
        tmax = pd.to_timedelta(self.rfunc.calc_tmax(p), 'd')
        gain = self.rfunc.gain(p)
        values = np.zeros(len(tindex))
        if len(tindex) > len(stress):
            # loop over the stress-series
            for ind_str, val_str in stress.items():
                t = tindex - ind_str
                mask = (tindex > ind_str) & (t <= tmax)
                if np.any(mask):
                    td = np.array(t[mask].total_seconds() / 86400)
                    r = val_str * self.rfunc.step(p, np.array(td))
                    values[mask] += r
                mask = t > tmax
                if np.any(mask):
                    values[mask] += val_str * gain
        else:
            # loop over the observation-series
            for i, ind_obs in enumerate(tindex):
                t = ind_obs - stress.index
                mask = (ind_obs > stress.index) & (t <= tmax)
                if np.any(mask):
                    # calculate the step response
                    td = np.array(t[mask].total_seconds() / 86400)
                    values[i] += np.sum(stress[mask] * self.rfunc.step(p, td))
                mask = t > tmax
                if np.any(mask):
                    values[i] += np.sum(stress[mask] * gain)
            pass
        h = pd.Series(values, tindex, name=self.name)
        return h


class Constant(StressModelBase):
    """A constant value that is added to the time series model.

    Parameters
    ----------
    value : float, optional
        Initial estimate of the parameter value. E.g. The minimum of the
        observed series.

    """
    _name = "Constant"

    def __init__(self, name="constant", value=0.0, pmin=np.nan, pmax=np.nan):
        self.nparam = 1
        self.value = value
        self.pmin = pmin
        self.pmax = pmax
        StressModelBase.__init__(self, One, name, pd.Timestamp.min,
                                 pd.Timestamp.max, 1, 0, 0)
        self.set_init_parameters()

    def set_init_parameters(self):
        self.parameters.loc[self.name + "_d"] = (
            self.value, self.pmin, self.pmax, 1, self.name)

    def simulate(self, p=None):
        return p


class WellModel(StressModelBase):
    """Time series model consisting of the convolution of one or more
    stresses with one response function. The distance from an influence to
    the location of the oseries has to be provided for each

    Parameters
    ----------
    stress: pandas.DataFrame
        Pandas DataFrame object containing the stresses.
    rfunc: rfunc class
        Response function used in the convolution with the stresses.
    name: str
        Name of the stress

    Notes
    -----
    This class implements convolution of multiple series with a the same
    response function. This is often applied when dealing with multiple
    wells in a time series model.

    """
    _name = "WellModel"

    def __init__(self, stress, rfunc, name, radius, up=False, cutoff=0.99,
                 settings="well"):

        meanstress = 1.0  # ? this should be something logical

        tmin = pd.Timestamp.max
        tmax = pd.Timestamp.min

        StressModelBase.__init__(self, rfunc, name, tmin, tmax,
                                 up, meanstress, cutoff)

        if settings is None or isinstance(settings, str):
            settings = len(stress) * [None]

        self.stress = self.handle_stress(stress, settings)

        # Check if number of stresses and radii match
        if len(self.stress) != len(radius) and radius:
            logger.error("The number of stresses applied does not match the "
                         "number of radii provided.")
        else:
            self.radius = radius

        self.freq = self.stress[0].settings["freq"]

        self.set_init_parameters()

    def set_init_parameters(self):
        self.parameters = self.rfunc.set_parameters(self.name)

    def simulate(self, p=None, tindex=None, dt=1, istress=None):
        h = pd.Series(data=0, index=self.stress[0].index, name=self.name)
        stresses = self.get_stress(istress=istress)
        radii = self.get_radii(irad=istress)
        for stress, radius in zip(stresses, radii):
            npoints = stress.index.size
            # TODO Make response function that take the radius as input
            # b = self.rfunc.block(p, dt=dt, radius=radius)
            b = self.rfunc.block(p, dt)
            c = fftconvolve(stress, b, 'full')[:npoints]
            h = h.add(pd.Series(c, index=stress.index), fill_value=0.0)

        if tindex is not None:
            h = h[tindex]
        return h

    def get_stress(self, p=None, istress=None):
        if istress is None:
            return self.stress
        else:
            return [self.stress[istress]]

    def get_radii(self, irad=None):
        if irad is None:
            return self.radius
        else:
            return [self.radius[irad]]
