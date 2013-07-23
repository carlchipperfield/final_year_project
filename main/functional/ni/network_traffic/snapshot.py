import re
import sys
from datetime import datetime
from sets import Set
sys.path.append('/app/share/python/site-packages/')

from pymongo import MongoClient
from bson.objectid import ObjectId
from messages import Message, SipMessage

sys.stdout = sys.stderr


class NetworkTrafficSnapshot:

    def __init__(self):
        connection = MongoClient()
        db = connection.diagnostics
        self.snapshots = db.snapshots
        self.networkmessages = db.networkmessages
        self.data = {}
        self.messages = []
        self.internal_messages = []

    def load(self, snapshot_id):

        query = {
            "snapshot_id": str(snapshot_id)
        }

        self.data = self.snapshots.find(query)
        self.networkmessages = self.networkmessages.find(query) # Will need to create object for each message?

    def save(self):
        # Save the snapshot and retrieve its assigned _id
        snapshot_id = self.snapshots.insert(self.data)

        # Save all of the network messages with ref to snapshot
        for message in self.messages:
            message.save(snapshot_id)

        # return the saved snapshot id
        self.id = snapshot_id
        return snapshot_id

    def upload(self, title, desc, logfile, content):
        self.data['title'] = title
        self.data['desc'] = desc
        self.data['creation_method'] = "upload"
        self.data['creation_logfile'] = logfile
        self.data['creation_time'] = self._get_current_time()
        self._process_logfile_messages(content)
        self.data['start'] = self._parse_start()
        self.data['end'] = self._parse_end()

    def _get_current_time(self):
        return datetime.now().isoformat()

    def _process_logfile_messages(self, content):
        # Identify each log entry and create a message
        log_entry = ""
        for line in content.splitlines():
            if re.match("\s*[0-9]{4}-[0-9]{2}-[0-9]{2}T", line):
                self._process_message(log_entry)
                log_entry = line + '\n'
            else:
                log_entry += line + '\n'
        self._process_message(log_entry)

    def _process_message(self, log_entry):
        message = Message.create_message(log_entry)
        if message:  # If a supported message is found

            if message.is_internal_message():

                # (internal messages should always be sent then received,
                # not always case at beginning and end of logfile)
                if message.is_sent_message():

                    message.data['index'] = len(self.messages)
                    self.messages.append(message)

                    index = len(self.messages) - 1
                    self.internal_messages.append({'index': index, 'message': message})

                # If an received message, try find sent message in list and merge extra info
                # If sent message not found update the message to say not found and append to list
                elif message.is_received_message():

                    for index, sent_message in enumerate(self.internal_messages):

                        # Handle the case when duplicate messages are logged
                        if Message.is_same_message(sent_message['message'], message):

                            merged_message = Message.merge(sent_message['message'], message)
                            self.messages[sent_message['index']] = merged_message
                            self.internal_messages.pop(index)
                            break

                    else:
                        # Externally received message
                        message.data['index'] = len(self.messages)
                        self.messages.append(message)

            else:
                message.data['index'] = len(self.messages)
                self.messages.append(message)

    def _parse_start(self):
        if len(self.messages) > 0:
            first_message = self.messages[0]
            return first_message.data['utc']
        return ''

    def _parse_end(self):
        if len(self.messages) > 0:
            index_of_last = len(self.messages) - 1
            last_message = self.messages[index_of_last]
            return last_message.data['utc']
        return ''

    def generate_statistics(self):
        test = {"_id": self.id}
        # Initialise statistics
        statistics = {
            "statistics": {
                "total_messages": self.get_total_messages(),
                "total_calls": self.get_total_calls(),
                "total_requests": self.get_total_requests(),
                "total_responses": self.get_total_responses(),
                "total_incoming": self.get_total_incoming(),
                "total_outgoing": self.get_total_outgoing(),
                "total_internal": self.get_total_internal(),
                "methods": self.get_methods_used(),
                "responses": self.get_status_distribution()
            },
            "summary": {
                "methods": self.get_distinct_methods(),
                "call-ids": self.get_distinct_call_ids(),
                "participants": self.get_distinct_participants()
            }
        }

        # Update the network traffic db document with statistics object
        self.snapshots.update(test, {"$set": statistics})

    def get_total_messages(self):
        query = {
            'snapshot_id': str(self.id)
        }
        return self.networkmessages.find(query).count()

    def get_total_requests(self):
        query = {
            'snapshot_id': str(self.id),
            'status': 'None'
        }
        return self.networkmessages.find(query).count()

    def get_total_responses(self):
        query = {
            'snapshot_id': str(self.id),
            'status': {'$ne': 'None'}
        }
        return self.networkmessages.find(query).count()

    def get_total_incoming(self):
        query = {
            'snapshot_id': str(self.id),
            'type': 'external',
            'destination': '127.0.0.1'
        }
        return self.networkmessages.find(query).count()

    def get_total_outgoing(self):
        query = {
            'snapshot_id': str(self.id),
            'type': 'external',
            'source': '127.0.0.1'
        }
        return self.networkmessages.find(query).count()

    def get_total_internal(self):
        query = {
            'snapshot_id': str(self.id),
            'type': 'internal'
        }
        return self.networkmessages.find(query).count()

    def get_methods_used(self):
        method_count = {}
        for message in self.messages:
            message = message.get()
            if message['status'] == 'None':
                if message['method'] in method_count:
                    method_count[message['method']] += 1
                else:
                    method_count[message['method']] = 1

        return method_count

    def get_status_distribution(self):
        # Create a count for the different types of status codes
        response_categories = ['provisional', 'successful', 'redirection',
                'bad_request', 'server_failure', 'global_failure']
        response_counts = [0, 0, 0, 0, 0, 0]

        for message in self.messages:
            msg = message.get()
            if msg['status'] != 'None':
                status = int(msg['status'][0])
                response_counts[status - 1] += 1

        return dict(zip(response_categories, response_counts))

    def get_total_calls(self):
        query = {
            'snapshot_id': str(self.id)
        }
        test = self.networkmessages.find(query).distinct('call-id')
        return len(test)

    def get_distinct_call_ids(self):
        query = {
            'snapshot_id': str(self.id)
        }
        return self.networkmessages.find(query).distinct('call-id')

    def get_distinct_methods(self):
        query = {
            'snapshot_id': str(self.id)
        }
        return self.networkmessages.find(query).distinct('method')

    def get_distinct_participants(self):
        participants = Set([])
        for message in self.messages:
            msg = message.get()
            participants.add(self.get_participant(msg, "To"))
            participants.add(self.get_participant(msg, "From"))
        return list(participants)

    def get_participant(self, message, field):
        participant = self.find_header(message, field)
        try:
            pattern = '<sip:.+>'
            return re.search(pattern, participant).group(0)[5:-1]
        except AttributeError:
            return 'Not available'

    def find_header(self, message, header):
        for entry in message['headers']:
            if entry['name'] == header:
                return entry['value']
        return 'Not found'


