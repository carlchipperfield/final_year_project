import unittest
import sys

sys.path.append('/app/share/python/site-packages')
from ni.network_traffic.messages import Message, SipMessage

messages = {}

messages['request'] = '''2012-12-11T03:06:53+00:00 cisco tvcs: UTCTime="2012-12-11 03:06:53,142" Module="network.sip" Level="DEBUG":  Src-ip="90.214.3.75"  Src-port="64981"
 SIPMSG:
 |INFO sip:phonebook@fyp.com SIP/2.0
 Via: SIP/2.0/TLS 192.168.0.3:64981;branch=z9hG4bK0003fbbdac0fc4c86b696342d60acff9.1;received=90.214.3.75;rport=64981
 Call-ID: 546f4050ff00d58b@192.168.0.3
 CSeq: 103 INFO
 Contact: <sip:laura.michael.movi@fyp.com;gr=urn:uuid:fa086037-f36b-57f1-b190-e1ebcddbb2c8>
 From: <sip:laura.michael.movi@fyp.com>;tag=bd417b01657b6303
 To: <sip:phonebook@fyp.com>
 Max-Forwards: 70
 Route: <sip:192.133.244.16:5061;lr>
 User-Agent: TANDBERG/772 (MCX 4.3.12.13351) - Mac OS X
 Expires: 10
 Proxy-Authorization: Digest nonce="ae17894c5a628ec830bf2eb3f69daebe865afc7a1c78bc6873a3d7a7628f", realm="cchipperfyp.fyp.com", qop=auth, opaque="AQAAAPg+o8sLn+lv40sM7jo2S3G3Gztv", username="laura.michael", uri="sip:fyp.com", response="6419914da48bcfdd9092c1e7bd7a5e42", algorithm=MD5, nc=00000009, cnonce="d6d3beb9c6ff4f3e3bff1800c463bfd9"
 Content-Type: application/tandberg-phonebook+xml
 Content-Length: 261

 <?xml version="1.0" encoding="UTF-8"?>
 <SearchParameters>
   <searchString>te</searchString>
   <returnFields>DisplayName,ContactMethodGroups</returnFields>
   <groupId></groupId>
   <maxResultSize>10</maxResultSize>
   <offset>10</offset>
 </SearchParameters>
|'''

request_content = '''<?xml version="1.0" encoding="UTF-8"?>
 <SearchParameters>
   <searchString>te</searchString>
   <returnFields>DisplayName,ContactMethodGroups</returnFields>
   <groupId></groupId>
   <maxResultSize>10</maxResultSize>
   <offset>10</offset>
 </SearchParameters>
'''

messages['response'] = '''2012-12-11T03:07:02+00:00 cisco tvcs: UTCTime="2012-12-11 03:07:02,238" Module="network.sip" Level="DEBUG":  Dst-ip="127.0.0.1"  Dst-port="25000"
 SIPMSG:
 |SIP/2.0 200 OK
 Via: SIP/2.0/TCP 127.0.0.1:5060;egress-zone=DefaultZone;branch=z9hG4bKeddc39fddb653eb2e21e8dff57384faa153.8de24b12c2931257c0e410e17bd936b9;proxy-call-id=d5bb0634-433f-11e2-aa82-005056ab3dbd;received=127.0.0.1;rport=25000
 Via: SIP/2.0/TLS 192.168.0.3:64981;branch=z9hG4bK1362adc2b49b82b052c4931786fefc95.1;received=90.214.3.75;rport=64981;ingress-zone=DefaultSubZone
 Call-ID: 5a8615fc0ccb32eb@192.168.0.3
 CSeq: 206 PUBLISH
 From: <sip:laura.michael.movi@fyp.com>;tag=2ec3d9a8c06e5acc
 To: <sip:laura.michael.movi@fyp.com>;tag=f899b911a87c1104
 Server: TANDBERG/4120 (X7.2.1)
 Expires: 1314
 SIP-ETag: e8b432b8-433c-11e2-83c1-005056ab3dbd
 Content-Length: 0
|'''

