import unittest
import sys

sys.path.append('/app/share/python/site-packages')
from ni.network_traffic.snapshot import NetworkTrafficSnapshot

large_snapshot = {
    'title': 'Test snapshot 1',
    'desc': 'This is the first test snapshot',
    'path': 'test_snapshots/diagnostic_test_log_1.txt',
    'start': '2012-12-11 03:06:30,594',
    'end': '2012-12-11 03:07:24,987',
    'total_messages': 260,
    'creation_method': 'upload',
    'messages': [
        {
            'index': 11,
            'protocol': 'SIP',
            'status_code': '',
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
    'start': '2012-12-11 03:06:32,284',
    'end': '2012-12-11 03:07:24,987',
    'total_messages': 27,
    'creation_method': 'upload'
}

single_message_test = {
    'title': 'Single network message snapshot',
    'desc': 'Test a logfile that contains one network message',
    'path': 'test_snapshots/single_network_message_logfile.txt',
    'start': '2012-12-11 03:07:02,237',
    'end': '2012-12-11 03:07:02,237',
    'total_messages': 1
}

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
    'start': '2012-12-11 03:02:01,760',
    'end': '2012-12-11 03:07:02,238',
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

    snapshots = []
    snapshot_data = []

    # Setup functions
    @classmethod
    def setUpClass(cls):
        cls.snapshot_data = [large_snapshot, small_snapshot, single_message_test,
                             no_messages_test, internal_messages_test]

        for snapshot in cls.snapshot_data:
            s = NetworkTrafficSnapshot()
            content = TestNetworkTrafficSnapshot._get_snapshot_content(snapshot['path'])
            s.upload(snapshot['title'], snapshot['desc'], snapshot['path'], content)
            cls.snapshots.append(s.get())

    @classmethod
    def _get_snapshot_content(cls, path):
        with open(path) as f:
            return f.read()

    def test_snapshot_data(self):
        test_data = ['title', 'desc', 'start', 'end', 'total_messages', 'method_created']

        for data, snapshot in zip(self.snapshot_data, self.snapshots):
            for field in test_data:
                if field in data:
                    message = 'Snapshot "' + snapshot['title'] + ' ' + field + ' not parsed correctly. Expected=' + str(data[field]) + ' Actual=' + str(snapshot[field])
                    self.assertEqual(snapshot[field], data[field], message)

    def test_total_messages(self):
        for index, snapshot in enumerate(self.snapshots):
            message = 'Snapshot ' + str(index) + ' total messages is incorrect'
            self.assertEqual(len(snapshot['messages']), snapshot['total_messages'], message)

    def test_snapshot_messages(self):
        header_fields = ['protocol', 'status_code', 'content', 'method',
                         'version', 'sender', 'receiver', 'destination_port', 'source_port']

        for data, snapshot in zip(self.snapshot_data, self.snapshots):
            if 'messages' in data:
                for message in data['messages']:
                    actual_message = snapshot['messages'][message['index']]

                    # Test that each of the fields specified match
                    for field in header_fields:
                        if field in message:
                            self.assertEqual(message[field], actual_message[field])

if __name__ == '__main__':
    unittest.main()
