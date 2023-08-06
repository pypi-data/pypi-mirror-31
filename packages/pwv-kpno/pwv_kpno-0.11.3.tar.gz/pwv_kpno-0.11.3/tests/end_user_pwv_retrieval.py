#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the pwv_kpno software package.
#
#    The pwv_kpno package is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The pwv_kpno package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.

"""This file tests the functions "measured_pwv" and "modeled_pwv"."""

import unittest
from datetime import datetime

from astropy.table import Table
from pytz import utc

from pwv_kpno.pwv_atm import measured_pwv, modeled_pwv, pwv_date
from pwv_kpno._pwv_data import _check_date_time_args

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'


def _check_attrs(iterable, **kwargs):
    """Check the attribute values of objects in an iterable

    Iterate through the contents of a given iterable and check that all
    attribute values match those specified by **kwargs.

    Args:
        table    (Table): A table with a 'date' column
        **kwargs      (): datetime attributes and values

    Returns:
        True or False
    """

    assert len(kwargs), 'No attributes specified'
    for obj in iterable:
        for param_name, param_value in kwargs.items():
            if getattr(obj, param_name) != param_value:
                return False

    return True


class SearchArgumentErrors(unittest.TestCase):
    """Test that _check_search_args raises the appropriate errors

    _check_search_args is responsible for checking the arguments for both
    pwv_kpno.measured_pwv and pwv_kpno.modeled_pwv"""

    def test_checks_for_valid_year(self):
        """Test for correct errors due to bad year argument"""

        next_year = datetime.now().year + 1
        self.assertRaises(ValueError, _check_date_time_args, -2010)
        self.assertRaises(ValueError, _check_date_time_args, 2009)
        self.assertRaises(ValueError, _check_date_time_args, next_year)
        self.assertRaises(TypeError, _check_date_time_args, '2009')
        self.assertRaises(TypeError, _check_date_time_args, 2009.0)

    def test_checks_for_valid_month(self):
        """Test for correct errors due to bad month argument"""

        self.assertRaises(ValueError, _check_date_time_args, month=-3)
        self.assertRaises(ValueError, _check_date_time_args, month=0)
        self.assertRaises(ValueError, _check_date_time_args, month=13)
        self.assertRaises(TypeError, _check_date_time_args, month='12')
        self.assertRaises(TypeError, _check_date_time_args, month=12.0)

    def test_checks_for_valid_day(self):
        """Test for correct errors due to bad day argument"""

        self.assertRaises(ValueError, _check_date_time_args, day=-3)
        self.assertRaises(ValueError, _check_date_time_args, day=0)
        self.assertRaises(ValueError, _check_date_time_args, day=32)
        self.assertRaises(TypeError, _check_date_time_args, day='17')
        self.assertRaises(TypeError, _check_date_time_args, day=17.0)

    def test_checks_for_valid_hour(self):
        """Test for correct errors due to bad hour argument"""

        self.assertRaises(ValueError, _check_date_time_args, hour=-3)
        self.assertRaises(ValueError, _check_date_time_args, hour=24)
        self.assertRaises(ValueError, _check_date_time_args, hour=30)
        self.assertRaises(TypeError, _check_date_time_args, hour='12')
        self.assertRaises(TypeError, _check_date_time_args, hour=12.0)


class MeasuredPWV(unittest.TestCase):
    """Tests for the 'measured_pwv' function"""

    all_local_pwv_data = measured_pwv()

    def test_returned_tz_info(self):
        """Test if datetimes in the returned data are timezone aware"""

        tzinfo = self.all_local_pwv_data[0][0].tzinfo
        error_msg = 'Datetimes should be UTC aware (found "{}")'
        self.assertTrue(tzinfo == utc, error_msg.format(tzinfo))

    def test_returned_column_order(self):
        """Test the column order of the table returned by measured_pwv()

        The first two columns should be 'date' and 'KITT'
        """

        col_0 = self.all_local_pwv_data.colnames[0]
        col_1 = self.all_local_pwv_data.colnames[1]
        error_msg = 'column {} should be "{}", found "{}"'
        self.assertEqual(col_0, 'date', error_msg.format(0, 'date', col_0))
        self.assertEqual(col_1, 'KITT', error_msg.format(1, 'KITT', col_1))

    def test_filtering_by_args(self):
        """Test if results are correctly filtered by kwarg arguments"""

        test_cases = [{'year': 2010}, {'month': 7}, {'day': 21}, {'hour': 5},
                      {'year': 2011, 'month': 4, 'day': 30, 'hour': 21}]

        error_msg = 'measured_pwv returned incorrect dates. kwargs: {}'
        for kwargs in test_cases:
            attr_check = _check_attrs(measured_pwv(**kwargs)['date'], **kwargs)
            self.assertTrue(attr_check, error_msg.format(kwargs))

    def test_units(self):
        """Test columns for appropriate units"""

        for column in self.all_local_pwv_data.itercols():
            if column.name == 'date':
                self.assertEqual(column.unit, 'UTC')

            else:
                self.assertEqual(column.unit, 'mm')

    def test_removed_bad_kitt_data(self):
        """Test for the removal of Kitt Peak data from jan through mar 2016"""

        data_2016 = measured_pwv(2016)
        april_2016 = datetime(2016, 4, 1, tzinfo=utc)
        bad_data = data_2016[data_2016['date'] < april_2016]
        self.assertTrue(all(bad_data['KITT'].mask))


class ModeledPWV(unittest.TestCase):
    """Tests for the 'modeled_pwv' function"""

    kitt_peak_pwv_model = modeled_pwv()

    def test_returned_tz_info(self):
        """Test if datetimes in the returned data are timezone aware"""

        tzinfo = self.kitt_peak_pwv_model[0][0].tzinfo
        error_msg = 'Datetimes should be UTC aware (found "{}")'
        self.assertTrue(tzinfo == utc, error_msg.format(tzinfo))

    def test_units(self):
        """Test columns for appropriate units"""

        error_msg = 'Wrong units for column {}. Found ({})'
        date_unit = self.kitt_peak_pwv_model['date'].unit
        pwv_unit = self.kitt_peak_pwv_model['pwv'].unit

        self.assertEqual(date_unit, 'UTC', error_msg.format('date', date_unit))
        self.assertEqual(pwv_unit, 'mm', error_msg.format('pwv', pwv_unit))


class PwvDate(unittest.TestCase):
    """Tests for the pwv_date function"""

    kitt_peak_pwv_model = modeled_pwv()

    def test_known_dates(self):
        """Tests that pwv_date"""

        test_date_0 = self.kitt_peak_pwv_model['date'][0]
        test_pwv_0 = self.kitt_peak_pwv_model['pwv'][0]
        test_date_100 = self.kitt_peak_pwv_model['date'][100]
        test_pwv_100 = self.kitt_peak_pwv_model['pwv'][100]

        error_msg = "pwv_date returned incorrect PWV value for tabulated date"
        self.assertEqual(test_pwv_0, pwv_date(test_date_0), error_msg)
        self.assertEqual(test_pwv_100, pwv_date(test_date_100), error_msg)