messages['outgoing'] = '''2013-03-26T15:36:53+00:00 rusc01-et-vcs200 tvcs: UTCTime="2013-03-26 15:36:53,887" Module="network.sip" Level="DEBUG":  Dst-ip="10.50.152.101"  Dst-port="7001" 
 SIPMSG:
 |OPTIONS sip:10.50.152.101:7001;transport=tls SIP/2.0
 Via: SIP/2.0/TLS 10.47.156.200:5061;branch=z9hG4bK9f38956954c0b183bbd0110fb1caf90d508450;rport
 Call-ID: 59bd3cd31e1ea4bc@10.47.156.200
 CSeq: 63330 OPTIONS
 From: <sip:10.47.156.200>;tag=bb8a8bf92cb51c01
 To: <sip:10.50.152.101:7001>
 Max-Forwards: 0
 User-Agent: TANDBERG/4120 (X7.2.1)
 Authorization: Digest nonce="087ae51c868ffb28ce27b65c26d0dfb9076fc2f374faf64b955f99df7223", realm="traversal (cluster 1)", opaque="AQAAAAk3jDeOuiQAO4Ax9stMJ/EsHBGu", algorithm=MD5, uri="sip:10.50.152.101:7001;transport=tls", username="traversal", response="3a58702491b6a24029c69a5781c45438", qop=auth, cnonce="f32713e8e34f8b80522e596d392d9c0277c0bf4002d5197d6f8faa4ecac3", nc=00000001
 Supported: com.tandberg.vcs.resourceusage
 Content-Type: text/xml
 Content-Length: 250
 
 <resourceusageinfo><traversalcallsavailable>249</traversalcallsavailable><nontraversalcallsavailable>750</nontraversalcallsavailable><registrationsavailable>2494</registrationsavailable><turnrelaysavailable>0</turnrelaysavailable></resourceusageinfo>|
'''

messages['diff_content'] = '''2012-12-11T03:07:02+00:00 cisco tvcs: UTCTime="2012-12-11 03:07:02,238" Module="network.sip" Level="DEBUG":  Dst-ip="127.0.0.1"  Dst-port="25000"
 SIPMSG:
 |SIP/2.0 200 OK
 Via: SIP/2.0/TLS 192.168.0.3:64981;branch=z9hG4bK1362adc2b49b82b052c4931786fefc95.1;received=90.214.3.75;rport=64981;ingress-zone=DefaultSubZone
 Call-ID: 5a8615fc0ccb32eb@192.168.0.3
 CSeq: 206 PUBLISH
 From: <sip:laura.michael.movi@fyp.com>;tag=2ec3d9a8c06e5acc
 To: <sip:laura.michael.movi@fyp.com>;tag=f899b911a87c1104
 Server: TANDBERG/4120 (X7.2.1)
 Expires: 1314
 SIP-ETag: e8b432b8-433c-11e2-83c1-005056ab3dbd
 Content-Length: 37

 Test a message with different content
|'''

messages['diff_dest'] = '''2012-12-11T03:07:02+00:00 cisco tvcs: UTCTime="2012-12-11 03:07:02,238" Module="network.sip" Level="DEBUG":  Src-ip="1.2.3.4" Src-port="25000"
 SIPMSG:
 |SIP/2.0 200 OK
 Via: SIP/2.0/TLS 192.168.0.3:64981;branch=z9hG4bK1362adc2b49b82b052c4931786fefc95.1;received=90.214.3.75;rport=64981;ingress-zone=DefaultSubZone
 Call-ID: 5a8615fc0ccb32eb@192.168.0.3
 CSeq: 206 PUBLISH
 From: <sip:laura.michael.movi@fyp.com>;tag=2ec3d9a8c06e5acc
 To: <sip:laura.michael.movi@fyp.com>;tag=f899b911a87c1104
 Server: TANDBERG/4120 (X7.2.1)
 Expires: 1314
 SIP-ETag: e8b432b8-433c-11e2-83c1-005056ab3dbd
 Content-Length: 0
|'''

not_message_log = '''2013-03-26T15:36:52+00:00 rusc01-et-vcs200 tvcs: UTCTime="2013-03-26 15:36:52,612"
Module="developer.iwf" Level="DEBUG" CodeLocation="ppcmains/oak/calls/iwf/IIWFTarget.cpp(470)" Method="IIWFTarget::runTargetLeg"
Thread="0x7fcb6ab53700":  State="IWFAwaitingConnectSipOutLegState" Global-CallId="fb5b6b02-962a-11e2-be85-000c298fb0c1" Local-CallId="fb5b6922-962a-11e2-896d-000c298fb0c1"
'''


