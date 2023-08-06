#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/4/18
"""
.. currentmodule:: base
.. moduleauthor:: Pat Daburu <pat@daburu.net>

The GeoAlchemy declarative base for the data model is defined in this module
along with some other helpful classes.
"""
from sqlalchemy.ext.declarative import declarative_base
from .geometry import GeometryTypes


Base = declarative_base()  #: This is the model's declarative base.  pylint: disable=invalid-name


class ModelMixin(object):
    """
    This mixin includes columns and methods common to objects within the
    data model.
    """
    __geoattr__ = 'geometry'  #: the name of the geometry column attribute

    @classmethod
    def geometry_type(cls) -> GeometryTypes:
        """
        Get the geometry type defined for the model class.

        :return: the geometry type

        .. note::

            The name of the geometry attribute must be 'geometry' to be properly
            identified.
        """
        try:
            # Get the string that identifies the geometry type.
            gt_str = cls.__table__.c[cls.__geoattr__].type.geometry_type
            # The string should correspond to one of the supported types.
            gtyp = GeometryTypes[gt_str]
            # Return that value.
            return gtyp
        except KeyError:
            return GeometryTypes.NONE
