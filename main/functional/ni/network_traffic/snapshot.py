import re
import sys
from datetime import datetime
sys.path.append('/app/share/python/site-packages/')

from pymongo import MongoClient
from messages import Message

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

            message.parse(log_entry)
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
                        if Message.is_same_message(sent_message['message'], message):
                            merged_message = Message.merge(sent_message['message'], message)
                            self.messages[sent_message['index']] = merged_message
                            self.internal_messages.pop(index)
                            break
                    else:
                        message.data['index'] = len(self.messages)
                        self.messages.append(message)
                        entry = {'index': len(self.messages) - 1, 'message': message}
                        self.internal_messages.append(entry)
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
                "call-ids": self.get_distinct_call_ids()
            }
        }

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
