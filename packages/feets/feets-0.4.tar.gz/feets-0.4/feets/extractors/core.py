#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2017 Juan Cabral

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals, print_function


# =============================================================================
# DOCS
# =============================================================================

__doc__ = """Features extractors base classes classes"""


# =============================================================================
# IMPORTS
# =============================================================================

import warnings
from collections import namedtuple

import six


# =============================================================================
# CONSTANTS
# =============================================================================

DATA_MAGNITUDE = "magnitude"
DATA_TIME = "time"
DATA_ERROR = "error"
DATA_MAGNITUDE2 = "magnitude2"
DATA_ALIGNED_MAGNITUDE = "aligned_magnitude"
DATA_ALIGNED_MAGNITUDE2 = "aligned_magnitude2"
DATA_ALIGNED_TIME = "aligned_time"
DATA_ALIGNED_ERROR = "aligned_error"
DATA_ALIGNED_ERROR2 = "aligned_error2"

DATAS = (
    DATA_TIME,
    DATA_MAGNITUDE,
    DATA_ERROR,
    DATA_MAGNITUDE2,
    DATA_ALIGNED_TIME,
    DATA_ALIGNED_MAGNITUDE,
    DATA_ALIGNED_MAGNITUDE2,
    DATA_ALIGNED_ERROR,
    DATA_ALIGNED_ERROR2
)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class ExtractorBadDefinedError(Exception):
    """The extractor are not properly defined."""
    pass


class ExtractorContractError(ValueError):
    """The extractor dont get the expected features, data, parameters
    or wathever.

    """
    pass


class ExtractorWarning(UserWarning):
    """Warn about the Extractor behavior."""
    pass


class FeatureExtractionWarning(UserWarning):
    """Warn about calculation of some feature"""
    pass


warnings.simplefilter("always", ExtractorWarning)
warnings.simplefilter("always", FeatureExtractionWarning)


# =============================================================================
# BASE CLASSES
# =============================================================================

ExtractorConf = namedtuple(
    "ExtractorConf",
    ["data", "dependencies", "params", "features", "warnings"])


class ExtractorMeta(type):

    def __new__(mcls, name, bases, namespace):
        cls = super(ExtractorMeta, mcls).__new__(mcls, name, bases, namespace)

        try:
            cls != Extractor
        except NameError:
            return cls

        if not hasattr(cls, "data"):
            msg = "'{}' must redefine {}"
            raise ExtractorBadDefinedError(
                msg.format(cls, "data attribute"))
        if not cls.data:
            msg = "'data' can't be empty"
            raise ExtractorBadDefinedError(msg)
        for d in cls.data:
            if d not in DATAS:
                msg = "'data' must be a iterable with values in {}. Found '{}'"
                raise ExtractorBadDefinedError(msg.format(DATAS, d))
        if len(set(cls.data)) != len(cls.data):
            msg = "'data' has duplicated values: {}"
            raise ExtractorBadDefinedError(msg.format(cls.data))

        if not hasattr(cls, "features"):
            msg = "'{}' must redefine {}"
            raise ExtractorBadDefinedError(
                msg.format(cls, "features attribute"))
        if not cls.features:
            msg = "'features' can't be empty"
            raise ExtractorBadDefinedError(msg)
        for f in cls.features:
            if not isinstance(f, six.string_types):
                msg = "Feature name must be an instance of string. Found {}"
                raise ExtractorBadDefinedError(msg.format(type(f)))
            if f in DATAS:
                msg = "Params can't be in {}".format(DATAS)
                raise ExtractorBadDefinedError(msg)

        if len(set(cls.features)) != len(cls.features):
            msg = "'features' has duplicated values: {}"
            raise ExtractorBadDefinedError(msg.format(cls.features))

        if cls.fit == Extractor.fit:
            msg = "'{}' must redefine {}"
            raise ExtractorBadDefinedError(msg.format(cls, "fit method"))

        if not hasattr(cls, "dependencies"):
            cls.dependencies = ()
        for d in cls.dependencies:
            if not isinstance(d, six.string_types):
                msg = (
                    "All Dependencies must be an instance of string. Found {}")
                raise ExtractorBadDefinedError(msg.format(type(d)))

        if not hasattr(cls, "params"):
            cls.params = {}
        for p, default in cls.params.items():
            if not isinstance(p, six.string_types):
                msg = "Params names must be an instance of string. Found {}"
                raise ExtractorBadDefinedError(msg.format(type(p)))
            if p in DATAS:
                msg = "Params can't be in {}".format(DATAS)
                raise ExtractorBadDefinedError(msg)

        if not hasattr(cls, "warnings"):
            cls.warnings = []

        cls._conf = ExtractorConf(
            data=frozenset(cls.data),
            dependencies=frozenset(cls.dependencies),
            params=tuple(cls.params.items()),
            features=frozenset(cls.features),
            warnings=tuple(cls.warnings))

        if not cls.__doc__:
            cls.__doc__ = ""
        cls.__doc__ += "\n" + "\n".join([
            ".. warning:: {}".format(w) for w in cls.warnings])

        del cls.data, cls.dependencies, cls.params, cls.features, cls.warnings

        return cls


