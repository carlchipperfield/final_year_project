import re
import sys
from datetime import datetime
sys.path.append('/app/share/python/site-packages/')

from pymongo import MongoClient
from messages import Message


class NetworkTrafficSnapshot:

    def __init__(self):
        connection = MongoClient()
        db = connection.diagnostics
        self.snapshots = db.snapshots

        self.data = {
            'messages': []
        }
        self.internal_messages = []

    def save(self):
        self.snapshots.insert(self.data)

    def get(self):
        return self.data

    def upload(self, title, desc, logfile, content):
        self.data['creation_method'] = "upload"
        self.data['creation_logfile'] = logfile
        self.data['creation_time'] = self._get_current_time()
        self.data['title'] = title
        self.data['desc'] = desc
        self._process_logfile_messages(content)
        self.data['total_messages'] = len(self.data['messages'])
        self.data['start'] = self._parse_start()
        self.data['end'] = self._parse_end()

    def _get_current_time(self):
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%d %H:%M:%S,%f')

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
                # not always case at beginning and end of logfile) TEST THIS CASE
                if message.is_sent_message():
                    self.data['messages'].append(message.get())
                    index = len(self.data['messages']) - 1
                    message = message.get()
                    message['source_port'] = 'Not Found'
                    self.internal_messages.append({'index': index, 'message': message})

                # If an received message, try find sent message in list and merge extra info
                # If sent message not found update the message to say not found and append to list TEST THIS CASE
                elif message.is_received_message():
                    for index, sent_message in enumerate(self.internal_messages):
                        if Message.is_same_message(sent_message['message'], message.get()):
                            merged_message = Message.merge(sent_message['message'], message.get())
                            self.data['messages'][sent_message['index']] = merged_message
                            self.internal_messages.pop(index)
                            break
                    else:
                        message.data['destination_port'] = 'Not Found'
                        self.data['messages'].append(message.get())
                        entry = {'index': len(self.data['messages']) - 1, 'message': message.get()}
                        self.internal_messages.append(entry)
            else:
                self.data['messages'].append(message.get())

    def _parse_start(self):
        if len(self.data['messages']) > 0:
            first_message = self.data['messages'][0]
            return first_message['utc']
        return ''

    def _parse_end(self):
        if len(self.data['messages']) > 0:
            index_of_last = len(self.data['messages']) - 1
            last_message = self.data['messages'][index_of_last]
            return last_message['utc']
        return ''
