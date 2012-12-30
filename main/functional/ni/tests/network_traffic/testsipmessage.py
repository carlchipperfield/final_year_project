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

messages['diff_header_values'] = '''2012-12-11T03:07:02+00:00 cisco tvcs: UTCTime="2012-12-11 03:07:02,238" Module="network.sip" Level="DEBUG":  Dst-ip="127.0.0.1"  Dst-port="25000"
 SIPMSG:
 |SIP/2.0 200 OK
 Via: SIP/2.0/TCP 127.0.0.1:5060;egress-zone=DefaultZone;branch=z9hG4bKeddc39fddb653eb2e21e8dff57384faa153.8de24b12c2931257c0e410e17bd936b9;proxy-call-id=d5bb0634-433f-11e2-aa82-005056ab3dbd;received=127.0.0.1;rport=25000
 Call-ID: 5a8615fc0ccb32eb@192.168.0.3
 CSeq: 206 PUBLISH
 From: <sip:laura.michael.movi@fyp.com>;tag=2ec3d9a8c06e5acc
 To: <sip:laura.michael.movi@fyp.com>;tag=f899b911a87c1104
 Server: TANDBERG/4120 (X7.2.1)
 Expires: 1314
 SIP-ETag: e8b432b8-433c-11e2-83c1-005056ab3dbd
 Content-Length: 0
|'''

messages['diff_header_keys'] = '''2012-12-11T03:07:02+00:00 cisco tvcs: UTCTime="2012-12-11 03:07:02,238" Module="network.sip" Level="DEBUG":  Dst-ip="127.0.0.1"  Dst-port="25000"
 SIPMSG:
 |SIP/2.0 200 OK
 Via: SIP/2.0/TCP 127.0.0.1:5060;egress-zone=DefaultZone;branch=z9hG4bKeddc39fddb653eb2e21e8dff57384faa153.8de24b12c2931257c0e410e17bd936b9;proxy-call-id=d5bb0634-433f-11e2-aa82-005056ab3dbd;received=127.0.0.1;rport=25000
 Via: SIP/2.0/TLS 192.168.0.3:64981;branch=z9hG4bK1362adc2b49b82b052c4931786fefc95.1;received=90.214.3.75;rport=64981;ingress-zone=DefaultSubZone
 Call-ID: 5a8615fc0ccb32eb@192.168.0.3
 CSeq: 206 PUBLISH
 From: <sip:laura.michael.movi@fyp.com>;tag=2ec3d9a8c06e5acc
 To: <sip:laura.michael.movi@fyp.com>;tag=f899b911a87c1104
 Server: TANDBERG/4120 (X7.2.1)
 SIP-ETag: e8b432b8-433c-11e2-83c1-005056ab3dbd
 Content-Length: 0
|'''

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

