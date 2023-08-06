# -*- coding: utf-8 -*-
#pylint: disable=invalid-name

"""Copyright 2015 Roger R Labbe Jr.

FilterPy library.
http://github.com/rlabbe/filterpy

Documentation at:
https://filterpy.readthedocs.org

Supporting book at:
https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python

This is licensed under an MIT license. See the readme.MD file
for more information.
"""


from __future__ import print_function
from collections import defaultdict
import copy
from itertools import repeat
import numpy as np


class Saver(object):
    """
    Helper class to save the states of any filter object.
    Each time you call save() all of the attributes (state, covariances, etc)
    are appended to lists.

    Generally you would do this once per epoch - predict/update.

    Then, you can access any of the states by using the [] syntax or by
    using the . operator.

    .. code-block:: Python

        my_saver = Saver()
        ... do some filtering

        x = my_saver['x']
        x = my_save.x

    Either returns a list of all of the state `x` values for the entire
    filtering process.

    If you want to convert all saved lists into numpy arrays, call to_array().


    Parameters
    ----------

    kf : object
        any object with a __dict__ attribute, but intended to be one of the
        filtering classes

    save_current : bool, default=True
        save the current state of `kf` when the object is created;

    skip_private: bool, default=False
        Control skipping any private attribute (anything starting with '_')
        Turning this on saves memory, but slows down execution a bit.

    skip_callable: bool, default=False
        Control skipping any attribute which is a method. Turning this on
        saves memory, but slows down execution a bit.

    ignore: (str,) tuple of strings
        list of keys to ignore.

    Examples
    --------

    .. code-block:: Python

        kf = KalmanFilter(...whatever)
        # initialize kf here

        saver = Saver(kf) # save data for kf filter
        for z in zs:
            kf.predict()
            kf.update(z)
            saver.save()

        x = np.array(s.x) # get the kf.x state in an np.array
        plt.plot(x[:, 0], x[:, 2])

        # ... or ...
        s.to_array()
        plt.plot(s.x[:, 0], s.x[:, 2])

    """

    def __init__(self, kf, save_current=False,
                 skip_private=False,
                 skip_callable=False,
                 ignore=()):
        """ Construct the save object, optionally saving the current
        state of the filter"""
        #pylint: disable=too-many-arguments

        self._kf = kf
        self._DL = defaultdict(list)
        self._skip_private = skip_private
        self._skip_callable = skip_callable
        self._ignore = ignore
        self._len = 0

        if save_current:
            self.save()


    def save(self):
        """ save the current state of the Kalman filter"""

        kf = self._kf
        v = copy.deepcopy(kf.__dict__)

        if self._skip_private:
            for key in list(v.keys()):
                if key.startswith('_'):
                    print('deleting', key)
                    del v[key]

        if self._skip_callable:
            for key in list(v.keys()):
                if callable(v[key]):
                    del v[key]

        for ig in self._ignore:
            if ig in v:
                del v[ig]

        for key in list(v.keys()):
            self._DL[key].append(v[key])

        self.__dict__.update(self._DL)
        self._len += 1


    def __getitem__(self, key):
        return self._DL[key]


    def __len__(self):
        return self._len


    @property
    def keys(self):
        """ list of all keys"""
        return list(self._DL.keys())


    def to_array(self):
        """
        Convert all saved attributes from a list to np.array.

        This may or may not work - every saved attribute must have the
        same shape for every instance. i.e., if `K` changes shape due to `z`
        changing shape then the call will raise an exception.

        This can also happen if the default initialization in __init__ gives
        the variable a different shape then it becomes after a predict/update
        cycle.
        """
        for key in self.keys:
            try:
                self.__dict__[key] = np.array(self._DL[key])
            except:
                # get back to lists so we are in a valid state
                self.__dict__.update(self._DL)

                raise ValueError("could not convert {} into np.array".format(key))


def runge_kutta4(y, x, dx, f):
    """computes 4th order Runge-Kutta for dy/dx.

    Parameters
    ----------

    y : scalar
        Initial/current value for y
    x : scalar
        Initial/current value for x
    dx : scalar
        difference in x (e.g. the time step)
    f : ufunc(y,x)
        Callable function (y, x) that you supply to compute dy/dx for
        the specified values.

    """

    k1 = dx * f(y, x)
    k2 = dx * f(y + 0.5*k1, x + 0.5*dx)
    k3 = dx * f(y + 0.5*k2, x + 0.5*dx)
    k4 = dx * f(y + k3, x + dx)

    return y + (k1 + 2*k2 + 2*k3 + k4) / 6.


def pretty_str(label, arr):
    """
    Generates a pretty printed NumPy array with an assignment. Optionally
    transposes column vectors so they are drawn on one line. Strictly speaking
    arr can be any time convertible by `str(arr)`, but the output may not
    be what you want if the type of the variable is not a scalar or an
    ndarray.

    Examples
    --------
    >>> pprint('cov', np.array([[4., .1], [.1, 5]]))
    cov = [[4.  0.1]
           [0.1 5. ]]

    >>> print(pretty_str('x', np.array([[1], [2], [3]])))
    x = [[1 2 3]].T
    """

    def is_col(a):
        """ return true if a is a column vector"""
        try:
            return a.shape[0] > 1 and a.shape[1] == 1
        except (AttributeError, IndexError):
            return False

    transposed = False
    if is_col(arr):
        arr = arr.T
        transposed = True

    rows = str(arr).split('\n')
    if not rows:
        return ''

    if label is None:
        label = ''

    if label:
        label += ' = '

    s = label + rows[0]
    if transposed:
        s += '.T'
        return s

    pad = ' ' * len(label)

    for line in rows[1:]:
        s = s + '\n' + pad + line

    return s


def pprint(label, arr, **kwargs):
    """ pretty prints an NumPy array using the function pretty_str. Keyword
    arguments are passed to the print() function.

    See Also
    --------
    pretty_str

    Examples
    --------
    >>> pprint('cov', np.array([[4., .1], [.1, 5]]))
    cov = [[4.  0.1]
           [0.1 5. ]]
    """

    print(pretty_str(label, arr), **kwargs)


def reshape_z(z, dim_z, ndim):
    """ ensure z is a (dim_z, 1) shaped vector"""

    z = np.atleast_2d(z)
    if z.shape[1] == dim_z:
        z = z.T

    if z.shape != (dim_z, 1):
        raise ValueError('z must be convertible to shape ({}, 1)'.format(dim_z))

    if ndim == 1:
        z = z[:, 0]

    if ndim == 0:
        z = z[0, 0]

    return z


def repeated_array(val, N):
    """ User can specify either a single value, or a list/array of N values.
    If a single value, create an iterable list to return that value
    repeatedly.
    """

    shape = np.shape(val)
    if len(shape) > 1 and shape[0] == N:
            return val

    return repeat(val, N)