@six.add_metaclass(ExtractorMeta)
class Extractor(object):

    _conf = None

    @classmethod
    def get_data(cls):
        return cls._conf.data

    @classmethod
    def get_dependencies(cls):
        return cls._conf.dependencies

    @classmethod
    def get_default_params(cls):
        return dict(cls._conf.params)

    @classmethod
    def get_features(cls):
        return cls._conf.features

    @classmethod
    def get_warnings(cls):
        return cls._conf.warnings

    @classmethod
    def has_warnings(cls):
        return not cls._conf.warnings

    def __init__(self, **cparams):
        for w in self.get_warnings():
            warnings.warn(w, ExtractorWarning)

        self.name = type(self).__name__

        self.params = self.get_default_params()
        set(cparams).difference(self.params)

        not_allowed = set(cparams).difference(self.params)
        if not_allowed:
            msg = "Extractor '{}' not allow the parameters: {}".format(
                type(self).__name__, ", ".join(not_allowed))
            raise ExtractorContractError(msg)

        # here all is ok
        self.params.update(cparams)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if not hasattr(self, "__str"):
            params = self.params
            if params:
                params = ", ".join([
                    "{}={}".format(k, v) for k, v in params.items()])
            else:
                params = ""
            self.__str = "{}({})".format(self.name, params)
        return self.__str

    def setup(self):
        """This method will be executed before the feature is calculated"""
        pass

    def fit(self):
        raise NotImplementedError()

    def teardown(self):
        """This method will be executed after the feature is calculated"""
        pass

    def extract(self, **kwargs):
        # create the besel for the parameters
        fit_kwargs = {}

        # add the required features as parameters to fit()
        dependencies = kwargs["features"]
        fit_kwargs = {k: dependencies[k] for k in self.get_dependencies()}

        # add the required data as parameters to fit()
        for d in self.get_data():
            fit_kwargs[d] = kwargs[d]

        # add the configured parameters as parameters to fit()
        fit_kwargs.update(self.params)
        try:
            # setup & run te extractor
            self.setup()
            result = self.fit(**fit_kwargs)

            # validate if the extractors generates the expected features
            expected = self.get_features()  # the expected features
            diff = (
                expected.difference(result.keys()) or
                set(result).difference(expected))  # some diff
            if diff:
                cls = type(self)
                estr, fstr = ", ".join(expected), ", ".join(result.keys())
                msg = (
                    "The extractor '{}' expect the features [{}], "
                    "and found: [{}]").format(cls, estr, fstr)
                raise ExtractorContractError(msg)
            return dict(result)
        finally:
            self.teardown()
