import unittest
import sys

sys.path.append('/app/share/python/site-packages')
from ni.network_traffic.snapshot import NetworkTrafficSnapshot

large_snapshot = {
    'title': 'Test snapshot 1',
    'desc': 'This is the first test snapshot',
    'path': 'test_snapshots/diagnostic_test_log_1.txt',
    'start': '2012-12-11T03:06:30.594000',
    'end': '2012-12-11T03:07:24.987000',
    'total_messages': 227,
    'creation_method': 'upload',
    'messages': [
        {
            'index': 11,
            'protocol': 'SIP',
            'status_code': 'None',
            "source": "cisco tvcs",
            "destination": "cisco tvcs",
            "destination_port": "22416",
            "version": "2.0",
            "method": "INFO",
            'headers': [],
            'total_headers': 13,
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
 <SearchParameters>
   <searchString>ca</searchString>
   <returnFields>DisplayName,ContactMethodGroups</returnFields>
   <groupId></groupId>
   <maxResultSize>10</maxResultSize>
   <offset>0</offset>
 </SearchParameters>'''
        }
    ]
}

small_snapshot = {
    'title': 'Snapshot 2',
    'desc': '',
    'path': 'test_snapshots/diagnostic_test_log_2.txt',
    'start': '2012-12-11T03:06:32.284000',
    'end': '2012-12-11T03:07:24.987000',
    'total_messages': 25,
    'creation_method': 'upload'
}

'''
    Mainly interested in the start/end dates and total_messages
'''
single_message_test = {
    'title': 'Single network message snapshot',
    'desc': 'Test a logfile that contains one network message',
    'path': 'test_snapshots/single_network_message_logfile.txt',
    'start': '2012-12-11T03:07:02.237000',
    'end': '2012-12-11T03:07:02.237000',
    'total_messages': 1
}

'''
    Test that the correct data is extracted when no messages are within the log file
'''
no_messages_test = {
    'title': 'No network messages snapshot',
    'desc': 'Test a logfile that contains no network messages',
    'path': 'test_snapshots/no_network_message_logfile.txt',
    'start': '',
    'end': '',
    'total_messages': 0
}

'''
    When a message is received it is often sent to an internal component.
    In this case the message will be logged twice.

    Tests that the message is only output once and the message been merged.
    Interested in the correct sender, receiver, destination_port and source_port fields.

    In some cases the sent or received logged message will be unavailable as
    it was not recorded during the log, check that the message is logged correctly in
    this case.
'''
internal_messages_test = {
    'title': 'Internal messages snapshot',
    'desc': 'Test that internal messages are handled correctly',
    'path': 'test_snapshots/internal_messages_logfile.txt',
    'start': '2012-12-11T03:02:01.760000',
    'end': '2012-12-11T03:07:02.238000',
    'total_messages': 3,
    'messages': [
        {
            'index': 0,
            'source': 'cisco tvcs',
            'destination': 'cisco tvcs',
            'source_port': '2664',
            'destination_port': ''
        }, {
            'index': 1,
            'source': 'cisco tvcs',
            'destination': 'cisco tvcs',
            'destination_port': '10',
            'source_port': '22416'
        }, {
            'index': 2,
            'source': 'cisco tvcs',
            'destination': 'cisco tvcs',
            'source_port': '',
            'destination_port': '25000'
        }
    ]
}


class TestNetworkTrafficSnapshot(unittest.TestCase):
    '''
        Test the Network traffic snapshot class using test diagnostics log files
        that are located in ./testsnapshots/
    '''
    snapshots = []
    snapshot_data = []

    # Setup functions
    @classmethod
    def setUpClass(cls):
        '''
            Initiate the test data to use throughout all Tests
        '''
        cls.snapshot_data = [large_snapshot, small_snapshot, single_message_test,
                             no_messages_test, internal_messages_test]

        # Create a new snaphot object for all test data
        for snapshot in cls.snapshot_data:
            s = NetworkTrafficSnapshot()

            # Use upload method to extract data from the test log files
            content = TestNetworkTrafficSnapshot._get_snapshot_content(snapshot['path'])
            s.upload(snapshot['title'], snapshot['desc'], snapshot['path'], content)

            # Store the snapshot for use within the tests
            cls.snapshots.append(s)

    @classmethod
    def _get_snapshot_content(cls, path):
        # Read the log file and return the contents
        with open(path) as f:
            return f.read()

    def test_snapshot_data(self):
        test_data = ['title', 'desc', 'start', 'end', 'method_created']

        # If these fields are provided in the test data
        # assert that the same value is extracted from logfile
        for data, snapshot in zip(self.snapshot_data, self.snapshots):
            for field in test_data:
                if field in data:
                    message = 'Snapshot "' + snapshot.data['title'] + ' ' + field + ' not parsed correctly. Expected=' + str(data[field]) + ' Actual=' + str(snapshot.data[field])
                    self.assertEqual(snapshot.data[field], data[field], message)

    '''def test_total_messages(self):
        for index, snapshot in enumerate(self.snapshots):
            message = 'Snapshot ' + str(index) + ' total messages is incorrect'
            self.assertEqual(len(snapshot.messages), snapshot.data['statistics']['total_messages'], message)'''

    def test_snapshot_messages(self):
        # A form of integration test. Ensure that the correct message info is extracted if defined
        # in the test data
        header_fields = ['protocol', 'status', 'content', 'method',
                         'version', 'sender', 'receiver', 'destination_port', 'source_port']

        for data, snapshot in zip(self.snapshot_data, self.snapshots):
            if 'messages' in data:
                for message in data['messages']:
                    actual_message = snapshot.messages[message['index']]

                    # Test that each of the fields specified match
                    for field in header_fields:
                        if field in message:
                            self.assertEqual(message[field], actual_message.data[field])

if __name__ == '__main__':
    unittest.main()
