import json
import re
from pymongo import MongoClient


class Message(object):

    def __init__(self):
        connection = MongoClient()
        db = connection.diagnostics
        self.networkmessages = db.networkmessages

        self.data = {
            'protocol':         '',
            'version':          '',
            'utc':              '',
            'source':           '',
            'destination':         '',
            'source_port':      '',
            'destination_port': '',
            'status':      '',
            'headers':          [],
            'content':          ''
        }

    def get(self):
        return self.data

    def get_json(self):
        return json.dumps(self.data)

    def save(self, snapshot_id):
        self.data['snapshot_id'] = str(snapshot_id)
        self.networkmessages.insert(self.data)

    @staticmethod
    def create_message(log_entry):
        if log_entry.find("SIPMSG:") != -1:
            return SipMessage()
        else:
            return None

    def is_internal_message(self):
        return self.data['destination'] == self.data['source']

    def is_sent_message(self):
        return self.data['destination_port'] != ''

    def is_received_message(self):
        return self.data['source_port'] != ''

    @staticmethod
    def is_same_message(sent_message, received_message):
        if sent_message.data['content'] != received_message.data['content']:
            return False
        elif sent_message.data['source'] != received_message.data['source']:
            return False
        elif sent_message.data['destination'] != received_message.data['destination']:
            return False
        elif sent_message.data['status'] != received_message.data['status']:
            return False
        elif sent_message.data['method'] != received_message.data['method']:
            return False
        return True

    @staticmethod
    def merge(sent_message, received_message):
        '''
            Merge the destination port of the sent message to the received message.
            We do it this way, rather than merging the received to sent, as the
            received message may have some more info attached.
        '''
        message = received_message
        message.data['index'] = sent_message.data['index']
        message.data['destination_port'] = sent_message.data['destination_port']
        return message

    def parse(self, log_entry):
        self._parse_message_info(log_entry)
        self._parse_headers(log_entry)
        self._parse_content(log_entry)

    def _parse_message_info(self, log_entry):
        self.data['utc'] = self._parse_utc(log_entry)
        self.data['source'], self.data['destination'] = self._parse_sender_and_receiver(log_entry)

        try:
            port_type, port = self._parse_port(log_entry)
        except InvalidMessageFormatError:
            pass  # Log error
        else:
            if port_type == "destination":
                self.data['destination_port'] = port
            else:
                self.data['source_port'] = port

    def _parse_message_headers(self, log_entry):
        pass  # Implemented by specific messages

    def _parse_message_content(self, log_entry):
        pass  # Implemented by specific messages

    def _parse_utc(self, log_entry):
        utc_log = re.search('UTCTime="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}', log_entry)  # 2012-12-11 03:07:18,457
        if utc_log:
            return utc_log.group(0)[9:28]

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
        dest_ip = re.search('Dst-port="[0-9]*', log_entry)
        if dest_ip:
            return "destination", dest_ip.group(0).strip('Dst-port="')
        else:
            src_ip = re.search('Src-port="[0-9]*', log_entry)
            if src_ip:
                return "source", src_ip.group(0).strip('Src-port="')
            else:
                raise InvalidMessageFormatError('SIP', log_entry, "Unable to find destination or source port")


class SipMessage(Message):

    methods = ['INVITE', 'ACK', 'BYE', 'CANCEL', 'OPTIONS',
                'REGISTER', 'PRACK', 'SUBSCRIBE', 'NOTIFY', 'PUBLISH',
                'INFO', 'REFER', 'MESSAGE', 'UPDATE']

    def __init__(self):
        Message.__init__(self)

    def _parse_message_info(self, log_entry):
        super(SipMessage, self)._parse_message_info(log_entry)

        self.data['protocol'] = 'SIP'
        self.data['version'] = self._parse_version(log_entry)
        self.data['method'] = self._parse_method(log_entry)
        self.data['status'] = self._parse_status(log_entry)

    def _parse_headers(self, log_entry):
        headers = re.findall('\n.*: .*', log_entry)
        if headers:
            for header in headers:
                field = header.split(":", 1)
                name = field[0].strip()
                value = field[1].strip()
                self.data['headers'].append({'name': name, 'value': value})

    def _parse_content(self, log_entry):
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


class InvalidMessageFormatError(Exception):

    def __init__(self, protocol, log, reason):
        self.protocol = protocol
        self.log = log
        self.reason = reason
