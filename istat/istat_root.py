# -*- coding: utf-8 -*-
# This file is part of https://github.com/26fe/jsonstat.py
# Copyright (C) 2016 gf <gf@26fe.com>
# See LICENSE file

# stdlib
from __future__ import print_function
from __future__ import unicode_literals
import sys

# istat
from istat.istat_helper import IstatHelper
from istat.istat_area import IstatArea


class IstatRoot:
    """
    Represent the root of all Istat dataseries
    """

    def __init__(self, cache_dir="./istat_cached", time_to_live = None, lang=1):
        """
        Initialize Istat class.
        :param cache_dir: where to store the cached file
        :param lang: 1=english, otherwise italian
        """
        self.__istat_helper = IstatHelper(cache_dir, time_to_live, lang)
        self.__id2area = None
        self.__cod2area = None
        self.__desc2area = None

    def cache_dir(self):
        return self.__istat_helper.cache_dir()

    def areas(self):
        """Get a list of all areas

        :return: list of IstatArea instances
        """
        if self.__id2area is None:
            self.__download_areas()
        return self.__id2area.values()

    def areas_as_html(self):
        """returns html string useful to be showed into ipython notebooks"""
        if self.__id2area is None:
            self.__download_areas()

        # todo: using __repr__html?
        html = "<table>"
        html += "<tr><th>id</th><th>desc</th></tr>"
        for iid, area in sorted(self.__id2area.items()):
            html += "<tr>"
            html += "<td>{}</td>".format(iid)
            html += "<td>{}</td>".format(area.desc())
            html += "</td>"
            html += "</tr>"
        html += "</table>"
        return html

    def area(self, spec):
        """Get a IstatArea by name or id

        :param spec: can be a string (for code or desc) or an int (for id)
        :return: a IstatArea istance
        """
        if self.__id2area is None:
            self.__download_areas()
        if type(spec) is str:
            if spec in self.__cod2area: return self.__cod2area[spec]
            if spec in self.__desc2area: return self.__desc2area[spec]
        # python2 has also 'unicode' string type other than native string 'str' type
        elif sys.version_info < (3,) and type(spec) is unicode:
            if spec in self.__cod2area: return self.__cod2area[spec]
            if spec in self.__desc2area: return self.__desc2area[spec]
        else:
            spec = int(spec) # try to convert into int
            return self.__id2area[spec]

    def dataset(self, spec_area, spec_dataset):
        """Returns an IstatDataset

        :param spec_area: selector for an IstatArea
        :param spec_dataset: selector for an IstatDataset that belong to the spec_area dataset
        :return: an instance of IstatDataset
        """
        a = self.area(spec_area)
        ds = a.dataset(spec_dataset)
        return ds

    def __download_areas(self):
        self.__id2area = {}
        self.__cod2area = {}
        self.__desc2area = {}
        json_data = self.__istat_helper.area(False)
        for area in json_data:
            iid = int(area['Id'])  # try to convert into int
            cod = area['Cod']
            desc = area['Desc']
            if iid in self.__id2area:
                continue
            istat_area = IstatArea(self.__istat_helper, iid, cod, desc)
            self.__id2area[iid] = istat_area
            self.__cod2area[cod] = istat_area
            self.__desc2area[desc] = istat_area


