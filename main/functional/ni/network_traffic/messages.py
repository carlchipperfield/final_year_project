import json
import re
import sys
from pymongo import MongoClient
from datetime import datetime

sys.stdout = sys.stderr


class Message(object):

    def __init__(self):
        self.data = {}

    def get(self):
        return self.data

    def get_json(self):
        return json.dumps(self.data)

    @staticmethod
    def get_message_ids(messages):
        ids = []
        for message in messages:
            ids.append(str(message.get()['_id']))
        return ids

    def get_id(self):
        return str(self.data['_id'])

    def load(self, data):
        self.data = data

    def save(self, snapshot_id):

        connection = MongoClient()
        db = connection.diagnostics
        self.networkmessages = db.networkmessages

        # Relate message to the snapshot and save to the database
        self.data['snapshot_id'] = str(snapshot_id)
        self.networkmessages.insert(self.data)

        connection.close()

    @staticmethod
    def create_message(log_entry):
        message = None

        # Compare future supported protocols here
        if log_entry.find("SIPMSG:") != -1:
            message = SipMessage()

        if message:  # Parse the message if it is a supported protocol
            message.parse(log_entry)

        return message

    def is_internal_message(self):
        return self.data['destination'] == self.data['source']

    def is_sent_message(self):
        return self.data['destination_port'] != ''

    def is_received_message(self):
        return self.data['source_port'] != ''

    @staticmethod
    def is_same_message(sent_message, received_message):
        compare_fields = ['content', 'source', 'destination', 'status', 'method']
        # Check if the fields of both message are the same, based on the compare fields
        for comparison in compare_fields:
            if sent_message.data[comparison] != received_message.data[comparison]:
                return False
        return True

    @staticmethod
    def merge(sent_message, received_message):
        '''
            Merge the important info of each message
            Start with received_message and merge over sent_message fields
        '''
        message = received_message
        for field in ['index', 'destination_port']:
            message.data[field] = sent_message.data[field]
        return message

    def parse(self, log_entry):
        self._parse_message_info(log_entry)
        self._parse_headers(log_entry)
        self._parse_content(log_entry)
        self.extract_useful_header_data()

    def _parse_message_info(self, log_entry):
        self.data['utc'] = self._parse_utc(log_entry)
        self.data['source'], self.data['destination'] = self._parse_sender_and_receiver(log_entry)

        # Try to extract source and dest ports
        try:
            port_type, port = self._parse_port(log_entry)
        except InvalidMessageFormatError:
            pass  # Log error
        else:
            if port_type == "destination":
                self.data['destination_port'] = port
                self.data['source_port'] = ''
            else:
                self.data['source_port'] = port
                self.data['destination_port'] = ''

        # Determine the type of message
        if self.is_internal_message():
            self.data['type'] = 'internal'
        else:
            self.data['type'] = 'external'

    def _parse_message_headers(self, log_entry):
        pass  # Implemented by specific protocol message

    def _parse_message_content(self, log_entry):
        pass  # Implemented by specific protocol message

    def extract_useful_header_data(self):
        pass  # Implemented by specific protocol message

    def _parse_utc(self, log_entry):
        utc_log = re.search('UTCTime="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}', log_entry)  # 2012-12-11 03:07:18,457
        if utc_log:
            date = utc_log.group(0)
            year = int(date[9:13])
            month = int(date[14:16])
            day = int(date[17:19])
            hour = int(date[20:22])
            min = int(date[23:25])
            sec = int(date[26:28])
            msec = int(date[29:32]) * 1000
            return datetime(year, month, day, hour, min, sec, msec).isoformat()

    def _parse_sender_and_receiver(self, log_entry):
        '''
            2012-12-11T03:06:30+00:00 cisco tvcs: UTCTime="2012-12-11 03:06:30,594"
            Module="network.sip" Level="DEBUG":  Src-ip="90.214.3.75"  Src-port="64979"

            2012-12-11T03:06:54+00:00 cisco tvcs: UTCTime="2012-12-11 03:06:54,548"
            Module="network.sip" Level="DEBUG":  Dst-ip="90.214.3.75"  Dst-port="64981"
        '''
        # Get the component that is logging the message
        log_start = log_entry.split(': ', 1)
        component = log_start[0].strip().split(' ', 1)
        component = component[1]

        # Set the destination and source data
        dest_ip = re.search('Dst-ip="[^"]*', log_entry)
        if dest_ip:
            destination = dest_ip.group(0).strip('Dst-ip="')
            source = '127.0.0.1'
        else:
            src_ip = re.search('Src-ip="[^"]*', log_entry)
            if src_ip:
                source = src_ip.group(0).strip('Src-ip="')
                destination = '127.0.0.1'
            else:
                source = ''
                destination = ''

        return source, destination

    def _parse_port(self, log_entry):
        # Try to extract the destination port
        dest_ip = re.search('Dst-port="[0-9]*', log_entry)
        if dest_ip:
            return "destination", dest_ip.group(0).strip('Dst-port="')
        else:
            # Now attempt to extract the source port
            src_ip = re.search('Src-port="[0-9]*', log_entry)
            if src_ip:
                return "source", src_ip.group(0).strip('Src-port="')
            else:
                raise InvalidMessageFormatError('SIP', log_entry, "Unable to find destination or source port")