messages['diff_dest'] = '''2012-12-11T03:07:02+00:00 cisco tvcs: UTCTime="2012-12-11 03:07:02,238" Module="network.sip" Level="DEBUG":  Src-ip="1.2.3.4"3 Src-port="25000"
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


class TestSipMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parsed_messages = {}

        for key, value in messages.items():
            message = SipMessage()
            message.parse(value)
            cls.parsed_messages[key] = message.get()

    def test_content(self):
        self._test_message_field('request', 'content', request_content)
        self._test_message_field('response', 'content', 'None')

    def test_utc(self):
        self._test_message_field('request', 'utc', '2012-12-11 03:06:53,142')
        self._test_message_field('response', 'utc', '2012-12-11 03:07:02,238')

    def test_sender_and_receiver(self):
        self._test_message_field('request', 'destination', 'cisco tvcs')
        self._test_message_field('request', 'source', '90.214.3.75')
        self._test_message_field('request', 'source_port', '64981')
        self._test_message_field('request', 'destination_port', '')

        self._test_message_field('response', 'destination', 'cisco tvcs')
        self._test_message_field('response', 'source', 'cisco tvcs')
        self._test_message_field('response', 'source_port', '')
        self._test_message_field('response', 'destination_port', '25000')

    def test_method(self):
        self._test_message_field('request', 'method', 'INFO')
        self._test_message_field('response', 'method', 'PUBLISH')

    def test_protocol(self):
        self._test_message_field('request', 'protocol', 'SIP')
        self._test_message_field('response', 'protocol', 'SIP')

    def test_version(self):
        self._test_message_field('request', 'version', '2.0')
        self._test_message_field('response', 'version', '2.0')

    def test_status_code(self):
        self._test_message_field('request', 'status_code', '')
        self._test_message_field('response', 'status_code', '200 OK')

    def test_total_headers(self):
        num_headers = len(self.parsed_messages['response']['headers'])
        self.assertEqual(num_headers, 9)

        num_headers = len(self.parsed_messages['request']['headers'])
        self.assertEqual(num_headers, 13)

    def test_header_fields(self):
        # Test headers with single entry
        self._test_header_field('request', 'To', ['<sip:phonebook@fyp.com>'])
        self._test_header_field('response', 'SIP-ETag', ['e8b432b8-433c-11e2-83c1-005056ab3dbd'])

        # Now test a header field with multiple entries
        values = [
            'SIP/2.0/TCP 127.0.0.1:5060;egress-zone=DefaultZone;branch=z9hG4bKeddc39fddb653eb2e21e8dff57384faa153.8de24b12c2931257c0e410e17bd936b9;proxy-call-id=d5bb0634-433f-11e2-aa82-005056ab3dbd;received=127.0.0.1;rport=25000',
            'SIP/2.0/TLS 192.168.0.3:64981;branch=z9hG4bK1362adc2b49b82b052c4931786fefc95.1;received=90.214.3.75;rport=64981;ingress-zone=DefaultSubZone'
        ]
        self._test_header_field('response', 'Via', values)

    def test_duplicate_message(self):
        self._test_duplicate_message('diff_header_keys', 'response', False)
        self._test_duplicate_message('diff_header_values', 'response', False)
        self._test_duplicate_message('diff_content', 'response', False)
        self._test_duplicate_message('diff_dest', 'response', False)
        self._test_duplicate_message('response', 'response')

    # TEST HELPER FUNCTIONS
    def _test_message_field(self, message_name, field, expected_value):
        actual_value = self.parsed_messages[message_name][field]

        fail_response = 'SIP ' + message_name + ' ' + field + ' not parsed correctly. '
        fail_response += '\nExpected:\n' + repr(expected_value) + '\nActual:\n' + repr(actual_value)

        self.assertEqual(actual_value, expected_value, fail_response)

    def _test_header_field(self, message_name, header_field, expected_values):
        header = self.parsed_messages[message_name]['headers'][header_field]

        # Check the length of the header field
        self._test_header_length(message_name, header, len(expected_values))

        # Check that the header values match as expected
        for index, expected_value in enumerate(expected_values):
            actual_value = header[index]
            fail_response = message_name + ' ' + header_field + ' header not parsed as expected. '
            fail_response += 'Expected: ' + expected_value + ' Actual: ' + actual_value
            self.assertEqual(actual_value, expected_value, fail_response)

    def _test_header_length(self, message_name, header, expected_length):
        actual_length = len(header)
        fail_response = message_name + ' message header field\'s length is incorrect. Expected: ' + str(actual_length) + ' Actual: ' + str(expected_length)
        self.assertEqual(expected_length, actual_length, fail_response)

    def _test_duplicate_message(self, sent_message_name, received_message_name, expected=True):
        sent_message = self.parsed_messages[sent_message_name]
        received_message = self.parsed_messages[received_message_name]
        is_same = Message.is_same_message(sent_message, received_message)

        fail_response = "Message function is_same_message returned " + str(is_same) + ' instead of ' + str(expected) + ' when sent message is ' + repr(sent_message_name) + ' and received message is ' + repr(received_message_name)
        self.assertEqual(is_same, expected, fail_response)


if __name__ == '__main__':
    unittest.main()
