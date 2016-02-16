# -*- coding: utf-8 -*-
# This file is part of https://github.com/26fe/jsonstat.py
# Copyright (C) 2016 gf <gf@26fe.com>
# See LICENSE file

# stdlib
from __future__ import print_function
from __future__ import unicode_literals
import unittest
import os

# jsonstat
import jsonstat


class TestDataSet(unittest.TestCase):
    def setUp(self):
        self.fixture_collection_dir = os.path.join(os.path.dirname(__file__), "fixtures", "collection")
        self.fixture_dataset_dir = os.path.join(os.path.dirname(__file__), "fixtures", "dataset")

        self.json_missing_value = '''
        {
            "label" : "three dimensions"
        }
        '''

        self.json_empty_value = '''
        {
            "label" : "three dimensions",
            "value" : []
        }
        '''

        self.json_missing_dimension = '''
        {
            "label" : "three dimensions",
            "value" : [1,2]
        }
        '''

        self.json_incorrect_data_size = '''
        {
            "label" : "Unemployment rate in the OECD countries 2003-2014",
            "source" : "Economic Outlook No 92 - December 2012 - OECD Annual Projections",
            "value" : [1, 2, 3, 4],
            "dimension" : {
                "id" : ["area", "year"],
                "size" : [4, 12],
                "area" : {
                    "category" : { "index" : { "AU" : 0, "AT" : 1, "BE" : 2, "CA" : 3 } }
                },
                "year" : {
                    "category" : {
                        "index" : {
                            "2003" : 0, "2004" : 1, "2005" : 2, "2006" : 3, "2007" : 4,
                            "2008" : 5, "2009" : 6,
                            "2010" : 7, "2011" : 8, "2012" : 9, "2013" : 10, "2014" : 11
                        }
                    }
                }
            }
        }
        '''

    def test_exception_not_valid(self):
        dataset = jsonstat.JsonStatDataSet("canada")
        with self.assertRaises(jsonstat.JsonStatException):
            dataset.value(year="2003", area="CA")

    def test_empty_value(self):
        dataset = jsonstat.JsonStatDataSet("canada")
        with self.assertRaises(jsonstat.JsonStatMalformedJson) as cm:
            dataset.from_string(self.json_empty_value)
        e = cm.exception
        expected = "dataset 'canada': field 'value' is empty"
        self.assertEqual(expected, e.value)

    def test_missing_value_field(self):
        dataset = jsonstat.JsonStatDataSet("canada")
        with self.assertRaises(jsonstat.JsonStatMalformedJson) as cm:
            dataset.from_string(self.json_missing_value)
        e = cm.exception
        expected = "dataset 'canada': missing 'value' key"
        self.assertEqual(expected, e.value)

    def test_missing_dimension(self):
        dataset = jsonstat.JsonStatDataSet("canada")
        with self.assertRaises(jsonstat.JsonStatMalformedJson) as cm:
            dataset.from_string(self.json_missing_dimension)
        e = cm.exception
        expected = "dataset 'canada': missing 'dimension' key"
        self.assertEqual(expected, e.value)

    def test_exception_dataset_size(self):
        dataset = jsonstat.JsonStatDataSet("canada")
        with self.assertRaises(jsonstat.JsonStatException) as cm:
            dataset.from_string(self.json_incorrect_data_size)
        e = cm.exception
        # expected e il primo valore dell'assert (giusto per ricordare!)
        expected = "dataset 'canada': size 4 is different from calculate size 48 by dimension"
        self.assertEqual(expected, e.value)

    def test_name(self):
        dataset = jsonstat.JsonStatDataSet("canada")
        self.assertEqual(dataset.name(), "canada")

    def test_dimensions(self):
        json_pathname = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathname)

        self.assertEqual(len(dataset.dimensions()), 2)

    def test_exception_no_existent_dimension(self):
        json_pathname = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathname)

        self.assertEqual(dataset.dimension("year").name(), "year")
        with self.assertRaises(jsonstat.JsonStatException) as cm:
            dataset.dimension("not existent dim")
        e = cm.exception
        expected = "dataset 'canada': unknown dimension 'not existent dim' know dimensions ids are: year, area"
        self.assertEqual(expected, e.value)

    def test_info(self):
        json_pathname = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathname)

        expected =(
            "name:   'canada'\n"
            "label:  'Unemployment rate in the OECD countries'\n"
            "source: 'Unemployment rate in the OECD countries'\n"
            "size: 12\n"
            "2 dimensions:\n"
            "  0: dim id: 'year' label: '2003-2014' size: '3' role: 'time'\n"
            "  1: dim id: 'area' label: 'OECD countries, EU15 and total' size: '4' role: 'geo'\n"
        )
        self.assertEqual(expected, dataset.__str__())

    #
    # test dataset.value()
    #
    def test_value(self):
        json_pathname = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathname)

        self.assertEqual(dataset.value(area="AU", year="2012"), 11)
        # using label Australia insted of index AU
        self.assertEqual(dataset.value(area="Australia", year="2012"), 11)

        # using dictionary
        self.assertEqual(dataset.value({'area':"Australia", 'year':"2012"}), 11)
        self.assertEqual(dataset.value({'area':"AU", 'year':"2012"}), 11)
        self.assertEqual(dataset.value({"OECD countries, EU15 and total":"AU", 'year':'2012'}), 11)

        self.assertEqual(dataset.value(area="BE", year="2014"), 33)

    def test_value2(self):
        json_pathname = os.path.join(self.fixture_dataset_dir, "json_three_dimensions.json")
        dataset = jsonstat.JsonStatDataSet()
        dataset.from_file(json_pathname)

        self.assertEqual(dataset.value(one="one_1", two="two_1", three="three_1"), 111)
        v = dataset.value(one="one_2", two="two_2", three="three_2")
        self.assertEqual(v, 222)

    def test_value_oecd(self):
        json_pathname = os.path.join(self.fixture_collection_dir, "oecd-canada.json")
        collection = jsonstat.JsonStatCollection()
        collection.from_file(json_pathname)

        oecd = collection.dataset('oecd')
        v = oecd.value(concept='UNR',area='AU',year='2004')
        self.assertEqual(5.39663128, v)

    #
    # test from functions
    #

    def test_from_vec_idx_to_vec_dim(self):
        json_pathfile = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathfile)

        ret = dataset.from_vec_idx_to_vec_dim(["area", "year"])
        self.assertEqual([1,0], ret)

        ret = dataset.from_vec_idx_to_vec_dim(["year", "area"])
        self.assertEqual([0,1], ret)

    #
    # enumeration function
    # all_pos test
    #

    def test_all_pos(self):
        json_pathfile = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathfile)

        result = list(dataset.all_pos())
        expected = [[0, 0], [0, 1], [0, 2], [0, 3], # first digit 0
                    [1, 0], [1, 1], [1, 2], [1, 3], # first digit 1
                    [2, 0], [2, 1], [2, 2], [2, 3]] # first digit 2
        self.assertEqual(result, expected)

    def test_all_pos_reorder(self):
        json_pathfile = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathfile)

        reorder = dataset.from_vec_idx_to_vec_dim(["area", "year"])
        result = list(dataset.all_pos(order=reorder))
        expected = [[0, 0], [1, 0], [2, 0],  # last digit 0
                    [0, 1], [1, 1], [2, 1],  # last digit 1
                    [0, 2], [1, 2], [2, 2],  # last digit 2
                    [0, 3], [1, 3], [2, 3]]  # last digit 3
        self.assertEqual(result, expected)

    def test_all_pos_with_block(self):
        json_pathfile = os.path.join(self.fixture_dataset_dir, "json_dataset_unemployment.json")
        dataset = jsonstat.JsonStatDataSet("canada")
        dataset.from_file(json_pathfile)

        result = list(dataset.all_pos({"area": "IT"}))
        expected = [[0, 3], [1, 3], [2, 3]]
        self.assertEqual(result, expected)

        dataset.generate_all_vec(area="IT")

        result = list(dataset.all_pos({"year": "2014"}))
        expected = [[2, 0], [2, 1], [2, 2], [2, 3]]
        self.assertEqual(result, expected)

        dataset.generate_all_vec(year='2014')

    def test_all_pos_with_three_dim(self):
        json_pathfile = os.path.join(self.fixture_dataset_dir, "json_three_dimensions.json")
        dataset = jsonstat.JsonStatDataSet()
        dataset.from_file(json_pathfile)

        # test 1
        result = list(dataset.all_pos({'one':'one_1'}))
        expected = [
            [0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 0, 3],
            [0, 1, 0], [0, 1, 1], [0, 1, 2], [0, 1, 3],
            [0, 2, 0], [0, 2, 1], [0, 2, 2], [0, 2, 3]]

        self.assertEqual(result, expected)

        # test 2
        dataset.generate_all_vec(one='one_1')
        result = list(dataset.all_pos({"two":"two_2"}))
        expected = [
            [0, 1, 0], [0, 1, 1], [0, 1, 2], [0, 1, 3],
            [1, 1, 0], [1, 1, 1], [1, 1, 2], [1, 1, 3]
        ]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