class SipMessage(Message):

    methods = ['INVITE', 'ACK', 'BYE', 'CANCEL', 'OPTIONS',
                'REGISTER', 'PRACK', 'SUBSCRIBE', 'NOTIFY', 'PUBLISH',
                'INFO', 'REFER', 'MESSAGE', 'UPDATE']

    def _parse_message_info(self, log_entry):
        # Extract the common info
        super(SipMessage, self)._parse_message_info(log_entry)

        # Extract SIP specific info
        self.data['protocol'] = 'SIP'
        self.data['version'] = self._parse_version(log_entry)
        self.data['method'] = self._parse_method(log_entry)
        self.data['status'] = self._parse_status(log_entry)

    def _parse_headers(self, log_entry):
        self.data['headers'] = []

        # Log entries identified by colon separator
        headers = re.findall('\n.*: .*', log_entry)

        if headers:
            for header in headers:
                field = header.split(":", 1)
                name = field[0].strip()
                value = field[1].strip()
                self.data['headers'].append({'name': name, 'value': value})

    def _parse_content(self, log_entry):
        # Content always starts after the content length header
        if log_entry.find('Content-Length: 0') != -1:
            self.data['content'] = 'None'
        else:
            content_pos = re.search('Content-Length: [0-9]*', log_entry)
            if content_pos:
                content = log_entry[content_pos.end():].strip().strip('|')
                self.data['content'] = content

    def _parse_method(self, log_entry):
        # CSeq: 100 INVITE
        cseq = re.search('CSeq: .*\n', log_entry)
        if cseq:
            for method in self.methods:
                if cseq.group(0).find(method) != -1:
                    return method
        return 'None'

    def _parse_status(self, log_entry):
        # SIP/2.0 200 OK
        status = re.search('SIP.* [0-9]{3} [a-zA-Z]*', log_entry)
        if status:
            dd = re.search('[0-9]{3} [a-zA-Z]*', status.group(0))
            return dd.group(0)
        return 'None'

    def _parse_version(self, log_entry):
        # Find a status line e.g. SIP/2.0 200 OK
        status_line = re.search('SIP.* [0-9]{3} [a-zA-Z]*', log_entry)
        if status_line:
            return status_line.group(0).split(' ', 1)[0].strip('SIP/')
        else:
            # Find a request line e.g. INVITE sip:test@fyp.com SIP/2.0
            request_line = re.search('[A-Z]* .* SIP/.*', log_entry)
            if request_line:
                version = re.search('SIP/.*', request_line.group(0))
                return version.group(0).strip('SIP/')
            raise InvalidMessageFormatError('SIP', log_entry, "Unable to determine protocol version")

    def extract_useful_header_data(self):
        # Going to extract the call_id
        for header in self.data['headers']:
            if header['name'].lower() == 'call-id':
                self.data['call-id'] = header['value']

    def get_transaction_id(self):
        try:
            via = self.find_header('Via').pop()
            pattern = 'branch=z9hG4bK[a-zA-Z0-9\.]+;'
            return re.search(pattern, via).group(0)[7:-1]
        except AttributeError:
            return 'None'

    def get_call_id(self):
        return self.find_header('Call-ID')[0]

    def get_cseq(self):
        return self.find_header('CSeq')[0]

    def get_sender(self):
        return self.get_participant('From')

    def get_receiver(self):
        return self.get_participant('To')

    def get_participant(self, field):
        participant = self.find_header(field)[0]
        try:
            pattern = '<sip:.+>'
            return re.search(pattern, participant).group(0)[5:-1]
        except AttributeError:
            return 'Not available'

    def get_tags(self):
        return (self.get_local_tag(), self.get_remote_tag())

    def get_local_tag(self):
        return self.get_tag('To')

    def get_remote_tag(self):
        return self.get_tag('From')

    def get_tag(self, field):
        field = self.find_header(field)[0]
        try:
            return re.search('tag=[a-f0-9]*', field).group(0)[4:]
        except (AttributeError):
            return ''

    def find_header(self, header):
        ''' Extracts the header field from the message.
        There may be multiple instances of the same header field
        so return a list of headers found '''
        headers = []

        for entry in self.data['headers']:
            if entry['name'] == header:
                headers.append(entry['value'])

        if not headers:
            headers = ['Not available']

        return headers


class InvalidMessageFormatError(Exception):

    def __init__(self, protocol, log, reason):
        self.protocol = protocol
        self.log = log
        self.reason = reason
