import sys
sys.path.append("/app/share/api")

import unittest
from pymongo import ASCENDING, DESCENDING
from apiutils import *


class TestLimitFunction(unittest.TestCase):

    def test_no_limit(self):
        fail_response = "No limit param should return integer zero"
        data = {}
        self.assertEqual(get_limit(data), 0, fail_response)

    def test_invalid_limit(self):
        fail_response = "Invalid limit param should return integer zero"
        data = {'limit': 'mfcw34 '}
        self.assertEqual(get_limit(data), 0, fail_response)

    def test_valid_limit(self):
        fail_response = "Valid limit should return expected integer"
        data = {'limit': '100'}
        self.assertEqual(get_limit(data), 100, fail_response)


class TestOffsetFunction(unittest.TestCase):

    def test_no_offset(self):
        fail_response = "No offset param should return integer zero"
        data = {}
        self.assertEqual(get_offset(data), 0, fail_response)

    def test_invalid_offset(self):
        fail_response = "Invalid offset param should return integer zero"
        data = {'offset': '20ed '}
        self.assertEqual(get_offset(data), 0, fail_response)

    def test_valid_offset(self):
        fail_response = "Valid offset should return expected integer"
        data = {'offset': '20'}
        self.assertEqual(get_offset(data), 20, fail_response)


class TestSortFunction(unittest.TestCase):
    '''
        The sort function is responsible for converting a sort and
        sortorder request and returning either None or a list of
        (field, direction) tuples
    '''

    def test_no_sort(self):
        fail_response = "No sort param in request data should return None"
        data = {}
        self.assertIsNone(get_sort(data), fail_response)

    def test_empty_sort(self):
        fail_response = "Empty sort param in request data should return None"
        data = {'sort': ''}
        self.assertIsNone(get_sort(data), fail_response)

    def test_sort_only(self):
        fail_response = "Sort fields are not returned correctly"
        data = {'sort': 'field1,field2'}
        expected = [('field1', ASCENDING), ('field2', ASCENDING)]
        self.assertEqual(get_sort(data), expected, fail_response)

    def test_sort_and_direction(self):
        fail_response = "Sort fields and direction are not returned correctly"
        data = {'sort': 'field1,field2', 'sortorder': 'asc,desc'}
        expected = [('field1', ASCENDING), ('field2', DESCENDING)]
        self.assertEqual(get_sort(data), expected, fail_response)

    def test_invalid_direction(self):
        fail_response = "Invalid sortorder entries should be set to ASCENDING"
        data = {'sort': 'field1,field2', 'sortorder': 'desc,descjir'}
        expected = [('field1', DESCENDING), ('field2', ASCENDING)]
        self.assertEqual(get_sort(data), expected, fail_response)

    def test_additional_sortorder_entries(self):
        message = "Additional sortorder entries should be ignored"
        data = {'sort': 'field1,field2', 'sortorder': 'asc,desc,asc'}
        expected = [('field1', ASCENDING), ('field2', DESCENDING)]
        self.assertEqual(get_sort(data), expected, message)

    def test_undefined_sortorder_entries(self):
        message = "Undefined sortorder entries should be set to ASCENDING"
        data = {'sort': 'field1,field2', 'sortorder': 'desc'}
        expected = [('field1', DESCENDING), ('field2', ASCENDING)]
        self.assertEqual(get_sort(data), expected, message)

    def test_id_field_transform(self):
        message = "Sort field 'id' should be transformed to '_id'"
        data = {'sort': 'field1,id'}
        expected = [('field1', ASCENDING), ('_id', ASCENDING)]
        self.assertEqual(get_sort(data), expected, message)


class TestFieldsFunction(unittest.TestCase):

    def test_no_fields(self):
        message = "get_fields function should return None when no lists defined"
        self.assertEqual(get_fields(None, None), None, message)

    def test_display_fields(self):
        message = "display only get_fields function did not return correct dict"
        displayed_fields = ['field_1', 'field_2']
        expected = {'field_1': 1, 'field_2': 1}
        self.assertEqual(get_fields(displayed_fields, None), expected, message)

    def test_exclude_fields(self):
        message = "exclude only get_fields function did not return correct dict"
        excluded_fields = ['field_1', 'field_2']
        expected = {'field_1': 0, 'field_2': 0}
        self.assertEqual(get_fields(None, excluded_fields), expected, message)

    def test_combine_display_and_exclude_fields(self):
        message = "display and exclude get_fields function did not return correct dict"

        displayed_fields = ['field_1', 'field_2']
        excluded_fields = ['field_3', 'field_4']

        expected = {'field_1': 1, 'field_2': 1, 'field_3': 0, 'field_4': 0}
        output = get_fields(displayed_fields, excluded_fields)
        self.assertEqual(output, expected, message)


if __name__ == '__main__':
    unittest.main()
