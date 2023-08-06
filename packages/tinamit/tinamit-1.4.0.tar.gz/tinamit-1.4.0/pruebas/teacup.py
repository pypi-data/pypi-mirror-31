"""
Python model "teacup.py"
Translated using PySD version 0.8.3
"""
from __future__ import division
import numpy as np
from pysd import utils
import xarray as xr

from pysd.py_backend.functions import cache
from pysd.py_backend import functions

_subscript_dict = {}

_namespace = {
    'TIME': 'time',
    'Time': 'time',
    'Characteristic Time': 'characteristic_time',
    'Heat Loss to Room': 'heat_loss_to_room',
    'Room Temperature': 'room_temperature',
    'Teacup Temperature': 'teacup_temperature',
    'FINAL TIME': 'final_time',
    'INITIAL TIME': 'initial_time',
    'SAVEPER': 'saveper',
    'TIME STEP': 'time_step'
}

__pysd_version__ = "0.8.3"


@cache('run')
def characteristic_time():
    """
    Characteristic Time

    Minutes [0.0, inf]

    constant

    How long will it take the teacup to cool 1/e of the way to equilibrium?
    """
    return 10


@cache('step')
def heat_loss_to_room():
    """
    Heat Loss to Room

    Degrees Fahrenheit/Minute [-inf, inf]

    component

    This is the rate at which heat flows from the cup into the room.
    """
    return (teacup_temperature() - room_temperature()) / characteristic_time()


@cache('run')
def room_temperature():
    """
    Room Temperature

    Degrees Fahrenheit [-459.67, inf]

    constant

    The room temperature cannot go below absolute zero.
    """
    return 70


@cache('step')
def teacup_temperature():
    """
    Teacup Temperature

    Degrees Fahrenheit [32.0, 212.0]

    component

    The model is only valid for the liquid phase of tea. While the tea could theoretically freeze or boil off, we would want an error to be thrown in these cases so that the modeler can identify the issue and decide whether to expand the model. Of course, this refers to standard sea-level conditions...
    """
    return integ_teacup_temperature()


@cache('run')
def final_time():
    """
    FINAL TIME

    Minute [nan, nan]

    constant

    The final time for the simulation.
    """
    return 30


@cache('run')
def initial_time():
    """
    INITIAL TIME

    Minute [nan, nan]

    constant

    The initial time for the simulation.
    """
    return 0


@cache('step')
def saveper():
    """
    SAVEPER

    Minute [0.0, inf]

    component

    The frequency with which output is stored.
    """
    return time_step()


@cache('run')
def time_step():
    """
    TIME STEP

    Minute [0.0, inf]

    constant

    The time step for the simulation.
    """
    return 0.125


integ_teacup_temperature = functions.Integ(lambda: -heat_loss_to_room(), lambda: 180)