class TestCreateMessage(unittest.TestCase):
    '''
        Test that the create_message function works as expected.
        The aim is to take in a log entry and return the correct object.

        Currently only SIP messages are supported.
        Add more tests when new protocols are supported.
    '''
    def test_create_sip_message(self):
        self._test_create_message(type(SipMessage()), messages['response'])

    def test_create_not_message(self):
        self._test_create_message(type(None), not_message_log)

    def _test_create_message(self, expected_type, log_entry):
        message_object = Message.create_message(log_entry)
        self.assertIs(type(message_object), expected_type)


parsed_messages = {}


class TestMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        '''
            Creates the Message object for use throughout all the
            tests.
        '''
        for key, value in messages.items():
            # Create a new message for each message
            message = SipMessage()
            message.parse(value)
            parsed_messages[key] = message

    def test_utc(self):
        test_message_field(self, 'request', 'utc', '2012-12-11T03:06:53.142000')
        test_message_field(self, 'response', 'utc', '2012-12-11T03:07:02.238000')
        test_message_field(self, 'outgoing', 'utc', '2013-03-26T15:36:53.887000')

    def test_source(self):
        test_message_field(self, 'request', 'source', '90.214.3.75')
        test_message_field(self, 'response', 'source', '127.0.0.1')
        test_message_field(self, 'outgoing', 'source', '127.0.0.1')

    def test_destination(self):
        test_message_field(self, 'request', 'destination', '127.0.0.1')
        test_message_field(self, 'response', 'destination', '127.0.0.1')
        test_message_field(self, 'outgoing', 'destination', '10.50.152.101')

    def test_source_port(self):
        test_message_field(self, 'request', 'source_port', '64981')
        test_message_field(self, 'response', 'source_port', '')
        test_message_field(self, 'outgoing', 'source_port', '')

    def test_destination_port(self):
        test_message_field(self, 'request', 'destination_port', '')
        test_message_field(self, 'response', 'destination_port', '25000')
        test_message_field(self, 'outgoing', 'destination_port', '7001')

    def test_duplicate_message(self):
        test_duplicate_message(self, 'diff_content', 'response', False)
        test_duplicate_message(self, 'diff_dest', 'response', False)
        test_duplicate_message(self, 'response', 'response')


class TestSipMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for key, value in messages.items():
            # Create a new message for each message
            message = SipMessage()
            message.parse(value)
            parsed_messages[key] = message

    def test_protocol(self):
        test_message_field(self, 'request', 'protocol', 'SIP')
        test_message_field(self, 'response', 'protocol', 'SIP')

    def test_version(self):
        test_message_field(self, 'request', 'version', '2.0')
        test_message_field(self, 'response', 'version', '2.0')

    def test_method(self):
        test_message_field(self, 'request', 'method', 'INFO')
        test_message_field(self, 'response', 'method', 'PUBLISH')

    def test_status(self):
        test_message_field(self, 'request', 'status', 'None')
        test_message_field(self, 'response', 'status', '200 OK')

    def test_content(self):
        test_message_field(self, 'request', 'content', request_content)
        test_message_field(self, 'response', 'content', 'None')

    def test_total_headers(self):
        num_headers = len(parsed_messages['response'].data['headers'])
        self.assertEqual(num_headers, 10)

        num_headers = len(parsed_messages['request'].data['headers'])
        self.assertEqual(num_headers, 13)


# TEST HELPER FUNCTIONS
def test_message_field(test, message_name, field, expected_value):
    actual_value = parsed_messages[message_name].data[field]

    fail_response = 'SIP ' + message_name + ' ' + field + ' not parsed correctly. '
    fail_response += '\nExpected:\n' + repr(expected_value) + '\nActual:\n' + repr(actual_value)

    test.assertEqual(actual_value, expected_value, fail_response)


def test_header_length(test, message_name, header, expected_length):
    actual_length = len(header)
    fail_response = message_name + ' message header field\'s length is incorrect. Expected: ' + str(actual_length) + ' Actual: ' + str(expected_length)
    test.assertEqual(expected_length, actual_length, fail_response)


def test_duplicate_message(test, sent_message_name, received_message_name, expected=True):
    sent_message = parsed_messages[sent_message_name]
    received_message = parsed_messages[received_message_name]
    is_same = Message.is_same_message(sent_message, received_message)

    fail_response = "Message function is_same_message returned " + str(is_same) + ' instead of ' + str(expected) + ' when sent message is ' + repr(sent_message_name) + ' and received message is ' + repr(received_message_name)
    test.assertEqual(is_same, expected, fail_response)


if __name__ == '__main__':
    unittest.main()