class SIPDialogs:

    dialogs = {}

    def __init__(self):
        connection = MongoClient()
        db = connection.diagnostics
        self.networkmessages = db.networkmessages
        self.siptransactions = db.siptransactions
        self.sipdialogs = db.sipdialogs

    def extract(self, snapshot_id):

        transactions = self.siptransactions.find({"snapshot_id": str(snapshot_id)})

        for transaction in transactions:
            key = transaction['call_id'] + transaction['local_tag'] + transaction['remote_tag']

            if key in self.dialogs.keys():
                # The dialog already exists, just add the message ids
                transaction['_id'] = str(transaction['_id'])
                self.dialogs[key]['transactions'].append(transaction)
            else:

                message = self.networkmessages.find({"_id": ObjectId(transaction['message_ids'][0])})
                sipmessage = SipMessage()
                sipmessage.load(message[0])

                # Parse the sender and receiver
                sender = sipmessage.get_sender()
                receiver = sipmessage.get_receiver()

                transaction['_id'] = str(transaction['_id'])

                # Need to create a new dialog
                self.dialogs[key] = {
                    'snapshot_id': str(snapshot_id),
                    'transactions': [transaction],
                    'sender':      sender,
                    'receiver':    receiver
                }

    def save(self):
        for sipdialog in self.dialogs.itervalues():
            self.sipdialogs.insert(sipdialog)

from operator import itemgetter


class SipTransactions:

    transactions = []

    def __init__(self):
        connection = MongoClient()
        self.db = connection.diagnostics

    def extract(self, snapshot_id):
        messages = self._get_network_messages(snapshot_id)
        grouped_messages = self._group_transaction_messages(messages)
        self._extract_transaction_info(snapshot_id, grouped_messages)

    def save(self):
        for transaction in self.transactions:
            self.db.siptransactions.insert(transaction)

    def _get_network_messages(self, snapshot_id):
        snapshot = NetworkTrafficSnapshot()
        snapshot.load(snapshot_id)

        return snapshot.networkmessages

    def _group_transaction_messages(self, messages):
        ''' Group together the SIP transactions. '''
        transactions = {}
        for message in sorted(messages, key=itemgetter('utc')):
            if message['protocol'] == 'SIP':
                sipmessage = SipMessage()
                sipmessage.load(message)
                key = sipmessage.get_transaction_id()
                if key in transactions.keys():
                    transactions[key].append(sipmessage)
                else:
                    transactions[key] = [sipmessage]
        return transactions

    def _extract_transaction_info(self, snapshot_id, grouped_messages):
        self.transactions = []
        for group in grouped_messages.itervalues():
            self.transactions.append({
                'snapshot_id':    str(snapshot_id),
                'transaction_id': group[0].get_transaction_id(),
                'request':        group[0].get()['method'],
                'status':         group[-1].get()['status'],
                'utc':            group[0].get()['utc'],
                'message_ids':    Message.get_message_ids(group),
                'call_id':        self._get_group_call_id(group),
                'local_tag':      self._get_group_local_tag(group),
                'remote_tag':     self._get_group_remote_tag(group)
            })

    def _get_group_call_id(self, messages):
        for message in messages:
            call_id = message.get_call_id()
            if call_id:
                return call_id

    def _get_group_local_tag(self, messages):
        for message in messages:
            local_tag = message.get_local_tag()
            if local_tag:
                return local_tag

    def _get_group_remote_tag(self, messages):
        for message in messages:
            remote_tag = message.get_remote_tag()
            if remote_tag:
                return remote_tag
